# backend/modules/m_external_context.py
"""
External API Context Layer — Advisory Only
==========================================
Fetches live market/macro data from up to four external APIs to enrich the
final Nemotron synthesis with contextual framing.

ISOLATION GUARANTEES:
  - Zero imports from data/crm_db.py, data/canary_db.py, or data/vectordb.py
  - Makes no database connections and performs no writes of any kind
  - Every fetcher is fully wrapped in try/except; any failure returns
    {"available": False, "data": ""} — the pipeline is unaffected
  - Data is fetched live per-query and discarded after the response is sent
  - Output is always prefixed [EXTERNAL MARKET CONTEXT — ADVISORY ONLY] so
    the LLM never confuses it with internal CRM evidence

The routing function selects only the APIs relevant to the current question,
so a hiring question never triggers FRED or Yahoo Finance.
"""

import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional


# ── Intent Keyword Routing ────────────────────────────────────────────────────

_NEWS_KEYWORDS = {
    "expand", "expansion", "market", "industry", "competitor", "competition",
    "launch", "product", "acquisition", "merge", "trend", "news", "outlook",
    "sector", "region", "geography", "city", "branch", "open", "enter",
}

_SEARCH_KEYWORDS = {
    "competitor", "competition", "pricing", "price", "benchmark", "market share",
    "alternative", "compare", "industry standard", "salary", "wage", "hire",
    "talent", "recruit", "cost", "vendor", "supplier",
}

_MACRO_KEYWORDS = {
    "interest rate", "inflation", "gdp", "recession", "economy", "economic",
    "federal", "fed rate", "unemployment", "macro", "rate hike", "cpi", "ppi",
    "credit", "debt", "fiscal", "monetary", "supply chain",
}

_EQUITY_KEYWORDS = {
    "stock", "share", "equity", "valuation", "ipo", "public", "nasdaq", "nyse",
    "investor", "investment", "fund", "venture", "market cap", "pe ratio",
    "ticker", "sector etf",
}


def select_relevant_sources(intent: dict, question: str) -> list[str]:
    """
    Inspect intent goal + question text to select which external APIs to call.
    Returns a list of source names from: ["tavily", "serpapi", "fred", "yahoo"].
    """
    q_lower = question.lower()
    goal_lower = intent.get("goal", "").lower()
    combined = q_lower + " " + goal_lower

    sources = []
    if any(kw in combined for kw in _NEWS_KEYWORDS):
        sources.append("tavily")
    if any(kw in combined for kw in _SEARCH_KEYWORDS):
        sources.append("serpapi")
    if any(kw in combined for kw in _MACRO_KEYWORDS):
        sources.append("fred")
    if any(kw in combined for kw in _EQUITY_KEYWORDS):
        sources.append("yahoo")

    return sources


# ── Individual Fetchers ───────────────────────────────────────────────────────

def fetch_tavily_news(question: str) -> dict:
    """
    Calls Tavily Search API for recent news/articles relevant to the question.
    Returns {"source": "Tavily News", "data": str, "available": bool}.
    """
    api_key = os.getenv("TAVILY_API_KEY", "").strip()
    if not api_key:
        return {"source": "Tavily News", "data": "", "available": False}

    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=api_key)
        result = client.search(
            query=question,
            search_depth="basic",
            max_results=3,
            include_answer=True,
        )
        lines = []
        if result.get("answer"):
            lines.append(f"Summary: {result['answer']}")
        for r in result.get("results", [])[:3]:
            title = r.get("title", "")
            url = r.get("url", "")
            snippet = r.get("content", "")[:300]
            lines.append(f"• {title} — {snippet} [{url}]")
        data = "\n".join(lines) if lines else ""
        return {"source": "Tavily News", "data": data, "available": bool(data)}
    except Exception as e:
        return {"source": "Tavily News", "data": "", "available": False}


def fetch_serpapi_results(question: str) -> dict:
    """
    Calls SerpAPI (Google Search) for structured organic results.
    Returns {"source": "SerpAPI Search", "data": str, "available": bool}.
    """
    api_key = os.getenv("SERPAPI_API_KEY", "").strip()
    if not api_key:
        return {"source": "SerpAPI Search", "data": "", "available": False}

    try:
        from serpapi import GoogleSearch
        params = {
            "q": question,
            "num": 3,
            "api_key": api_key,
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        organic = results.get("organic_results", [])[:3]
        lines = []
        for r in organic:
            title = r.get("title", "")
            snippet = r.get("snippet", "")[:280]
            link = r.get("link", "")
            lines.append(f"• {title}: {snippet} [{link}]")
        data = "\n".join(lines) if lines else ""
        return {"source": "SerpAPI Search", "data": data, "available": bool(data)}
    except Exception as e:
        return {"source": "SerpAPI Search", "data": "", "available": False}


def fetch_fred_indicator(question: str) -> dict:
    """
    Fetches the most relevant FRED macro indicator for the question context.
    Selects series ID heuristically from question keywords.
    Returns {"source": "FRED Macro", "data": str, "available": bool}.
    """
    api_key = os.getenv("FRED_API_KEY", "").strip()
    if not api_key:
        return {"source": "FRED Macro", "data": "", "available": False}

    # Series heuristic: pick most relevant FRED series based on keywords
    q_lower = question.lower()
    series_map = [
        (["interest rate", "fed rate", "rate hike", "monetary"],      ("FEDFUNDS",  "Federal Funds Rate (%)")),
        (["inflation", "cpi", "price level", "consumer price"],       ("CPIAUCSL",  "CPI All Urban Consumers (Index)")),
        (["unemployment", "jobs", "labor", "labour"],                  ("UNRATE",    "Unemployment Rate (%)")),
        (["gdp", "economic growth", "output"],                         ("GDP",       "Gross Domestic Product ($B)")),
        (["recession", "economy", "macro", "economic"],                ("USREC",     "US Recession Indicator")),
        (["supply chain", "ppi", "producer price"],                    ("PPIACO",    "Producer Price Index")),
        (["credit", "lending", "loan"],                                ("DPCREDIT",  "Discount Window Loans")),
    ]

    chosen_id, chosen_label = "FEDFUNDS", "Federal Funds Rate (%)"
    for keywords, (series_id, label) in series_map:
        if any(kw in q_lower for kw in keywords):
            chosen_id, chosen_label = series_id, label
            break

    try:
        from fredapi import Fred
        fred = Fred(api_key=api_key)
        series = fred.get_series(chosen_id, limit=3)
        if series.empty:
            return {"source": "FRED Macro", "data": "", "available": False}

        latest_val = series.iloc[-1]
        latest_date = series.index[-1].strftime("%Y-%m-%d")
        prev_val = series.iloc[-2] if len(series) >= 2 else None

        change_str = ""
        if prev_val is not None:
            delta = latest_val - prev_val
            change_str = f" (change: {delta:+.2f} from prior reading)"

        data = (
            f"{chosen_label}: {latest_val:.2f} as of {latest_date}{change_str}. "
            f"Source: Federal Reserve Economic Data (FRED)."
        )
        return {"source": "FRED Macro", "data": data, "available": True}
    except Exception as e:
        return {"source": "FRED Macro", "data": "", "available": False}


def fetch_yahoo_finance(question: str) -> dict:
    """
    Fetches recent sector/stock context via yfinance (no API key required).
    Heuristically selects a relevant sector ETF ticker from the question.
    Returns {"source": "Yahoo Finance", "data": str, "available": bool}.
    """
    q_lower = question.lower()

    # Heuristic: map keywords to representative sector ETFs
    ticker_map = [
        (["technology", "tech", "software", "saas", "developer"],  "XLK"),
        (["healthcare", "health", "pharma", "medical", "hospital"], "XLV"),
        (["finance", "financial", "bank", "insurance"],             "XLF"),
        (["energy", "oil", "solar", "renewable"],                   "XLE"),
        (["retail", "consumer", "ecommerce"],                       "XLY"),
        (["real estate", "property", "reit"],                       "XLRE"),
        (["industrial", "manufacturing", "logistics"],              "XLI"),
        (["material", "commodity", "mining"],                       "XLB"),
    ]

    ticker = "SPY"  # Default: broad S&P 500
    for keywords, t in ticker_map:
        if any(kw in q_lower for kw in keywords):
            ticker = t
            break

    try:
        import yfinance as yf
        info = yf.Ticker(ticker)
        hist = info.history(period="5d")
        if hist.empty:
            return {"source": "Yahoo Finance", "data": "", "available": False}

        latest_close = hist["Close"].iloc[-1]
        prev_close = hist["Close"].iloc[-2] if len(hist) >= 2 else latest_close
        pct_change = ((latest_close - prev_close) / prev_close) * 100
        latest_date = hist.index[-1].strftime("%Y-%m-%d")

        fast_info = info.fast_info
        week52_high = getattr(fast_info, "year_high", None)
        week52_low = getattr(fast_info, "year_low", None)
        range_str = ""
        if week52_high and week52_low:
            range_str = f" 52-week range: ${week52_low:.2f}–${week52_high:.2f}."

        data = (
            f"{ticker} closed at ${latest_close:.2f} on {latest_date} "
            f"({pct_change:+.2f}% vs prior session).{range_str} "
            f"Source: Yahoo Finance via yfinance."
        )
        return {"source": "Yahoo Finance", "data": data, "available": True}
    except Exception as e:
        return {"source": "Yahoo Finance", "data": "", "available": False}


# ── Dispatcher ────────────────────────────────────────────────────────────────

_FETCHER_MAP = {
    "tavily":  fetch_tavily_news,
    "serpapi": fetch_serpapi_results,
    "fred":    fetch_fred_indicator,
    "yahoo":   fetch_yahoo_finance,
}


def build_external_context(intent: dict, question: str) -> str:
    """
    Public entry point. Called from the main reasoning pipeline.

    Selects relevant APIs, fetches concurrently (matching the ThreadPoolExecutor
    pattern used in m06_debate.py), assembles a tagged advisory block, and
    returns it as a plain string.

    Returns "" if no APIs are relevant or all fail — the pipeline is unaffected.

    ISOLATION: This function has no side effects. It touches no database,
    no vector store, and returns nothing that can influence the CRM-derived
    verdict, confidence score, or department stances.
    """
    sources_needed = select_relevant_sources(intent, question)
    if not sources_needed:
        return ""

    results = {}
    with ThreadPoolExecutor(max_workers=len(sources_needed)) as executor:
        future_map = {
            executor.submit(_FETCHER_MAP[src], question): src
            for src in sources_needed
            if src in _FETCHER_MAP
        }
        for future in as_completed(future_map):
            src = future_map[future]
            try:
                results[src] = future.result()
            except Exception:
                results[src] = {"source": src, "data": "", "available": False}

    # Assemble only available results
    sections = []
    for src in sources_needed:  # preserve deterministic order
        r = results.get(src, {})
        if r.get("available") and r.get("data"):
            sections.append(f"[{r['source']}]\n{r['data']}")

    if not sections:
        return ""

    block = (
        "[EXTERNAL MARKET CONTEXT — ADVISORY ONLY]\n"
        "The following data is sourced from external APIs. It provides market "
        "framing only and must not alter the verdict, confidence, or evidence "
        "score derived from internal CRM data.\n\n"
        + "\n\n".join(sections)
    )
    return block

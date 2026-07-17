# backend/modules/m06_debate.py
"""
Debate Module — runs 4 department personas in parallel via Groq.
Each persona now receives its own slice of real CRM data to reason from.
"""
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from data.crm_db import get_financial_summary, get_deal_pipeline, get_team_stats, get_customer_health


def _build_dept_context(persona_name: str) -> str:
    """Build a department-specific context string from live CRM data."""
    try:
        if persona_name == "Finance":
            fin = get_financial_summary()
            return (
                f"Current financials: Revenue this month ${fin.get('latest_revenue', 0):,.0f}, "
                f"Profit ${fin.get('latest_profit', 0):,.0f}, "
                f"Avg 6-month profit margin {fin.get('avg_profit_margin_pct', 0)}%, "
                f"Revenue is {fin.get('revenue_trend', 'stable')}."
            )
        elif persona_name == "Sales":
            pipeline = get_deal_pipeline()
            top_deals = pipeline.get("top_open_deals", [])[:3]
            top_str = ", ".join([f"{d['customer_name']} (${d['value']:,.0f}, {d['probability']}% prob)" 
                                  for d in top_deals])
            return (
                f"Active pipeline: ${pipeline.get('open_pipeline_value', 0):,.0f} across "
                f"{pipeline.get('open_deal_count', 0)} open deals. "
                f"Closed-Won this year: ${pipeline.get('closed_won_value', 0):,.0f}. "
                f"Top deals at stake: {top_str}."
            )
        elif persona_name == "HR":
            team = get_team_stats()
            dept_str = "; ".join([
                f"{d['department']}: {d['headcount']} staff, avg perf {round(d['avg_perf'], 1)}/5"
                for d in team.get("by_department", [])
            ])
            return (
                f"Total team: {team.get('total_headcount', 0)} employees, "
                f"annual payroll ${team.get('total_annual_payroll', 0):,.0f}. "
                f"By department — {dept_str}. "
                f"Low performers: {len(team.get('low_performers', []))} staff below 4.0 rating."
            )
        elif persona_name == "Operations":
            fin = get_financial_summary()
            team = get_team_stats()
            ops_dept = next((d for d in team.get("by_department", []) if d["department"] == "Operations"), {})
            health = get_customer_health()
            at_risk = [a["name"] for a in health.get("at_risk_accounts", [])[:3]]
            return (
                f"Current headcount: {fin.get('latest_headcount', 'N/A')}. "
                f"Operations team: {ops_dept.get('headcount', 0)} people, avg performance {round(ops_dept.get('avg_perf', 0), 1)}/5. "
                f"At-risk customer accounts to monitor: {', '.join(at_risk) if at_risk else 'None'}."
            )
    except Exception as e:
        return f"[CRM data unavailable: {e}]"
    return ""


def debate_persona(question: str, goal: str, history: str, persona: str, bias: str, client) -> dict:
    dept_context = _build_dept_context(persona)

    prompt = f"""You are the {persona} Director at a mid-size B2B software company.

Your department's perspective: {bias}

Your real department data right now:
{dept_context}

The company is considering: "{question}"
The strategic goal is: {goal}
Relevant company knowledge and past decisions: {history[:2000]}

Based ONLY on your department's perspective and the data above, give your stance: "Support", "Neutral", or "Against".
Provide exactly 2 specific, data-grounded reasons. Reference actual numbers from the context where relevant.
Return ONLY a JSON object with keys: "stance", "reasons" (list of 2 short strings, max 12 words each)."""

    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    clean_json = chat_completion.choices[0].message.content.strip()
    return json.loads(clean_json)


def run_debate(question: str, goal: str, past_memory: str, client) -> list:
    personas = [
        {
            "name": "Finance",
            "bias": "You prioritize cash flow and profitability. You are conservative and quantify every risk in dollar terms."
        },
        {
            "name": "Operations",
            "bias": "You obsess over operational capacity, logistics, and bottlenecks. You hate over-committing resources."
        },
        {
            "name": "Sales",
            "bias": "You are growth-focused. You believe pipeline and market opportunity must not be squandered."
        },
        {
            "name": "HR",
            "bias": "You focus on team capacity, talent gaps, and culture health. You hate unplanned rapid changes."
        }
    ]

    views = [None] * 4
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_map = {}
        for i, p in enumerate(personas):
            future = executor.submit(
                debate_persona, question, goal, past_memory, p["name"], p["bias"], client
            )
            future_map[future] = i

        for future in as_completed(future_map):
            idx = future_map[future]
            views[idx] = future.result()

    return views

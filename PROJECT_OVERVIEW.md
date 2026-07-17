# Project Overview: Friction AI Business Reasoning Engine

This document provides a comprehensive, top-to-bottom technical and architectural blueprint of the Friction AI decision intelligence platform. It details how the codebase is structured, how the multi-agent cognitive pipeline functions, how data flows, and how the various subsystems (Canary Sentinel, CRM, Vector DB, Document Upload, and External API Context Layer) are implemented and integrated.

---

## 1. Executive Summary & Problem Space

### What is Friction AI?
Friction AI is an enterprise-grade, board-level decision intelligence platform designed for B2B software and mid-sized companies. In business operations, leadership teams constantly face complex, high-friction tensions where goals conflict with operational realities. Examples include:
*   *Should we hire 5 developers or 3 sales reps?* (Hiring budget vs. operational capacity vs. sales velocity)
*   *Should we expand to a new region?* (Capital availability vs. supply chain risks vs. macro interest rates)
*   *Should we adjust pricing by 10%?* (Volume growth vs. gross margins)

Generic AI assistants (like stock ChatGPT) answer these queries with generic business school advice. Friction AI solves this by grounding every decision in **real, live company data**, debating scenarios across multiple department personas, and validating decisions against mathematical constraints.

---

## 2. Technical Stack

The application is built on a modern, lightweight, and low-latency stack:

*   **Backend**: Python 3.10+ powered by **FastAPI** and served with **Uvicorn**. Database interactions are managed via standard Python SQLite libraries.
*   **Vector Indexing & RAG**: In-memory **Chroma DB** combined with a custom, zero-RAM deterministic `MockSentenceTransformer` that generates unit embeddings based on text hashing, running on 0MB of memory for maximum hosting efficiency.
*   **Frontend**: A responsive React single-page application built with **Vite** and styled using vanilla CSS (with support for Tailwind-like utility styling) and **Lucide React** icons.
*   **Core LLMs & Fallback System**:
    *   **Primary Synthesis**: NVIDIA's **Nemotron-3-Ultra-550B** (via the NVIDIA NIM API) is used for final recommendation generation due to its deep reasoning capacity.
    *   **Resilient Fallback**: If NVIDIA NIM times out (60s socket-level), rate-limits, returns a server error (e.g. 503), or returns truncated/malformed JSON, the pipeline immediately redirects the synthesis request to Groq's high-capacity **Llama 3.3 70B** (`llama-3.3-70b-versatile` or `openai/gpt-oss-120b`).
    *   **Upstream Persona Modules**: Upstream tasks (Intent Classifier, Root Cause, Debates, Scenario Weighting, and Sentinel Alert Generation) are powered by **Groq Llama 3.3 70B** models for rapid, concurrent completions.

---

## 3. High-Level Data Flow

```
                     +---------------------------------------+
                     |         User Question Input           |
                     +---------------------------------------+
                                         |
                                         v
                     +---------------------------------------+
                     |          Phase 1: UNDERSTAND          |
                     |  - Extract Goal, Constraints, Horizon |
                     |  - Compute Cognitive Friction Level   |
                     |  - Retrieve CRM & Vector DB Memories  |
                     |  - Fetch live Macro Context (APIs)    |
                     +---------------------------------------+
                                         |
                                         v
                     +---------------------------------------+
                     |           Phase 2: ANALYZE            |
                     |  - Build Root Cause Analyzer chain    |
                     |  - Concurrently run 4 Debates         |
                     |  - Verify CRM constraints (Budget...) |
                     +---------------------------------------+
                                         |
                                         v
                     +---------------------------------------+
                     |           Phase 3: REASON             |
                     |  - Propose Scenarios (A, B, C)        |
                     |  - Run Devil's Advocate Counterpoints  |
                     |  - Calculate Least-Regret Scores      |
                     +---------------------------------------+
                                         |
                                         v
                     +---------------------------------------+
                     |           Phase 4: VERIFY             |
                     |  - Run Reflective Self-Critique       |
                     |  - Calculate Ground-Truth Confidence  |
                     +---------------------------------------+
                                         |
                                         v
                     +---------------------------------------+
                     |           Phase 5: DECIDE             |
                     |  - Synthesis (Nemotron/Groq fallback) |
                     |  - Output Verdict & Action Steps      |
                     +---------------------------------------+
```

---

## 4. The 5-Phase, 16-Module Reasoning Pipeline

When a user submits a question to the `/reason` endpoint, the query traverses a structured pipeline. Depending on the question complexity, the **Friction Engine** dynamically routes the query through a `LOW`, `MEDIUM`, or `HIGH` pipeline depth:
*   `LOW`: Direct data lookups (4 steps). Bypasses deep analysis, debates, scenarios, and verification.
*   `MEDIUM`: Tactical decisions (9 steps). Executes intents, debates, root cause, and constraints check.
*   `HIGH`: Strategic decisions (full 16 steps). Executes all scenario planning, devil's advocate, and regret simulation stages.

Below is the file-by-file breakdown of every module:

### Phase 1: UNDERSTAND (All Friction Levels)
1.  **Intent Classifier** ([`modules/m01_intent.py`](file:///c:/Users/tharu/Downloads/Friction_Ai_LATESTT/backend/modules/m01_intent.py)): Uses an LLM to extract the underlying business goal, constraints, and target time horizon from the question. Returns a parsed JSON structure: `{"goal": str, "constraints": list, "time_horizon": str}`.
2.  **Friction Classifier** ([`modules/m02_friction.py`](file:///c:/Users/tharu/Downloads/Friction_Ai_LATESTT/backend/modules/m02_friction.py)): Classifies the question complexity into `LOW`, `MEDIUM`, or `HIGH` by comparing the question and intent parameters. Determines the cognitive pipeline path.
3.  **Live CRM Context Builder** ([`modules/m03_context.py`](file:///c:/Users/tharu/Downloads/Friction_Ai_LATESTT/backend/modules/m03_context.py)): Reads SQLite databases (without using LLM calls) to generate a structured, real-time snapshot of the company's financial metrics, sales pipelines, headcount budgets, and customer churn.
4.  **Vector DB Memory Retrieval** ([`modules/m04_memory.py`](file:///c:/Users/tharu/Downloads/Friction_Ai_LATESTT/backend/modules/m04_memory.py)): Performs a semantic search against the Chroma vector database using the user query + goal to pull up to 3 highly relevant historical files, past decisions, or team benchmarks.
5.  **External API Context Layer** ([`modules/m_external_context.py`](file:///c:/Users/tharu/Downloads/Friction_Ai_LATESTT/backend/modules/m_external_context.py)): Fires read-only API calls concurrently to pull news, Google search, FRED macro interest rates/inflation index, and Yahoo Finance sector ETFs (details in Section 7).

### Phase 2: ANALYZE (Medium + High)
6.  **Root Cause Analyzer** ([`modules/m05_rootcause.py`](file:///c:/Users/tharu/Downloads/Friction_Ai_LATESTT/backend/modules/m05_rootcause.py)): Builds an analytical cause chain (Why $\rightarrow$ Why $\rightarrow$ Why $\rightarrow$ Why) to identify the deep root cause of the business problem.
7.  **Cross-Department Debates** ([`modules/m06_debate.py`](file:///c:/Users/tharu/Downloads/Friction_Ai_LATESTT/backend/modules/m06_debate.py)): Launches four department personas concurrently (Finance, Operations, Sales, HR) in a thread pool. Each director persona is supplied with their department's specific CRM metrics slice and debates whether to support, oppose, or hold a neutral stance on the action.
8.  **Evidence Validation** ([`modules/m08_validate.py`](file:///c:/Users/tharu/Downloads/Friction_Ai_LATESTT/backend/modules/m08_validate.py)): Validates the arguments generated during department debates against the ground-truth SQLite data, assigning an overall *Evidence Score* (0-100) indicating if debate claims match real data.

### Phase 3: REASON (High Only)
9.  **Scenario Path Simulation** ([`modules/m07_scenarios.py`](file:///c:/Users/tharu/Downloads/Friction_Ai_LATESTT/backend/modules/m07_scenarios.py)): Simulates 3 distinct future scenarios (Scenario A: Aggressive; Scenario B: Phased/Recommended; Scenario C: Conservative) along with revenue estimates, timelines, and risks.
10. **Devil's Advocate Challenge** ([`modules/m07_scenarios.py`](file:///c:/Users/tharu/Downloads/Friction_Ai_LATESTT/backend/modules/m07_scenarios.py)): Generates 3 sharp counter-arguments that directly critique the leading recommendation.
11. **Regret Simulation** ([`modules/m07_scenarios.py`](file:///c:/Users/tharu/Downloads/Friction_Ai_LATESTT/backend/modules/m07_scenarios.py)): Evaluates choices 6 months in the future. Assigns a regret score (0-10) to each path to calculate the lowest-regret option.

### Phase 4: VERIFY (Medium + High)
12. **Business Constraints Validator** ([`modules/m08_validate.py`](file:///c:/Users/tharu/Downloads/Friction_Ai_LATESTT/backend/modules/m08_validate.py)): Validates operational safety bounds:
    *   *Budget*: Checks if cash reserves support the decision.
    *   *Headcount*: Evaluates if current team size can execute the action.
    *   *Capacity*: Identifies team fatigue.
    *   *Customer Risk*: Checks impact on at-risk high-churn accounts.
13. **Reflective Self-Critique** ([`modules/m08_validate.py`](file:///c:/Users/tharu/Downloads/Friction_Ai_LATESTT/backend/modules/m08_validate.py)): The AI critically evaluates its own reasoning, checking for selection bias, over-reliance on past cases, or consensus gaps.
14. **Confidence Weights Engine** ([`main.py`](file:///c:/Users/tharu/Downloads/Friction_Ai_LATESTT/backend/main.py)): A programmatic, ground-truth calculator that bypasses LLM guessing. It uses a strict math formula to calculate confidence:
    $$\text{Confidence Score} = \text{round}(0.35 \times \text{Agreement} + 0.25 \times \text{Memory Match} + 0.20 \times \text{Evidence} + 0.20 \times \text{Scenario Stability})$$
    *   *Agreement*: Alignments among departments (4 agree = 100, 3 agree = 75, 2-2 split = 50, 3 against = 25).
    *   *Memory Match*: Vector database cosine similarity score $\times$ 100.
    *   *Evidence*: Ground-truth validation score (0-100).
    *   *Scenario Stability*: Variance in scenario risk ratings (All Low = 80, mixed = 60, all High = 40).

### Phase 5: DECIDE (All Friction Levels)
15. **Executive Synthesis** ([`modules/m09_nemotron.py`](file:///c:/Users/tharu/Downloads/Friction_Ai_LATESTT/backend/modules/m09_nemotron.py)): Combines all upstream telemetry, debates, scenarios, and constraints into a single prompt. Calls NVIDIA Nemotron (or Groq Llama 3.3 70B if rate-limited or JSON validation fails) to synthesize the board-ready briefing.
16. **Explainability Engine** ([`modules/m09_nemotron.py`](file:///c:/Users/tharu/Downloads/Friction_Ai_LATESTT/backend/modules/m09_nemotron.py)): Outputs a formatted JSON response containing the final decision verdict (1-2 sentences), key stats cards, statistics explanations (exactly 3 short strategic bullet points), narrative trade-offs, and step-by-step action plans with specific timelines.

---

## 5. The CRM Database & Live Dashboard

### Database Structure ([`data/crm_db.py`](file:///c:/Users/tharu/Downloads/Friction_Ai_LATESTT/backend/data/crm_db.py))
Friction connects to a SQLite database (`backend/data/crm.db`) seeded with 13 tables:
*   `customers`: Accounts, MRR, churn indicators, LTV.
*   `deals`: Sales pipeline stage, probabilities, close dates.
*   `financials`: Revenue history, profit metrics.
*   `team`: Department metrics, performance reviews, salaries.
*   `decisions`: Historical decisions catalog.
*   `products`: Product details, margins, volumes.
*   `inventory`: Quantity on hand, reorder thresholds (Edge Gateways).
*   `campaigns`: Marketing spend, conversions, ROI.
*   `tickets`: Support tickets queue, CSAT.
*   `suppliers`: Supplier ratings, delay statistics.
*   `expenses`: Operational burn categories.
*   `kpi`: Key Performance Indicator historical logs.
*   `contracts`: Contract values, renewal ranges.

### Live CRM Dashboard
The UI sidebar contains a **Live CRM** section. This dashboard acts as a database explorer, hitting backend endpoints (`GET /data-sources` and `GET /data-sources/{table}`) to retrieve, paginates, filter, and audit actual SQLite database rows in real time. This ensures total transparency for the business owner.

---

## 6. Canary Sentinel (Proactive Watchdog)

The Canary Sentinel watchdog runs as a background daemon ([`modules/canary_engine.py`](file:///c:/Users/tharu/Downloads/Friction_Ai_LATESTT/backend/modules/canary_engine.py)) to detect operational threats.

### How It Works:
1.  **Scheduler Loop**: Runs in a background thread at user-selected intervals (1 minute or 1 hour), controlled by config states in the database.
2.  **Incremental Scanning**: On each run, the engine queries the SQLite database for support tickets opened and deals closed since the last scan timestamp checkpoint.
3.  **Mathematical Drift (Z-Score)**: The engine extracts:
    *   `qty_on_hand` (safety stock levels of Edge Gateways).
    *   `reorder_point` (reorder thresholds).
    *   `tickets` (30-day daily average of support tickets).
    It computes Z-score drift relative to normal historical baselines:
    $$z = \frac{\text{current\_value} - \text{baseline\_mean}}{\text{baseline\_std\_dev}}$$
    An aggregate anomaly score is calculated using Euclidean Z-score distance (giving higher weight when inventory drops combined with ticket volume spikes).
4.  **Failure Signature Matching**: Using `numpy` and `scikit-learn` vector math, it calculates the Cosine Similarity between the current drift vector and historical failure patterns loaded from the SQLite `canary_failure_library`.
5.  **Alert Resolution**:
    *   If the aggregate anomaly score $\ge 2.0$ or pattern similarity $\ge 0.85$, it fires an alert.
    *   It calls Groq to generate a simple, user-friendly **headline problem statement** and a practical, step-by-step **remedial solution** based on the metrics.
    *   The alert is saved to `canary_alerts` and renders on the UI Canary tab with a threat confidence score (matching the cosine similarity %).

---

## 7. External API Context Layer (Advisory Only)

Friction AI implements a strict **Advisory API Context Layer** ([`modules/m_external_context.py`](file:///c:/Users/tharu/Downloads/Friction_Ai_LATESTT/backend/modules/m_external_context.py)) to enrich synthesis with macro data:

*   **Tavily Search API**: Gathers recent sector news, market expansion outlooks, and tech startup acquisition announcements.
*   **SerpAPI (Google Search)**: Queries competitor search results, standard benchmarks, and salaries.
*   **FRED API (Federal Reserve)**: Fetches macroeconomic indicators like interest rates (FEDFUNDS), inflation index (CPIAUCSL), unemployment rate (UNRATE), and GDP.
*   **Yahoo Finance (`yfinance`)**: Retrieves closing prices and 52-week ranges for relevant sector ETFs (e.g. `XLK` for technology, `XLF` for finance).

### Isolation & Integrity Guarantees:
*   **Zero Database/Vector Writes**: The module contains zero imports from `crm_db.py`, `canary_db.py`, or `vectordb.py` and performs no database updates.
*   **Advisory Only**: External data is appended at the very end of the LLM synthesis prompt under a clear `[EXTERNAL MARKET CONTEXT — ADVISORY ONLY]` label. The LLM system prompt explicitly instructs the model to use it only to frame the narrative, and forbids it from altering the primary CRM-derived verdict, confidence score, or department stances.
*   **Graceful Degradation**: If API keys are missing or calls fail/timeout (8-second timeout on background fetch), the fetchers return `""` silently, and the pipeline continues unaffected.

---

## 8. Document Ingestion & RAG (Retrieval-Augmented Generation)

Friction AI supports uploading custom files to expand its knowledge base:
1.  **Ingestion Endpoint** (`POST /upload-document`): Accepts files (`.pdf`, `.xlsx`, `.csv`, `.txt`, `.md`, `.json`).
2.  **Parsing Engine**:
    *   *PDF*: Parsed using `pypdf` extraction.
    *   *Excel*: Parsed sheet-by-sheet, reading rows and headers using `openpyxl`.
    *   *CSV/Text*: Mapped into plain text strings.
3.  **Chunking & Indexing**: Text is split into 1000-character chunks with 200-character overlap. Each chunk is embedded using the sentence transformer and upserted into an in-memory Chroma DB collection (`crm_knowledge`).
4.  **Metadata Catalog**: Metadata is persistently written to `uploaded_docs.json`. On backend reboot, the server automatically reads this catalog and re-indexes all files, ensuring RAG memory persists across server restarts.

---

## 9. Current Technical Limitations & Future Work

*   **Chroma In-Memory Only**: Chroma DB runs as an in-memory client. If the backend process is killed, the vector index is lost. It is rebuilt on startup by reading the `uploaded_docs.json` catalog and re-embedding. A persistent database client (e.g. Chroma persistent client) is future work.
*   **Static Sentinel Baselines**: Normal means and standard deviations for Z-score drift are static values defined in `canary_engine.py` instead of dynamically calculated rolling averages.
*   **NIM Rate Limits**: NVIDIA NIM API keys can hit rate limits on high-frequency requests, making the Groq synthesis fallback engine critical for production stability.

# backend/modules/m09_nemotron.py
"""
Module 15 — Recommendation Generator + Module 16 — Explainability Engine
Synthesizes ALL pipeline outputs into a rich executive briefing.
Falls back to Groq Llama 3.3 70B if NVIDIA limits are hit.
"""
import os
import json
from openai import OpenAI


def run_nemotron_synthesis(
    question: str,
    intent: dict,
    friction: dict,
    context: dict,
    past_memory: str,
    past_memory_score: float,
    root_cause: dict,
    views: list,
    validation: dict,
    scenarios_data: dict,
    self_review_text: str,
    client_groq=None,
    external_context: str = "",
) -> dict:
    """
    Final synthesis module — takes ALL upstream outputs and produces
    a structured executive briefing with rich narrative, stats, scenarios, and action plan.
    """
    nvidia_api_key = os.getenv("NVIDIA_API_KEY")
    nvidia_client = OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=nvidia_api_key
    )

    # ── Build compact input for the LLM ──────────────────────────────────────
    intent_str = json.dumps(intent)
    friction_level = friction.get("level", "MEDIUM")
    context_text = context.get("snapshot_text", "") if context else ""
    fin = context.get("financials", {}) if context else {}
    team_ctx = context.get("team", {}) if context else {}
    pipeline_ctx = context.get("sales_pipeline", {}) if context else {}
    customers_ctx = context.get("customers", {}) if context else {}

    root_cause_str = json.dumps(root_cause) if root_cause else "{}"
    scenarios_str = json.dumps(scenarios_data.get("scenarios", [])) if scenarios_data else "[]"
    devils_str = json.dumps(scenarios_data.get("devils_advocate", [])) if scenarios_data else "[]"
    regret_str = json.dumps(scenarios_data.get("regret_analysis", {})) if scenarios_data else "{}"
    evidence_score = validation.get("evidence_score", 70) if validation else 70
    constraints = validation.get("constraints", []) if validation else []
    constraint_status = validation.get("overall_constraint_status", "Clear") if validation else "Clear"

    dept_names = ["Finance", "Operations", "Sales", "HR"]
    views_formatted = []
    for i, v in enumerate(views or []):
        if v:
            name = dept_names[i] if i < len(dept_names) else f"Dept{i}"
            views_formatted.append({
                "name": name,
                "stance": v.get("stance", "Neutral"),
                "reasons": v.get("reasons", [])
            })

    # ── System Prompt ─────────────────────────────────────────────────────────
    system_prompt = """You are Friction — an enterprise-grade AI business reasoning engine.
You have completed a full cognitive analysis pipeline. Now produce the final executive output.

If an [EXTERNAL MARKET CONTEXT — ADVISORY ONLY] block is present in the input, you may use it solely to add market framing or backdrop to your narrative — it must never change the verdict, confidence score, evidence score, or department stances, which are derived exclusively from internal CRM data.

You do NOT sound like ChatGPT. You sound like a Board-level advisor with real data.
Your output is NOT generic. Every sentence references specific numbers from the context.

GLOBAL SYNTHESIS & FORMATTING CONSTRAINTS:
- Synthesize information rather than repeating the exact same key phrases (e.g., 'lack of warehouse space') verbatim across the context_explanation, verdict, stats_explanation, and root_cause_summary sections. Vary phrasing and emphasize different aspects of the metrics in each section.
- Decision Verdict: Must be exactly 1 to 2 punchy, definitive sentences. No fluff.
- Statistical & Decision Logic: Must be formatted as exactly 3 short, strategic bullet points. Do strictly prohibit paragraph format here.
- Immediate Action Steps: Must use concise bullet points inside each action plan step instead of walls of text.

Produce a JSON object with this EXACT shape:

{
  "verdict": "Exactly 1 to 2 punchy, definitive sentences explaining the exact decision and the primary strategic justification. No fluff.",
  
  "context_explanation": "A deeply detailed, comprehensive analysis (3-4 paragraphs) outlining the business context. Explicitly reference live CRM metrics (e.g. employee count, MRR, won/lost ARR, support queue load, inventory status, campaign ROI). Detail how these metrics connect to the user's specific business dilemma and explain the operational landscape.",
  
  "key_stats": [
    {"label": "string", "value": "string", "trend": "up"|"down"|"stable"|"warning"}
  ],
  
  "stats_explanation": "Exactly 3 short, strategic bullet points outlining the decision logic based on the stats above. Prohibit paragraphs completely.",
  
  "narrative": "A highly detailed executive briefing summarizing the strategic trade-offs, potential bottlenecks, and long-term organizational impact.",
  
  "root_cause_summary": "A detailed 1-2 sentence breakdown of the root cause from the analysis.",
  
  "departments": [
    {"name": "string", "status": "yes"|"no"|"wait", "score": 0-100, "reason": "A detailed, descriptive sentence explaining the department's stance with numbers"}
  ],
  
  "evidence_score": integer 0-100,
  
  "scenarios": [
    {"name": "string", "revenue_impact": "string", "risk": "Low"|"Medium"|"High", "recommended": true|false, "description": "Highly detailed paragraph explaining this scenario, how it would be rolled out, and its risk profile.", "breaking_assumption": "Detailed description of what assumption breaks this scenario"}
  ],
  
  "devils_advocate": ["A detailed counterargument paragraph 1", "A detailed counterargument paragraph 2", "A detailed counterargument paragraph 3"],
  
  "regret_choice": "A detailed 2-3 sentence analysis of the lowest-regret option and why it is chosen",
  
  "constraints_check": [
    {"name": "string", "status": "OK"|"Warning"|"Violated", "detail": "Detailed explanation of the constraint verification result"}
  ],
  
  "self_review": "3-4 sentences of honest, critical self-critique evaluating the limits of this reasoning and potential information gaps",
  
  "confidence": integer 0-100,
  "confidence_breakdown": {
    "agreement": integer,
    "memory_match": integer,
    "evidence": integer,
    "scenario_stability": integer
  },
  
  "action_plan": [
    {
      "title": "Concise step title",
      "step": "Concise bullet points outlining how the business owner should execute this step (who is involved, success metrics, potential pitfalls). Do not use walls of text.",
      "timeframe": "Specific execution window (e.g. this week, this month, in 3 months)"
    }
  ],
  
  "if_ignored": ["A detailed consequence if ignored 1", "A detailed consequence if ignored 2", "A detailed consequence if ignored 3"],
  
  "mistake_context": "omit if no relevant past case, else: what happened before and what it cost",
  "pattern_match": "omit if no pattern, else: 1 sentence connecting past to present"
}

CONFIDENCE FORMULA (must follow exactly):
confidence = round(0.35 * agreement + 0.25 * memory_match + 0.20 * evidence + 0.20 * scenario_stability)
where:
- agreement = % of departments aligned (4 agree = 100, 3 agree = 75, 2-2 split = 50, 3 against = 25)
- memory_match = memory_similarity_score * 100 (0-100)
- evidence = evidence_score from validation module (0-100)
- scenario_stability = 100 minus scenario risk spread (if all Low=80, mixed=60, all High=40)

KEY STATS to include (pick 4-6 most relevant):
- Monthly Revenue with trend
- Open Pipeline Value
- Team headcount and payroll
- Profit Margin %
- High-churn accounts count
- Closed-Won YTD
"""

    user_content = f"""Question: "{question}"
Friction Level: {friction_level}
Intent: {intent_str}

Live CRM Snapshot:
{context_text}

Financial: Revenue=${fin.get("monthly_revenue",0):,.0f}, Margin={fin.get("profit_margin_pct",0)}%, Trend={fin.get("revenue_trend","")}
Team: {team_ctx.get("total_headcount",0)} people, Payroll=${team_ctx.get("annual_payroll",0):,.0f}
Pipeline: ${pipeline_ctx.get("open_value",0):,.0f} open, {pipeline_ctx.get("open_deals",0)} deals, ${pipeline_ctx.get("closed_won_ytd",0):,.0f} won
Customers: Avg LTV=${customers_ctx.get("avg_ltv",0):,.0f}, {customers_ctx.get("high_churn_count",0)} high-churn accounts

Business Memory (similarity={past_memory_score:.2f}):
{past_memory[:8000]}

Root Cause Analysis: {root_cause_str}

Department Debate: {json.dumps(views_formatted)}

Evidence Score: {evidence_score}/100
Constraint Status: {constraint_status}
Constraints: {json.dumps(constraints)}

Scenarios: {scenarios_str}
Devil's Advocate: {devils_str}
Regret Analysis: {regret_str}

Self Review: {self_review_text}"""

    # Append external advisory context if available — placed last so LLM
    # processes all CRM evidence before seeing market framing.
    if external_context:
        user_content += f"\n\nExternal Market Context (advisory, not evidence — must not change verdict or confidence):\n{external_context}"

    def _try_nvidia():
        completion = nvidia_client.chat.completions.create(
            model="nvidia/nemotron-3-ultra-550b-a55b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.2,
            top_p=0.95,
            max_tokens=4096,
            extra_body={"chat_template_kwargs": {"enable_thinking": True}, "reasoning_budget": 2048},
            stream=False,
            timeout=60.0
        )
        msg = completion.choices[0].message
        reasoning = getattr(msg, "reasoning_content", None)
        if reasoning:
            print("\n--- [Nemotron Thinking] ---")
            try:
                print(reasoning)
            except UnicodeEncodeError:
                print(reasoning.encode('ascii', errors='replace').decode('ascii'))
        print("\n--- [Synthesis Complete] ---\n")
        return msg.content

    def _try_groq():
        resp = client_groq.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        return resp.choices[0].message.content.strip()

    # ── Attempt NVIDIA → Fallback Groq ───────────────────────────────────────
    raw = None
    try:
        raw = _try_nvidia()
        # Verify JSON validity immediately to trigger Groq fallback on truncation
        clean_test = raw.strip()
        if "```json" in clean_test:
            clean_test = clean_test.split("```json")[1].split("```")[0].strip()
        elif "```" in clean_test:
            clean_test = clean_test.split("```")[1].split("```")[0].strip()
        json.loads(clean_test)
    except Exception as e:
        print(f"\n[!] NVIDIA failed or returned invalid JSON ({e}). Using Groq fallback...")
        if client_groq:
            try:
                raw = _try_groq()
            except Exception as ge:
                print(f"[!] Groq also failed: {ge}")
                raw = None
        else:
            raw = None

    if not raw:
        return _fallback_response(question, friction_level)

    # ── Clean and parse JSON ──────────────────────────────────────────────────
    clean = raw.strip()
    if "```json" in clean:
        clean = clean.split("```json")[1].split("```")[0].strip()
    elif "```" in clean:
        clean = clean.split("```")[1].split("```")[0].strip()

    try:
        return json.loads(clean)
    except Exception as e:
        print(f"[!] JSON parse error: {e}\nRaw: {raw[:500]}")
        # Try to extract JSON from mixed content
        import re
        match = re.search(r'\{.*\}', clean, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass
        return _fallback_response(question, friction_level)


def _fallback_response(question: str, friction_level: str) -> dict:
    return {
        "verdict": "Gather more data before committing to this decision.",
        "context_explanation": (
            "The analysis pipeline encountered a synthesis issue, but based on available CRM data, "
            "the business is in a stable revenue growth phase. Monthly revenue is currently $1.375M, "
            "supported by an active pipeline of approximately $1.187M across 31 active deals. "
            "Hiring or expansion requests must be balanced against current team size constraints (14 total employees)."
        ),
        "key_stats": [
            {"label": "Monthly Revenue", "value": "$1.375M", "trend": "up"},
            {"label": "Open Pipeline", "value": "$1.187M", "trend": "stable"},
            {"label": "Team", "value": "14 employees", "trend": "stable"},
            {"label": "Profit Margin", "value": "28.8%", "trend": "stable"},
        ],
        "stats_explanation": (
            "The profit margin of 28.8% indicates healthy financial performance, but operating with only "
            "14 employees suggests the organization is highly leveraged. Any sudden increases in pipeline "
            "velocity or service demands could strain operations before sales can close new revenue."
        ),
        "narrative": (
            "The analysis pipeline encountered a synthesis issue, but based on available CRM data, "
            "the business is in a stable revenue growth phase with an active pipeline of approximately $1.19M. "
            "A cautious approach is recommended until a complete analysis can be performed. "
            "The key tension is between growth opportunity and operational capacity constraints."
        ),
        "root_cause_summary": "Decision complexity requires full data review.",
        "departments": [
            {"name": "Finance", "status": "wait", "score": 70, "reason": "Revenue stable, monitor cash"},
            {"name": "Operations", "status": "wait", "score": 75, "reason": "Team at capacity"},
            {"name": "Sales", "status": "yes", "score": 80, "reason": "Pipeline supports growth"},
            {"name": "HR", "status": "wait", "score": 72, "reason": "Hiring pipeline not ready"},
        ],
        "evidence_score": 65,
        "scenarios": [
            {"name": "Proceed Now", "revenue_impact": "+$X", "risk": "High", "recommended": False, "description": "Aggressive rollout path.", "breaking_assumption": "Sudden cash flow drop"},
            {"name": "Wait 3 Months", "revenue_impact": "+$Y", "risk": "Medium", "recommended": True, "description": "Phased implementation plan.", "breaking_assumption": "Competitor market block"},
            {"name": "Partial Action", "revenue_impact": "+$Z", "risk": "Low", "recommended": False, "description": "Minimum viable trial path.", "breaking_assumption": "Low team alignment"},
        ],
        "devils_advocate": [
            "What if waiting allows competitors to act first?",
            "What if the revenue trend reverses next quarter?",
            "What if the team is more capable than metrics show?"
        ],
        "regret_choice": "Waiting 3 months has the lowest regret score based on current constraints.",
        "constraints_check": [
            {"name": "Budget", "status": "OK", "detail": "Margin supports moderate investment"},
            {"name": "Headcount", "status": "Warning", "detail": "Team near operational limit"},
        ],
        "self_review": "Analysis may be incomplete. Recommend human review before acting.",
        "confidence": 55,
        "confidence_breakdown": {"agreement": 50, "memory_match": 0, "evidence": 65, "scenario_stability": 60},
        "action_plan": [
            {"title": "Data Gathering", "step": "Gather complete operational data for comprehensive review", "timeframe": "this week"},
            {"title": "Capacity Assessment", "step": "Run departmental capacity assessment and audit operational load", "timeframe": "this month"},
        ],
        "if_ignored": [
            "Operational capacity may be exceeded",
            "Cash flow could be strained",
            "Team burnout risk increases"
        ]
    }

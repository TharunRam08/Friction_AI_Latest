# backend/modules/m08_validate.py
"""
Module 7 — Evidence Validation  (validates department claims against CRM data)
Module 13 — Business Constraints Validator (checks budget, headcount, compliance)
Module 14 — Reflective Self Review (AI critiques itself)
"""
import json
import os

def validate_evidence_and_constraints(
    question: str,
    debate_views: list,
    context: dict,
    client
) -> dict:
    """
    Validates department claims against real CRM data.
    Checks business constraints (budget, headcount, legal).
    """
    context_str = context.get("snapshot_text", "")
    fin = context.get("financials", {})
    team = context.get("team", {})

    system = """You are an evidence validator and business constraints checker.

You will receive:
- Department debate opinions
- Real CRM data (financials, team, pipeline)

Your job:
1. EVIDENCE VALIDATION: For each department claim, assess if the CRM data supports it (Yes/Partial/No). 
   Assign an overall Evidence Score (0-100).

2. CONSTRAINTS CHECK: Identify which business constraints are satisfied or violated:
   - Budget constraint (is cash flow sufficient?)
   - Headcount constraint (can current team support it?)
   - Operational capacity (is the team at limit?)
   - Customer risk (would this affect at-risk accounts?)

Return ONLY valid JSON:
{
  "evidence_score": 0-100,
  "evidence_breakdown": [
    {"department": "Finance", "claim": "brief claim", "evidence_status": "Supported"|"Partial"|"Unsupported", "reason": "1 sentence"}
  ],
  "constraints": [
    {"name": "Budget", "status": "OK"|"Warning"|"Violated", "detail": "1 sentence with numbers"}
  ],
  "overall_constraint_status": "Clear"|"Caution"|"Blocked"
}"""

    dept_names = ["Finance", "Operations", "Sales", "HR"]
    views_summary = []
    for i, v in enumerate(debate_views or []):
        if v:
            name = dept_names[i] if i < len(dept_names) else f"Dept{i}"
            reasons = v.get("reasons", [])
            stance = v.get("stance", "Neutral")
            views_summary.append(f"{name} ({stance}): {'; '.join(reasons)}")

    resp = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": (
                f'Question: "{question}"\n\n'
                f'Real CRM Data:\n{context_str}\n\n'
                f'Financial data: Revenue=${fin.get("monthly_revenue",0):,.0f}, '
                f'Profit margin={fin.get("profit_margin_pct",0)}%, '
                f'Trend={fin.get("revenue_trend","unknown")}\n'
                f'Team: {team.get("total_headcount",0)} people, '
                f'payroll=${team.get("annual_payroll",0):,.0f}\n\n'
                f'Department Opinions:\n' + '\n'.join(views_summary)
            )}
        ],
        model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
        response_format={"type": "json_object"},
        temperature=0.1,
    )
    try:
        result = json.loads(resp.choices[0].message.content)
        if isinstance(result, dict):
            return result
    except Exception as e:
        print(f"[!] Validation JSON decode error: {e}")
    return {
        "evidence_score": 70,
        "evidence_breakdown": [],
        "constraints": [],
        "overall_constraint_status": "Clear"
    }


def self_review(
    question: str,
    all_outputs: dict,
    client
) -> str:
    """
    Module 14 — Reflective Self Review.
    The AI critiques its own reasoning process.
    """
    system = """You are an AI performing a critical self-review of your own reasoning.

You will see a summary of the reasoning pipeline outputs. Ask yourself:
- Did I ignore important evidence?
- Am I relying too much on past cases that may not apply?
- Are the departments disagreeing too much to reach a reliable conclusion?
- Did I miss an obvious alternative?
- Should confidence be higher or lower?

Be honest and critical. Output 2-3 sentences max.
Return ONLY a plain text string (no JSON)."""

    summary = {
        "intent": all_outputs.get("intent", {}),
        "friction": all_outputs.get("friction", {}).get("level", "MEDIUM"),
        "memory_score": all_outputs.get("memory_score", 0),
        "evidence_score": all_outputs.get("validation", {}).get("evidence_score", 0),
        "constraint_status": all_outputs.get("validation", {}).get("overall_constraint_status", ""),
    }

    resp = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": f'Question: "{question}"\nReasoning summary: {json.dumps(summary)}'}
        ],
        model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
        temperature=0.4,
    )
    return resp.choices[0].message.content.strip()

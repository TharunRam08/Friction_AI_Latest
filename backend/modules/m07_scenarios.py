# backend/modules/m07_scenarios.py
"""
Module 9 — Scenario Simulation + Module 10 — Devil's Advocate + Module 11 — Regret Simulation
Generates 3 alternative futures, attacks each, then picks lowest-regret option.
"""
import json
import os

def run_scenarios_and_regret(question: str, intent: dict, context_snapshot: str,
                              debate_summary: str, client) -> dict:
    system = """You are a scenario planning and regret analysis engine.

Given a business question, current company data, and department perspectives, generate:

1. THREE distinct scenarios (not just "yes/no/wait" — make them creative but realistic):
   - Scenario A: The aggressive option
   - Scenario B: The moderate/recommended option  
   - Scenario C: The conservative option

2. For each scenario, estimate:
   - Expected revenue impact (+ or - amount)
   - Risk level: Low/Medium/High
   - Time to see results
   - Key assumption that could break it

3. Devil's Advocate — 3 sharp counter-arguments that challenge the leading recommendation

4. Regret Simulation — "Imagine 6 months from now. Which choice would you regret LEAST?"
   - Regret score for each option (0-10, lower = less regret)
   - Winner with reason

Return ONLY valid JSON:
{
  "scenarios": [
    {
      "name": "string",
      "description": "1 sentence",
      "revenue_impact": "+$X" or "-$X",
      "risk": "Low"|"Medium"|"High",
      "timeline": "string",
      "breaking_assumption": "string"
    }
  ],
  "devils_advocate": ["counter 1", "counter 2", "counter 3"],
  "regret_analysis": {
    "scenario_a_regret": 0-10,
    "scenario_b_regret": 0-10,
    "scenario_c_regret": 0-10,
    "lowest_regret_choice": "Scenario A|B|C",
    "regret_reason": "1 sentence"
  }
}"""

    resp = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": (
                f'Business Question: "{question}"\n'
                f'Strategic Intent: {json.dumps(intent)}\n\n'
                f'Current Business Context:\n{context_snapshot}\n\n'
                f'Department Perspectives Summary:\n{debate_summary}'
            )}
        ],
        model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
        response_format={"type": "json_object"},
        temperature=0.3,
    )
    try:
        result = json.loads(resp.choices[0].message.content)
        if not isinstance(result, dict):
            result = {}
    except Exception as e:
        print(f"[!] Scenarios JSON decode error: {e}")
        result = {}

    return {
        "scenarios": result.get("scenarios", []),
        "devils_advocate": result.get("devils_advocate", []),
        "regret_analysis": result.get("regret_analysis", {})
    }

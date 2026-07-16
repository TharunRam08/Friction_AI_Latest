# backend/modules/m02_friction.py
"""
Module 2 — Cognitive Friction Engine
Decides how much thinking is required based on question complexity.
LOW    → Simple data lookups, metric queries (4 steps)
MEDIUM → Tactical decisions, moderate impact (9 steps)
HIGH   → Strategic decisions, major impact (full 16 steps)
"""
import json
import os

def get_friction_level(question: str, intent: dict, client) -> dict:
    system = """You are a business decision complexity classifier for the Friction AI engine.

Classify the question into exactly one friction level:

LOW — Direct data queries, status checks, metric lookups
  Examples: "What was last month's revenue?", "How many customers do we have?"

MEDIUM — Tactical decisions with moderate risk and limited scope
  Examples: "Should we hire 1-2 people?", "Should we adjust pricing by 5%?", "Should we add a feature?"

HIGH — Strategic decisions with major business impact, multiple trade-offs, or irreversibility
  Examples: "Should we expand to a new city?", "Should we acquire a company?", "Should we launch a new product line?", "Should we restructure the team?"

Return ONLY valid JSON:
{"level": "LOW"|"MEDIUM"|"HIGH", "reason": "brief 1 sentence reason", "key_risks": ["risk1", "risk2"]}"""

    resp = client.chat.completions.create(
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": f'Question: "{question}"\nIntent: {json.dumps(intent)}'}],
        model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        response_format={"type": "json_object"},
        temperature=0.1,
    )
    result = json.loads(resp.choices[0].message.content)
    level = result.get("level", "MEDIUM").upper()
    if level not in ("LOW", "MEDIUM", "HIGH"):
        level = "MEDIUM"
    return {
        "level": level,
        "reason": result.get("reason", ""),
        "key_risks": result.get("key_risks", [])
    }

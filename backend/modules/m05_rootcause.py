# backend/modules/m05_rootcause.py
"""
Module 5 — Root Cause Intelligence
Builds a cause chain to identify WHY a problem exists or WHY a decision matters.
Not just: "Revenue is down" — but the full chain: Why → Why → Why
"""
import json
import os

def find_root_cause(question: str, context_snapshot: str, client) -> dict:
    system = """You are a root cause analysis engine for a business AI.

Given a business question and current company data, identify:
1. The SURFACE problem (what they see)
2. The CAUSE CHAIN (why → why → why, 3-4 levels deep)
3. The ROOT CAUSE (the actual underlying issue)

Be specific. Reference actual numbers from the context where relevant.

Return ONLY valid JSON:
{
  "surface_problem": "one sentence",
  "cause_chain": ["step 1", "step 2", "step 3", "step 4"],
  "root_cause": "one clear sentence identifying the real underlying cause",
  "severity": "Low"|"Medium"|"High"|"Critical"
}"""

    models = [os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"), "openai/gpt-oss-120b", "llama-3.3-70b-versatile"]
    resp = None
    last_err = None
    for m in models:
        try:
            resp = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": f'Business Question: "{question}"\n\nCurrent Business Context:\n{context_snapshot}'}
                ],
                model=m,
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            break
        except Exception as ex:
            last_err = ex
            continue
    if resp is None:
        raise last_err if last_err is not None else Exception("All models failed")
    try:
        result = json.loads(resp.choices[0].message.content)
        if not isinstance(result, dict):
            result = {}
    except Exception as e:
        print(f"[!] Root cause JSON decode error: {e}")
        result = {}

    return {
        "surface_problem": result.get("surface_problem", ""),
        "cause_chain": result.get("cause_chain", []),
        "root_cause": result.get("root_cause", ""),
        "severity": result.get("severity", "Medium")
    }

# backend/modules/m01_intent.py
import json
import os

def get_intent(question: str, client) -> dict:
    prompt = f"""
    You are a business strategist. Read the user's question: "{question}".
    Extract the underlying business goal, constraints, and time horizon.
    Return ONLY a valid JSON object with these exact keys: "goal", "constraints", "time_horizon".
    Example: {{"goal": "Increase Market Share", "constraints": ["Maintain Margin"], "time_horizon": "3 Months"}}
    """
    models = [os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"), "openai/gpt-oss-120b", "llama-3.3-70b-versatile"]
    chat_completion = None
    last_err = None
    for m in models:
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=m,
                response_format={"type": "json_object"},
                temperature=0.1,
            )
            break
        except Exception as ex:
            last_err = ex
            continue
    if chat_completion is None:
        raise last_err if last_err is not None else Exception("All models failed")
    clean_json = chat_completion.choices[0].message.content.strip()
    return json.loads(clean_json)

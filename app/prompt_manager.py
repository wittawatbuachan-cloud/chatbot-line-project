# app/prompt_manager.py

def build_prompt(
    cleaned_text: str,
    recent_context: list,
    user_profile: dict | None,
    config_prompts: dict
):
    system_instruction = config_prompts.get(
        "system_prompt",
        "You are a mental health support AI."
    )

    context_block = ""
    for msg in recent_context[-5:]:
        context_block += f"{msg['role']}: {msg['content']}\n"

    profile_block = ""
    if user_profile:
        profile_block = f"User profile: {user_profile}\n"

    prompt = f"""
SYSTEM:
{system_instruction}

CONTEXT:
{context_block}

{profile_block}

USER:
{cleaned_text}

Return ONLY JSON:
{{
  "emotion": "",
  "risk_level": "",
  "reply": ""
}}
"""

    return prompt

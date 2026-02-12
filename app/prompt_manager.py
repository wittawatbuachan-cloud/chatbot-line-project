# app/prompt_manager.py

def build_prompt(
    cleaned_text: str,
    recent_context: list,
    user_profile: dict | None,
    config_prompts: dict
):
    """
    สร้าง prompt พร้อม context memory
    """

    system_instruction = config_prompts.get(
        "system_prompt",
        "คุณคือผู้ช่วยด้านสุขภาพจิตที่พูดภาษาไทยอย่างเป็นธรรมชาติ "
        "น้ำเสียงอบอุ่น เข้าใจความรู้สึก "
        "ห้ามวินิจฉัยโรค และห้ามให้คำแนะนำทางการแพทย์เชิงลึก"
    )

    # ===============================
    # CONTEXT BLOCK
    # ===============================
    context_block = ""
    for msg in recent_context[-5:]:
        role = "ผู้ใช้" if msg["role"] == "user" else "ผู้ช่วย"
        context_block += f"{role}: {msg['content']}\n"

    # ===============================
    # PROFILE BLOCK
    # ===============================
    profile_block = ""
    if user_profile:
        profile_block = f"ข้อมูลผู้ใช้เพิ่มเติม: {user_profile}\n"

    # ===============================
    # FINAL PROMPT
    # ===============================
    prompt = f"""
SYSTEM:
{system_instruction}

บริบทก่อนหน้า:
{context_block}

{profile_block}

ข้อความล่าสุดของผู้ใช้:
{cleaned_text}

กติกาการตอบ:
- ใช้ภาษาไทยธรรมชาติ
- ตอบสั้น กระชับ
- แสดงความเข้าใจความรู้สึก
- ถ้ามีความเสี่ยงสูง ให้แนะนำสายด่วน 1323 อย่างสุภาพ
- ห้ามวินิจฉัยโรค

ตอบกลับเป็น JSON เท่านั้น:
{{
  "emotion": "",
  "risk_level": "low|medium|high",
  "reply": ""
}}
"""

    return prompt.strip()

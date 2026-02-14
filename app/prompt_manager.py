# app/prompt_manager.py

from typing import List, Dict, Optional

FEW_SHOT_EXAMPLES = """
Example 1:
User message:
I found some of my kids artwork from when they were little and it made me miss having them around all the time.

Expected JSON:
{
  "emotion": "nostalgia",
  "risk_level": "low",
  "reply": "Looking at those old artworks must have brought back so many meaningful memories. Missing those everyday moments shows how deeply you care about them."
}

Example 2:
User message:
I feel like nothing I do matters anymore.

Expected JSON:
{
  "emotion": "hopelessness",
  "risk_level": "medium",
  "reply": "I'm really sorry you're feeling this way. When things start to feel meaningless, it can feel heavy and exhausting. Would you like to tell me what's been weighing on you lately?"
}

Example 3:
User message:
I used to get excited over getting girls' numbers... nowadays I get excited over free cash and paying off credit card bills.

Expected JSON:
{
  "emotion": "excited",
  "risk_level": "low",
  "reply": "It sounds like your priorities have really evolved over time. Finding excitement in financial progress can actually feel empowering."
}

Example 4:
User message:
ฉันอยากตาย

Expected JSON:
{
  "emotion": "despair",
  "risk_level": "high",
  "reply": "ฉันเสียใจมากที่ได้ยินว่าคุณรู้สึกแบบนี้ คุณไม่ได้อยู่คนเดียวนะ หากคุณรู้สึกไม่ปลอดภัย โปรดติดต่อสายด่วนสุขภาพจิต 1323 หรือ 1669 ทันที"
}
"""


def build_prompt(
    *,
    cleaned_text: str,
    recent_context: List[Dict],
    user_profile: Optional[Dict],
    config_prompts: Dict
) -> str:
    """
    Build final prompt for Gemini.

    - cleaned_text: ข้อความของผู้ใช้ที่ผ่าน preprocessing แล้ว
    - recent_context: list ของข้อความย้อนหลัง (dicts with keys 'role' and 'content')
    - user_profile: optional metadata about the user
    - config_prompts: จาก DB (should include 'prompt_template' and optional 'few_shot_examples')
    """

    # system instruction: from DB if available, otherwise fallback
    system_instruction = config_prompts.get("prompt_template") or config_prompts.get("system_prompt", "").strip()
    if not system_instruction:
        # reasonable default if DB doesn't contain a prompt_template
        system_instruction = ("""คุณคือผู้ช่วยด้านสุขภาพจิตที่พูดภาษาไทยอย่างเป็นธรรมชาติ
            น้ำเสียง: อบอุ่น อ่อนโยน และเข้าใจความรู้สึก
            กฎภาษา:
            - ตอบเป็นภาษาที่ผู้ใช้ใช้ (ถ้าผู้ใช้พิมพ์ไทย ให้ตอบเป็นไทย)
            - ห้ามใช้ศัพท์วิชาการยากหรือภาษาทางการเกินไป
            - ตอบสั้น กระชับ และเข้าใจง่าย
            ความปลอดภัย:
            - ห้ามวินิจฉัยโรค
            - ห้ามให้คำแนะนำทางการแพทย์เชิงลึก
            - ถ้าพบความเสี่ยงสูง ให้แนะนำสายด่วน 1323 หรือ 1669 อย่างสุภาพ
            รูปแบบผลลัพธ์:
            ตอบกลับเป็น JSON เท่านั้นในรูปแบบ:
            { "emotion": "<string>", "risk_level": "low|medium|high", "reply": "<string>" }
        """)

    # few-shot examples: prefer DB value, otherwise use embedded FEW_SHOT_EXAMPLES
    few_shot = config_prompts.get("few_shot_examples")
    if not few_shot:
        few_shot = FEW_SHOT_EXAMPLES.strip()

    # build context block (last N messages)
    context_block = ""
    if recent_context:
        for msg in recent_context[-5:]:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            context_block += f"{role}: {content}\n"

    # user profile block (optional)
    profile_block = ""
    if user_profile:
        profile_block = "User profile:\n"
        for k, v in user_profile.items():
            profile_block += f"- {k}: {v}\n"

    # final prompt composition
    prompt = f"""
SYSTEM INSTRUCTION:
{system_instruction}

FEW SHOT EXAMPLES:
{few_shot}

CONTEXT:
{context_block}

{profile_block}

USER:
{cleaned_text}

Return ONLY valid JSON in this format:
{{ "emotion": "<string>", "risk_level": "low|medium|high", "reply": "<string>" }}
""".strip()

    return prompt
# app/conversation_service.py

from app.conversation_repo import get_recent_messages
from app.prompt_manager import PromptManager

prompt_manager = PromptManager()


async def prepare_prompt(user_id: str, user_message: str):

    history = await get_recent_messages(user_id, limit=5)

    prompt = await prompt_manager.build_prompt(
        user_message=user_message,
        conversation_history=history
    )

    return prompt

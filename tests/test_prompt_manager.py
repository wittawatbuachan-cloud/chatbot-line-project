# tests/test_prompt_manager.py
from app.prompt_manager import build_prompt

def test_prompt_build():
    prompt = build_prompt(
        "hello",      # user message
        [],           # recent_context
        {},           # user_profile
        {}            # config_prompts
    )

    assert "hello" in prompt


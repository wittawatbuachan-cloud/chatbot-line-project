import os
import httpx
from app.config import settings

async def call_llm_system(user_context: str, system_prompt: str = None):
    # example with OpenAI ChatCompletions API
    headers = {
        "Authorization": f"Bearer {settings.LLM_API_KEY}",
        "Content-Type": "application/json"
    }
    messages = []
    if system_prompt:
        messages.append({"role":"system","content": system_prompt})
    messages.append({"role":"user","content": user_context})
    payload = {
        "model": "gpt-4o-mini" , # replace with model you have access to
        "messages": messages,
        "max_tokens": 256,
        "temperature": 0.7
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(settings.LLM_API_URL, json=payload, headers=headers)
        r.raise_for_status()
        data = r.json()
        # extract text depending on provider; for OpenAI:
        text = data["choices"][0]["message"]["content"]
        return text

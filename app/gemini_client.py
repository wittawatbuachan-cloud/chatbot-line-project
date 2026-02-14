# app/gemini_client.py
import os
import json
import asyncio
import logging
import time
from typing import Any
from config.logging_config import get_logger

logger = get_logger("gemini_client", "logs/gemini.log")

# Try to import the supported gemini SDKs in preferential order.
# We'll attempt to support both 'google.genai' (newer) and 'google.generativeai' (older).
genai_sdk = None
genai_client = None
SDK_MODE = None

try:
    # newer package style: from google import genai
    from google import genai as genai_new
    genai_sdk = genai_new
    SDK_MODE = "google.genai"
    logger.info("Using google.genai SDK")
except Exception:
    try:
        import google.generativeai as genai_old
        genai_sdk = genai_old
        SDK_MODE = "google.generativeai"
        logger.info("Using google.generativeai SDK")
    except Exception:
        genai_sdk = None
        SDK_MODE = None
        logger.warning("No google genai SDK found. Please install google-genai or google-generativeai.")


API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if not API_KEY:
    logger.warning("GOOGLE_API_KEY / GEMINI_API_KEY not set in environment. Gemini calls will fail until set.")


def _configure_sdk():
    global genai_client
    if genai_sdk is None:
        return

    try:
        if SDK_MODE == "google.genai":
            # newer client model
            # Some versions require genai.configure or genai.Client(); try both patterns.
            try:
                genai_sdk.configure(api_key=API_KEY)  # older-style configure may exist
            except Exception:
                pass
            try:
                genai_client = genai_sdk.Client()
            except Exception:
                # some versions don't require instantiation; keep genai_sdk module
                genai_client = None
        elif SDK_MODE == "google.generativeai":
            # older: google.generativeai.configure(...)
            try:
                genai_sdk.configure(api_key=API_KEY)
            except Exception:
                pass
            genai_client = None
    except Exception as e:
        logger.exception("Error configuring GenAI SDK: %s", e)
        genai_client = None


_configure_sdk()


async def _call_model_threadsafe(model: str, contents: Any, config: dict | None = None):
    """
    Run sync SDK call in thread to avoid blocking event loop.
    Returns raw text content from model (string).
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _call_model_sync, model, contents, config)


def _call_model_sync(model: str, contents: Any, config: dict | None = None) -> str:
    """
    Synchronous model call using whichever SDK is available.
    Return text or raise.
    """
    if genai_sdk is None:
        raise RuntimeError("No GeminAI SDK available")

    # default config placeholder
    config = config or {}

    # different SDKs have different APIs
    if SDK_MODE == "google.genai":
        # prefer using client if available
        try:
            if genai_client is not None:
                resp = genai_client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=config
                )
            else:
                # fallback to module-level call if supported
                resp = genai_sdk.models.generate_content(
                    model=model,
                    contents=contents,
                    config=config
                )
            # response object shapes vary; try to extract returned text
            text = ""
            if hasattr(resp, "text"):
                text = resp.text
            else:
                # try to extract from dict-like
                try:
                    text = resp.output_text  # sometimes provided
                except Exception:
                    text = str(resp)
            return text
        except Exception as e:
            logger.exception("google.genai call failed: %s", e)
            raise

    elif SDK_MODE == "google.generativeai":
        # older style generate_text or generate?
        try:
            # older docs: genai.generate_text(prompt=..., model=...)
            if hasattr(genai_sdk, "generate_text"):
                out = genai_sdk.generate_text(model=model, prompt=contents)
                # out may be an object with .text
                text = getattr(out, "text", str(out))
                return text
            else:
                # fallback to module-level models.generate_content if exists
                resp = genai_sdk.models.generate_content(model=model, contents=contents)
                if hasattr(resp, "text"):
                    return resp.text
                return str(resp)
        except Exception as e:
            logger.exception("google.generativeai call failed: %s", e)
            raise
    else:
        raise RuntimeError("Unsupported GenAI SDK mode")


async def generate_content_with_retry(prompt_contents: Any, model: str = "gemini-2.0-flash", max_retries: int = 3, backoff_base: float = 1.0):
    """
    Async wrapper with exponential backoff. `prompt_contents` should match the SDK 'contents' param:
    - For google.genai: contents is usually a list of message dicts or a text string depending on SDK version.
    - For older: adjust accordingly.

    Returns raw text (string).
    """
    last_exc = None
    for attempt in range(1, max_retries + 1):
        try:
            text = await _call_model_threadsafe(model=model, contents=prompt_contents, config={"response_mime_type": "application/json"})
            return text
        except Exception as e:
            last_exc = e
            sleep_time = backoff_base * (2 ** (attempt - 1))
            logger.warning("Gemini call failed (attempt %d/%d). Retrying in %.1fs. Error: %s", attempt, max_retries, sleep_time, e)
            await asyncio.sleep(sleep_time)

    logger.exception("Gemini call failed after %d attempts: %s", max_retries, last_exc)
    raise last_exc


async def generate_empathetic_response(prompt_text: str):
    """
    Given a prepared prompt (string), call Gemini and attempt to parse JSON response.
    Returns a dict with keys: emotion, risk_level, reply
    """
    # Attempt to call model. Depending on SDK version we pass contents as plain string or structured list.
    # We'll pass as simple string initially.
    contents = prompt_text

    try:
        raw = await generate_content_with_retry(prompt_contents=contents, model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"), max_retries=3)
        raw_text = raw.strip() if isinstance(raw, str) else str(raw)
        logger.info("RAW GEMINI: %s", raw_text[:1000])
        # Try parse JSON
        try:
            parsed = json.loads(raw_text)
            # validate keys
            emotion = parsed.get("emotion", "unknown")
            risk_level = parsed.get("risk_level", "unknown")
            reply = parsed.get("reply", "")
            return {"emotion": emotion, "risk_level": risk_level, "reply": reply}
        except json.JSONDecodeError:
            # Not JSON — return fallback safe object
            logger.warning("Gemini did not return JSON. Raw: %s", raw_text[:400])
            # best-effort: return raw text as reply
            return {"emotion": "unknown", "risk_level": "unknown", "reply": raw_text}
    except Exception as e:
        logger.exception("generate_empathetic_response failed")
        return {"emotion": "error", "risk_level": "unknown", "reply": "ขออภัย ระบบขัดข้องชั่วคราว กรุณาลองใหม่อีกครั้ง"}
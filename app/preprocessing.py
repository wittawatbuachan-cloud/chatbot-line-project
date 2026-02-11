# app/preprocess.py
import re
from pythainlp.tokenize import word_tokenize
from pythainlp.util import normalize

# ลบ/แทน emoji (range unicode)
EMOJI_RE = re.compile("[\U00010000-\U0010ffff]", flags=re.UNICODE)

# ลบตัวอักษรพิเศษบางอย่าง
ZERO_WIDTH_RE = re.compile(r"[\u200b\u200c\u200d]")

# simple slang map (ขยายตามต้องการ)
SLANG_MAP = {
    "กู": "ฉัน",
    "มึง": "คุณ",
    "เหนื่อยจัง": "เหนื่อย",
    # ขยายเพิ่มเติมได้
}

def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    t = text.strip()
    t = ZERO_WIDTH_RE.sub("", t)
    t = EMOJI_RE.sub(" ", t)            # แทน emoji ด้วย space (หรือเก็บแยกได้)
    t = normalize(t)                    # basic normalization from PyThaiNLP
    # replace common slang
    for k, v in SLANG_MAP.items():
        t = t.replace(k, v)
    # collapse multiple spaces
    t = re.sub(r"\s+", " ", t).strip()
    return t

def tokenize_text(text: str):
    """
    คืนค่า (cleaned_text, tokens_list)
    ใช้ newmm ซึ่งเหมาะกับภาษาไทยทั่วไป
    """
    cleaned = clean_text(text)
    tokens = word_tokenize(cleaned, engine="newmm")
    return cleaned, tokens

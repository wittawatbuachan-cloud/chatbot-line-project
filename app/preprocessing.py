from pythainlp import word_tokenize, normalizers
import re

def normalize_text(text: str) -> str:
    # basic normalization
    text = normalizers.normalize(text)
    # collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text

def tokenize_text(text: str):
    # use newmm (or default) tokenizer
    return word_tokenize(text, engine="newmm")

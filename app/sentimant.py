# wrapper: try to load wangchanberta model; fallback to keyword rules
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import asyncio
import os

MODEL_NAME = os.getenv("SENT_MODEL", "airesearch/wangchanberta-base-att-spm-uncased")  # example

_sent_pipeline = None

def get_pipeline():
    global _sent_pipeline
    if _sent_pipeline is None:
        try:
            tok = AutoTokenizer.from_pretrained(MODEL_NAME)
            model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
            _sent_pipeline = pipeline("text-classification", model=model, tokenizer=tok, return_all_scores=True)
        except Exception as e:
            print("Could not load local model:", e)
            _sent_pipeline = None
    return _sent_pipeline

async def analyze_sentiment(text: str):
    pipe = get_pipeline()
    if pipe:
        # huggingface pipeline is sync; run in thread
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, lambda: pipe(text))
        # result: list of labels/scores; convert to a simple sentiment + score
        # This depends on label names from model; adapt if needed
        scores = result[0]
        # find label with max score
        best = max(scores, key=lambda x: x['score'])
        label = best['label']
        score = float(best['score'])
        return label, score
    # fallback: simple rules
    negative_keywords = ["ฆ่า","ตาย","อยากตาย","หมดหวัง","ชอบเสียชีวิต","ไม่อยากอยู่"]
    s = text.lower()
    for k in negative_keywords:
        if k in s:
            return "neg", 0.95
    # else neutral
    return "neutral", 0.5

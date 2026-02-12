import time
from fastapi import Request

async def add_latency_metrics(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    latency = time.time() - start
    print(f"Latency: {latency:.3f} seconds")
    return response

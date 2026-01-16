from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="EasyRead API", version="0.1.0")

class SimplifyRequest(BaseModel):
    text: str
    level: str = "simple"

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/simplify")
def simplify(req: SimplifyRequest):
    # Stub for now: proves the pipeline works end-to-end.
    return {
        "original": req.text,
        "simplified": f"[{req.level}] {req.text}",
        "notes": ["Stub response — real simplifier comes next."]
    }

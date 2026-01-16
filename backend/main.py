from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="EasyRead API", version="0.1.0")


class SimplifyRequest(BaseModel):
    text: str
    level: str = "simple"  # later: simple / very_simple


@app.get("/health") # Checks if server is alive
def health():
    return {"status": "ok"}


@app.post("/simplify")
def simplify(req: SimplifyRequest):
    # Stub for now (so frontend can connect immediately later).
    return {
        "original": req.text,
        "simplified": f"[{req.level}] {req.text}",
        "notes": ["Stub response — real simplifier comes next."]
    }

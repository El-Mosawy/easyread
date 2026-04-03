from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware  # So react app hosted on different origin can call API without issues

# Create app object. Can be used to define endpoints (aka routes) later.
app = FastAPI(title="EasyRead API", version="0.1.0") 


app.add_middleware( # middleware to allow CORS so frontend can call API without issues.
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SimplifyRequest(BaseModel):
    text: str
    level: str = "simple"  # later: simple / very_simple

# Below we register API endpoints so they can be called by frontend
# e.g. someone hits http://localhost:8000/health in their browser, this function run
@app.get("/health") # API endpoints. Checks if server is alive
def health():
    return {"status": "ok"}


@app.post("/simplify") # API endpoint to simplify text
def simplify(req: SimplifyRequest): # telling FastAPI to match simplifyRequest model
    # Stub for now (so frontend can connect immediately later).
    return {
        "original": req.text, # returns a dict -> becomes JSON response auto
        "simplified": f"[{req.level}] {req.text}", # f-string formatting
        "notes": ["Stub response — real simplifier comes next."] # just a message
    }

#“I defined a FastAPI app, added a Pydantic request model for validation, 
# and added endpoints. FastAPI handles the routing, JSON serialisation, 
# and auto generates docs at /docs, which makes it easy to test and connect a frontend”
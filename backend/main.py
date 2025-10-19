from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from fastapi.middleware.cors import CORSMiddleware
import random, time
from core.pipeline import analyze



app = FastAPI(title="AutoAI Scout Backend", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeIn(BaseModel):
    url: HttpUrl

@app.get("/")
def root():
    return {"ok": True, "service": "autoai-scout", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/analyze")
def analyze(inp: AnalyzeIn):
    try:
        result = analyze_url(str(inp.url))
        time.sleep(random.uniform(1, 3))
        return {"ok": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



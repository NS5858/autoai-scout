from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import AnalyzeRequest, AnalyzeResponse, HealthResponse
from app.services.pipeline import analyze as analyze_pipeline

app = FastAPI(title="AutoAI Scout Backend", version="1.0.0")

# CORS offen (Frontend kann von überall anfragen)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["meta"])
async def root():
    return {
        "status": "ok",
        "service": "autoai-backend",
        "routes": ["/health", "/analyze", "/docs"]
    }

@app.get("/health", response_model=HealthResponse, tags=["meta"])
async def health():
    return HealthResponse(status="ok", service="autoai-backend")

@app.post("/analyze", response_model=AnalyzeResponse, tags=["analyze"])
async def analyze(payload: AnalyzeRequest = Body(...)):
    try:
        result = await analyze_pipeline(payload.url, prefer_lang=payload.prefer_lang)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")

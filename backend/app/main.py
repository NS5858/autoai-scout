from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import AnalyzeRequest, AnalyzeResponse
from app.link_parser import parse_listing
from app.services.pipeline import run_analysis
import uvicorn

app = FastAPI(
    title="AutoAI Scout Backend",
    description="Backend für Fahrzeuganalyse mit KI",
    version="1.0.0"
)

# -----------------------------------------------------------
# CORS erlauben (Frontend darf mit Backend kommunizieren)
# -----------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------
# Haupt-Endpunkt für Analyse
# -----------------------------------------------------------
@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    try:
        listing_data = parse_listing(request.url)
        if not listing_data:
            raise ValueError("Ungültiger oder leerer Datensatz erhalten.")

        result = run_analysis(listing_data)
        return AnalyzeResponse(success=True, message="Analyse erfolgreich", data=result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler bei der Analyse: {str(e)}")

@app.get("/")
async def root():
    return {"status": "ok", "message": "AutoAI Scout Backend läuft."}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)

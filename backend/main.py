from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re

# ---- FastAPI App ----
app = FastAPI(title="AutoAI Scout", version="1.0.0")

# ---- CORS: Frontend darf zugreifen (StackBlitz, Render, usw.) ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # fürs Testen offen; später Domains einschränken
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Health / Root ----
@app.get("/")
def home():
    return {"ok": True, "service": "autoai-scout", "version": "1.0.0"}

# ---- Analyze Endpoint ----
class AnalyzeInput(BaseModel):
    text: str

@app.post("/analyze")
def analyze(input: AnalyzeInput):
    t = input.text.lower()

    # Marken grob erkennen
    brands = ["mercedes","bmw","audi","vw","porsche","ford","toyota","opel","seat","skoda","renault","peugeot"]
    brand = next((b for b in brands if b in t), None)

    # Modell grob erkennen (z. B. 280ce, 320d, a4, c200, golf 5)
    model_match = re.search(r"\b([a-z]?\d{2,4}[a-z]{0,3}|[acq]\d{1,3}|golf\s?\d)\b", t)
    model = model_match.group(1) if model_match else None

    # Preis mit € erkennen (Punkte/Spaces raus)
    price_match = re.search(r"(\d{3,6})\s?€", t.replace(".", "").replace(" ", ""))
    price = int(price_match.group(1)) if price_match else None

    # Zustand heuristisch
    condition = "gebraucht"
    if "neu" in t:
        condition = "neu"
    if "unfall" in t or "schaden" in t:
        condition = "unfallwagen"
    if "top" in t or "sehr gut" in t or "scheckheft" in t:
        condition = "sehr gut"

    # Fallback-Preise
    base = {"mercedes":12000,"bmw":11000,"audi":10500,"vw":9000,"porsche":45000,"ford":8000,"toyota":8500,"opel":7000,"seat":7500,"skoda":8000,"renault":6500,"peugeot":6500}
    estimated = price or base.get(brand, 8000)

    # einfache Confidence
    conf = 0.9 if brand and (price or model) else (0.7 if brand else 0.5)

    return {
        "brand": brand,
        "model": model,
        "condition": condition,
        "estimated_price": estimated,
        "confidence": round(conf, 2)
    }

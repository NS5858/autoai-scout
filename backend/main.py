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

from pydantic import BaseModel
import re

class AnalyzeInput(BaseModel):
    text: str

@app.post("/analyze")
def analyze(input: AnalyzeInput):
    text = input.text.lower()

    brands = ["mercedes", "bmw", "audi", "vw", "porsche", "ford", "toyota", "opel", "seat", "skoda", "renault", "peugeot"]
    brand = next((b for b in brands if b in text), None)

    model_match = re.search(r"\b([a-z]?\d{2,4}[a-z]{0,3}|[acq]\d{1,3}|golf\s?\d)\b", text)
    model = model_match.group(1) if model_match else None

    price_match = re.search(r"(\d{3,6})\s?€", text.replace(".", "").replace(" ", ""))
    price = int(price_match.group(1)) if price_match else None

    condition = "gebraucht"
    if "neu" in text:
        condition = "neu"
    if "unfall" in text or "schaden" in text:
        condition = "unfallwagen"
    if "top" in text or "sehr gut" in text or "scheckheft" in text:
        condition = "sehr gut"

    base_prices = {
        "mercedes": 12000, "bmw": 11000, "audi": 10500, "vw": 9000,
        "porsche": 45000, "ford": 8000, "toyota": 8500, "opel": 7000,
        "seat": 7500, "skoda": 8000, "renault": 6500, "peugeot": 6500
    }
    estimated = price or base_prices.get(brand, 8000)
    confidence = 0.9 if brand and (price or model) else (0.7 if brand else 0.5)

    return {
        "brand": brand,
        "model": model,
        "condition": condition,
        "estimated_price": estimated,
        "confidence": round(confidence, 2)
    }



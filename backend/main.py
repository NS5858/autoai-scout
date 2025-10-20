from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import re
from core.link_parser import extract_text_from_url, extract_listing

app = FastAPI(title="AutoAI Scout", version="3.0.0")

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # später: auf deine Domain einschränken
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Models ---
class AnalyzeInput(BaseModel):
    text: str

class AnalyzeUrlInput(BaseModel):
    url: str

# --- Health ---
@app.get("/")
def home():
    return {"ok": True, "service": "autoai-scout", "version": "3.0.0"}

# --- Textanalyse ---
@app.post("/analyze")
def analyze(input: AnalyzeInput):
    text = input.text.lower()

    brands = [
        "mercedes", "bmw", "audi", "vw", "porsche", "ford",
        "toyota", "opel", "seat", "skoda", "renault", "peugeot"
    ]
    brand = next((b for b in brands if b in text), None)

    model_match = re.search(r"\b([a-z]?\d{2,4}[a-z]{0,3}|[acq]\d{1,3}|golf\s?\d)\b", text)
    model = model_match.group(1) if model_match else None

    price_match = re.search(r"(\d{3,6})\s?€", text.replace(".", "").replace(" ", ""))
    price = int(price_match.group(1)) if price_match else None

    condition = "gebraucht"
    if "neu" in text: condition = "neu"
    if "unfall" in text or "schaden" in text: condition = "unfallwagen"
    if "top" in text or "sehr gut" in text or "scheckheft" in text: condition = "sehr gut"

    base_prices = {
        "mercedes":12000,"bmw":11000,"audi":10500,"vw":9000,
        "porsche":45000,"ford":8000,"toyota":8500,"opel":7000,
        "seat":7500,"skoda":8000,"renault":6500,"peugeot":6500
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

# --- Marktwert-Bewertung ---
def evaluate_market_value(listing: dict) -> dict:
    price = listing.get("price")
    year = listing.get("year")
    mileage = listing.get("mileage")
    brand = (listing.get("brand") or "").lower() if listing.get("brand") else None
    condition = listing.get("condition", "gebraucht")

    if not price or not year:
        return {"rating": "unbekannt", "score": None, "comment": "Nicht genug Daten für Bewertung"}

    current_year = 2025
    age = current_year - int(year)
    age_factor = max(0.5, 1.2 - (age * 0.03))

    if mileage:
        mileage_factor = max(0.5, min(1.1, 1.1 - (mileage / 200000)))
    else:
        mileage_factor = 1.0

    brand_value = {
        "mercedes":1.1,"mercedes-benz":1.1,"bmw":1.1,"audi":1.05,"porsche":1.5,
        "vw":1.0,"volkswagen":1.0,"ford":0.9,"toyota":0.95,"opel":0.85,
        "renault":0.8,"skoda":0.9,"peugeot":0.85,"seat":0.88
    }.get(brand, 1.0)

    cond_factor = {"neu":1.2,"sehr gut":1.1,"gebraucht":1.0,"unfallwagen":0.7}.get(condition, 1.0)

    base_ref = 12000 * age_factor * mileage_factor * brand_value * cond_factor
    deviation = (price - base_ref) / base_ref

    if deviation < -0.15:
        rating, comment = "💚 Günstig", "Deutlich unter dem erwarteten Marktwert."
    elif deviation <= 0.15:
        rating, comment = "⚖️ Fairer Preis", "Preis im typischen Marktbereich."
    else:
        rating, comment = "💸 Teuer", "Über dem durchschnittlichen Marktwert."

    return {
        "rating": rating,
        "score": round((1 - abs(deviation)) * 100, 1),
        "expected_market_value": round(base_ref),
        "price_deviation_percent": round(deviation * 100, 1),
        "comment": comment,
    }

# --- URL-Analyse (Listing + Analyse + Bewertung) ---
@app.post("/analyze_url")
def analyze_url(input: AnalyzeUrlInput):
    try:
        listing = extract_listing(input.url)  # strukturierte Felder + combined_text
        analysis = analyze(AnalyzeInput(text=listing.get("combined_text", "")))
        market_value = evaluate_market_value(listing)
        return {"url": input.url, "listing": listing, "analysis": analysis, "market_value": market_value}
    except Exception as e:
        return {"url": input.url, "error": f"Analyse fehlgeschlagen: {e}"}

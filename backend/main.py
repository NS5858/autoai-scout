from fastapi import FastAPI
from pydantic import BaseModel
import re
from core.link_parser import extract_text_from_url, extract_listing

app = FastAPI(title="AutoAI Scout", version="2.0.0")

# ----------- Basismodell für Textanalyse -----------
class AnalyzeInput(BaseModel):
    text: str


@app.get("/")
def home():
    return {"ok": True, "service": "autoai-scout", "version": "2.0.0"}


# ----------- Textbasierte Analyse (bestehende Logik) -----------
@app.post("/analyze")
def analyze(input: AnalyzeInput):
    text = input.text.lower()

    # 1) Marke erkennen
    brands = [
        "mercedes", "bmw", "audi", "vw", "porsche", "ford",
        "toyota", "opel", "seat", "skoda", "renault", "peugeot"
    ]
    brand = next((b for b in brands if b in text), None)

    # 2) Modell grob erkennen
    model_match = re.search(r"\b([a-z]?\d{2,4}[a-z]{0,3}|[acq]\d{1,3}|golf\s?\d)\b", text)
    model = model_match.group(1) if model_match else None

    # 3) Preis herausziehen
    price_match = re.search(r"(\d{3,6})\s?€", text.replace(".", "").replace(" ", ""))
    price = int(price_match.group(1)) if price_match else None

    # 4) Zustand bestimmen
    condition = "gebraucht"
    if "neu" in text:
        condition = "neu"
    if "unfall" in text or "schaden" in text:
        condition = "unfallwagen"
    if "top" in text or "sehr gut" in text or "scheckheft" in text:
        condition = "sehr gut"

    # 5) Basispreise
    base_prices = {
        "mercedes": 12000, "bmw": 11000, "audi": 10500, "vw": 9000,
        "porsche": 45000, "ford": 8000, "toyota": 8500, "opel": 7000,
        "seat": 7500, "skoda": 8000, "renault": 6500, "peugeot": 6500
    }
    estimated = price or base_prices.get(brand, 8000)

    # 6) Confidence
    confidence = 0.9 if brand and (price or model) else (0.7 if brand else 0.5)

    return {
        "brand": brand,
        "model": model,
        "condition": condition,
        "estimated_price": estimated,
        "confidence": round(confidence, 2)
    }


# ----------- URL-basierte Analyse (komplett neu, High-End) -----------
class AnalyzeUrlInput(BaseModel):
    url: str


@app.post("/analyze_url")
def analyze_url(input: AnalyzeUrlInput):
    """
    Analysiert ein beliebiges Fahrzeug-Inserat (mobile.de, AutoScout24, Kleinanzeigen usw.)
    und liefert strukturierte Daten + KI-Analyse in einer gemeinsamen Antwort.
    """
    try:
        # 1. Listing vollständig extrahieren (strukturierte Daten)
        listing = extract_listing(input.url)

        # 2. Textanalyse durchführen (bestehende Funktion)
        analysis = analyze(AnalyzeInput(text=listing.get("combined_text", "")))

        # 3. Rückgabe: alles vereint
        return {
            "url": input.url,
            "listing": listing,    # enthält alle Felder: Marke, Modell, Baujahr, Preis, KM etc.
            "analysis": analysis   # dein heuristisches Ergebnis
        }

    except Exception as e:
        return {
            "url": input.url,
            "error": f"Analyse fehlgeschlagen: {e}"
        }

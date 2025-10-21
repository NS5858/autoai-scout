import random

def run_analysis(data: dict) -> dict:
    """Führt eine Fahrzeuganalyse durch und schätzt den Marktwert."""
    try:
        base_price = data.get("price", 0)
        mileage = data.get("mileage", 0)
        year = data.get("year", 0)

        age_penalty = max(0, (2025 - year) * 0.03)
        mileage_penalty = min(0.2, mileage / 200000)

        market_value = base_price * (1 - age_penalty - mileage_penalty)
        ai_score = round(random.uniform(70, 95), 2)

        return {
            "estimated_value": round(market_value, 2),
            "ai_confidence": ai_score,
            "details": {
                "mileage": mileage,
                "year": year,
                "original_price": base_price,
                "platform": data.get("platform"),
                "title": data.get("title"),
            }
        }

    except Exception as e:
        raise RuntimeError(f"Fehler bei der Analysepipeline: {e}")

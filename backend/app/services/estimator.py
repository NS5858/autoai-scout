def estimate_price(data: dict) -> float:
    """Berechnet einen groben Fahrzeugpreis basierend auf Daten."""
    base = data.get("price", 20000)
    mileage = data.get("mileage", 0)
    year = data.get("year", 2020)

    factor = 1 - ((2025 - year) * 0.02) - (mileage / 300000)
    return round(base * max(factor, 0.5), 2)

import statistics

def evaluate_market_value(data: dict) -> dict:
    """Simulierte Marktwertanalyse – später durch API oder Data Lake erweiterbar."""
    comparable_prices = [19200, 20500, 21000, 19800, 22000]  # Beispiel-Daten
    avg_price = statistics.mean(comparable_prices)
    deviation = data.get("price", 0) - avg_price
    trend = "unter Marktwert" if deviation < 0 else "über Marktwert"

    return {
        "average_market_value": round(avg_price, 2),
        "price_difference": round(deviation, 2),
        "valuation": trend,
        "comparables": len(comparable_prices)
    }

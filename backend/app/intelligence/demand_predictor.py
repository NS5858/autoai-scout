def predict_demand(data: dict) -> dict:
    """Einfache Nachfrageprognose basierend auf Modell und Jahr."""
    year = data.get("year", 0)
    title = data.get("title", "").lower()

    score = 50  # Basiswert

    if "facelift" in title or year >= 2018:
        score += 20
    if "diesel" in title:
        score -= 5
    if "elektro" in title or "hybrid" in title:
        score += 15

    demand_level = (
        "hoch" if score >= 70 else
        "mittel" if score >= 50 else
        "niedrig"
    )

    return {"score": score, "demand_level": demand_level}

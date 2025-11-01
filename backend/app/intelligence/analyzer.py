from app.intelligence.market_data import evaluate_market_value
from app.intelligence.weaknesses import get_weak_points
from app.intelligence.demand_predictor import predict_demand

def analyze_vehicle(data: dict) -> dict:
    """Verbindet technische, wirtschaftliche und marktspezifische Intelligenz."""
    base_info = {
        "platform": data.get("platform"),
        "title": data.get("title"),
        "year": data.get("year"),
        "price": data.get("price"),
        "mileage": data.get("mileage"),
    }

    market_eval = evaluate_market_value(data)
    demand = predict_demand(data)
    weaknesses = get_weak_points(data)

    return {
        "vehicle": base_info,
        "market": market_eval,
        "demand": demand,
        "weaknesses": weaknesses
    }

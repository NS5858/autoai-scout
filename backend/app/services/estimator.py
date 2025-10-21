from typing import Optional, Dict, Any
from app.schemas import ListingData, ValueEstimation

# Ein leichtgewichtiger, nachvollziehbarer Heuristik-Schätzer.
# Ziel: stabile Baseline, keine externen Abhängigkeiten, deterministisch.
# Idee: Startwert aus Angebotspreis, dann “Normalisierung” über Alter, km und Treibstoff/ Getriebe.

def estimate_value(listing: ListingData) -> ValueEstimation:
    v = listing.vehicle
    price = listing.price_eur or None

    # Defaults/Fallbacks
    year = v.year or 2015
    mileage = v.mileage_km or 120_000
    fuel = (v.fuel_type or "").lower()
    transm = (v.transmission or "").lower()

    # Altersfaktor: 1.0 bei 3 Jahren, -4% pro weiteres Jahr bis -40% max, +4% pro Jahr jünger bis +20%
    age = max(0, 2025 - year)
    if age <= 3:
        age_factor = 1.0 + 0.04 * (3 - age)
        age_factor = min(age_factor, 1.20)
    else:
        age_factor = 1.0 - 0.04 * (age - 3)
        age_factor = max(age_factor, 0.60)

    # Kilometerfaktor: 0–200k km → linear 1.15 … 0.70
    km = min(max(mileage, 0), 200_000)
    km_factor = 1.15 - 0.45 * (km / 200_000.0)

    # Fuel/Transmission Modifikatoren (vorsichtige Heuristiken)
    fuel_mod = {
        "diesel": 0.98,
        "benzin": 1.00,
        "hybrid": 1.03,
        "plugin": 1.04,
        "elektro": 1.01,
        "electric": 1.01,
    }
    transm_mod = 1.02 if "auto" in transm else 1.0

    f_factor = 1.0
    for key, val in fuel_mod.items():
        if key in fuel:
            f_factor = val
            break
    f_factor *= transm_mod

    # Wenn kein Preis existiert: Baseline annehmen (konservativ)
    base = price if price else 15_000.0

    est = base * age_factor * km_factor * f_factor

    # Konfidenzband (breit, da Heuristik)
    conf_low = est * 0.90
    conf_high = est * 1.10

    return ValueEstimation(
        method="heuristic_v1",
        estimated_value_eur=round(est, 2),
        conf_low_eur=round(conf_low, 2),
        conf_high_eur=round(conf_high, 2),
        notes="Heuristische Schätzung (deterministisch, keine externen Daten).",
        features_used={
            "input_price_eur": price,
            "year": year,
            "mileage_km": mileage,
            "fuel": fuel,
            "transmission": transm,
            "age_factor": round(age_factor, 3),
            "km_factor": round(km_factor, 3),
            "fuel_trans_factor": round(f_factor, 3),
        },
    )

# backend/app/services/pipeline.py
from app.intelligence.analyzer import analyze_vehicle

def run_analysis(data: dict) -> dict:
    """
    verbindet Parser-Daten mit der neuen KI-Intelligenz-Schicht (v2).
    Gibt eine strukturierte Analyse zurück:
    {
      "vehicle": {...},
      "market": {...},
      "demand": {...},
      "weaknesses": [...]
    }
    """
    return analyze_vehicle(data)

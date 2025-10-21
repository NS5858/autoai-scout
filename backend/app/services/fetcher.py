import requests

def fetch_html(url: str) -> str:
    """Holt HTML-Daten für Parser (optional, falls du später erweitern willst)."""
    headers = {"User-Agent": "Mozilla/5.0 (AutoAI Scout)"}
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code != 200:
        raise ConnectionError(f"Fehler beim Abrufen: {response.status_code}")
    return response.text

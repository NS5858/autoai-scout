import re

def parse(url: str) -> dict:
    """Extrahiert Basisdaten aus einem Autoscout24-Link."""
    try:
        pattern = r"autoscout24\.de/.*/([a-zA-Z0-9\-]+)-(\d+)"
        match = re.search(pattern, url)
        if not match:
            raise ValueError("Kein gültiges Autoscout24-Angebot erkannt.")
        
        title = match.group(1).replace("-", " ").title()
        fake_price = 20000 + len(title) * 10

        return {
            "platform": "AutoScout24",
            "title": title,
            "price": fake_price,
            "mileage": 85000,
            "year": 2018
        }

    except Exception as e:
        raise RuntimeError(f"Fehler beim Autoscout24-Parser: {e}")

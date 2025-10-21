from app.providers import autoscout24, mobile_de, ebay_kleinanzeigen

def parse_listing(url: str):
    """Erkennt automatisch die Plattform und ruft den passenden Parser auf."""
    try:
        if "autoscout24" in url:
            return autoscout24.parse(url)
        elif "mobile.de" in url:
            return mobile_de.parse(url)
        elif "ebay" in url or "kleinanzeigen" in url:
            return ebay_kleinanzeigen.parse(url)
        else:
            raise ValueError("Unbekannte Plattform oder ungültiger Link.")
    except Exception as e:
        raise RuntimeError(f"Fehler beim Parsen: {e}")

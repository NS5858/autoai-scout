import requests
from bs4 import BeautifulSoup


def extract_text_from_url(url: str) -> str:
    """
    Lädt eine Verkaufsseite (z. B. eBay Kleinanzeigen oder mobile.de),
    sucht nach Titel und Beschreibung und gibt einen zusammenhängenden Text zurück.
    """

    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/118.0 Safari/537.36"
            )
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Versuche gängige Felder für Titel / Beschreibung
        title = (
            soup.find("h1")
            or soup.find("title")
            or soup.find("meta", property="og:title")
        )
        description = (
            soup.find("div", {"class": "ad-description"})
            or soup.find("section", {"class": "description"})
            or soup.find("meta", property="og:description")
        )

        text_parts = []

        if title:
            # Meta-Tags liefern Attribut "content"
            if hasattr(title, "get_text"):
                text_parts.append(title.get_text(strip=True))
            else:
                text_parts.append(title.get("content", ""))

        if description:
            if hasattr(description, "get_text"):
                text_parts.append(description.get_text(strip=True))
            else:
                text_parts.append(description.get("content", ""))

        # Fallback: falls nichts gefunden wurde
        combined = " ".join(text_parts).strip()
        if not combined:
            combined = "Kein relevanter Text auf der Seite gefunden."

        return combined

    except Exception as e:
        return f"Fehler beim Laden oder Analysieren der URL: {e}"

import requests
from bs4 import BeautifulSoup


def extract_text_from_url(url: str) -> str:
    """
    Lädt eine Verkaufsseite (z. B. eBay Kleinanzeigen, mobile.de oder autoscout24.de),
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

        text_parts = []

        # ---- eBay Kleinanzeigen / Kleinanzeigen.de ----
        if "kleinanzeigen" in url or "ebay-kleinanzeigen" in url:
            title = soup.find("h1") or soup.find("title")
            description = soup.find("div", {"class": "ad-description"}) or soup.find("p")

            if title:
                text_parts.append(title.get_text(strip=True))
            if description:
                text_parts.append(description.get_text(strip=True))

        # ---- mobile.de ----
        elif "mobile.de" in url:
            title = soup.find("h1") or soup.find("title")
            description = soup.find("div", {"class": "cBox-body"}) or soup.find("div", {"class": "seller-cBox"})

            if title:
                text_parts.append(title.get_text(strip=True))
            if description:
                text_parts.append(description.get_text(strip=True))

        # ---- autoscout24.de ----
        elif "autoscout24" in url:
            title = soup.find("h1") or soup.find("title")
            description = soup.find("div", {"class": "cldt-description"}) or soup.find("p")

            if title:
                text_parts.append(title.get_text(strip=True))
            if description:
                text_parts.append(description.get_text(strip=True))

        # ---- Fallback für alle anderen Seiten ----
        else:
            title = soup.find("h1") or soup.find("title")
            meta_desc = soup.find("meta", property="og:description") or soup.find("meta", {"name": "description"})

            if title:
                text_parts.append(title.get_text(strip=True))
            if meta_desc:
                text_parts.append(meta_desc.get("content", "").strip())

        combined = " ".join(text_parts).strip()
        if not combined:
            combined = "Kein relevanter Text auf der Seite gefunden."

        # Kürzen, falls extrem lang
        return combined[:3000]

    except Exception as e:
        return f"Fehler beim Laden oder Analysieren der URL: {e}"

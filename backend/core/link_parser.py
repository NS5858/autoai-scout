import re
import json
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# =========================
# Helpers & HTTP Session
# =========================

def _make_session() -> requests.Session:
    """HTTP-Session mit Retry/Timeouts und Browser-Headern."""
    sess = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET", "HEAD"]),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retries, pool_maxsize=10)
    sess.mount("https://", adapter)
    sess.mount("http://", adapter)

    sess.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/118.0 Safari/537.36"
        ),
        "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    })
    return sess


def _clean_text(s: Optional[str]) -> str:
    if not s:
        return ""
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def _to_int(s: Optional[str]) -> Optional[int]:
    if not s:
        return None
    s = re.sub(r"[^\d]", "", s)
    return int(s) if s.isdigit() else None


def _parse_price(val: Any) -> Tuple[Optional[int], Optional[str]]:
    """Akzeptiert z. B. '13.500 €', 13500, {'price': 13500, 'priceCurrency': 'EUR'} …"""
    if val is None:
        return None, None
    if isinstance(val, (int, float)):
        return int(val), "EUR"
    if isinstance(val, dict):
        # JSON-LD Offer
        p = val.get("price") or val.get("priceSpecification", {}).get("price")
        cur = val.get("priceCurrency") or val.get("priceSpecification", {}).get("priceCurrency")
        try:
            p = int(float(p)) if p is not None else None
        except Exception:
            p = None
        return p, cur or "EUR"
    if isinstance(val, str):
        cur = "EUR" if "€" in val or "eur" in val.lower() else None
        p = _to_int(val)
        return p, cur
    return None, None


def _from_meta(soup: BeautifulSoup, prop: str, key: str = "content") -> Optional[str]:
    tag = soup.find("meta", { "property": prop }) or soup.find("meta", { "name": prop })
    return tag.get(key) if tag and tag.has_attr(key) else None


def _first(*values) -> Optional[str]:
    for v in values:
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def _extract_all_text(soup: BeautifulSoup, limit: int = 6000) -> str:
    """Fallback: gesamter sichtbarer Text."""
    for tag in soup(["script", "style", "noscript"]):
        tag.extract()
    text = " ".join(soup.stripped_strings)
    return _clean_text(text)[:limit]


def _json_loads_safe(s: str) -> Optional[Any]:
    try:
        return json.loads(s)
    except Exception:
        return None


# =========================
# Domain-spezifische Parser
# =========================

def _parse_json_ld(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """Alle JSON-LD-Objekte in der Seite extrahieren."""
    out: List[Dict[str, Any]] = []
    for script in soup.find_all("script", type="application/ld+json"):
        data = _json_loads_safe(script.text.strip())
        if not data:
            continue
        if isinstance(data, list):
            out.extend([d for d in data if isinstance(d, dict)])
        elif isinstance(data, dict):
            out.append(data)
    return out


def _parse_next_data(soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
    """Next.js __NEXT_DATA__ extrahieren (Autoscout24, teils mobile.de)."""
    node = soup.find("script", id="__NEXT_DATA__")
    return _json_loads_safe(node.text) if node else None


def _mobile_de_parser(soup: BeautifulSoup) -> Dict[str, Any]:
    # 1) JSON-LD versuchen
    listing: Dict[str, Any] = {}
    for obj in _parse_json_ld(soup):
        if obj.get("@type") in ("Vehicle", "Product"):
            listing["title"] = _first(obj.get("name"))
            # Preis
            offer = obj.get("offers") or {}
            price, cur = _parse_price(offer)
            listing["price"], listing["currency"] = price, cur
            # Beschreibung
            listing["description"] = _first(obj.get("description"))
            # Bilder
            imgs = obj.get("image")
            if isinstance(imgs, list):
                listing["images"] = [i for i in imgs if isinstance(i, str)]
            elif isinstance(imgs, str):
                listing["images"] = [imgs]

            # Fahrzeugspezifische Angaben
            veh = obj.get("vehicleConfiguration") or {}
            listing["mileage"] = _to_int(
                obj.get("mileageFromOdometer") or veh.get("mileageFromOdometer")
            )
            listing["first_registration"] = _first(
                obj.get("dateVehicleFirstRegistered"),
                obj.get("productionDate"),
                veh.get("dateVehicleFirstRegistered")
            )
            break

    # 2) DOM-Fallback
    if not listing.get("title"):
        listing["title"] = _first(
            _clean_text((soup.find("h1") or {}).get_text() if soup.find("h1") else ""),
            _from_meta(soup, "og:title"),
            soup.title.string if soup.title else None
        )

    if not listing.get("description"):
        cands = [
            soup.find("div", {"class": "cBox-body"}),
            soup.find("div", {"id": "vip-description"}),
        ]
        for c in cands:
            if c and _clean_text(c.get_text()):
                listing["description"] = _clean_text(c.get_text())
                break

    if not listing.get("price"):
        listing["price"], listing["currency"] = _parse_price(
            _first(_from_meta(soup, "product:price:amount"), _from_meta(soup, "og:price:amount"))
            or _from_meta(soup, "og:price")
            or (soup.find(text=re.compile(r"€")) or "")
        )

    if not listing.get("images"):
        ogimg = _from_meta(soup, "og:image")
        if ogimg:
            listing["images"] = [ogimg]

    return listing


def _autoscout24_parser(soup: BeautifulSoup) -> Dict[str, Any]:
    listing: Dict[str, Any] = {}

    # 1) Next.js JSON
    nx = _parse_next_data(soup)
    if nx:
        try:
            # Struktur kann variieren: Pfad zur Fahrzeugbeschreibung suchen
            props = nx.get("props", {})
            page_props = props.get("pageProps", {})
            data = page_props.get("listing", {}) or page_props.get("initialState", {})
            # Heuristik: häufig gibt es 'title', 'price', 'images' etc. an unterschiedlichen Stellen.
            title = data.get("title") or data.get("vehicle", {}).get("title")
            price = data.get("price") or data.get("vehicle", {}).get("price")
            images = data.get("images") or data.get("media", {}).get("images", [])
            desc = (
                data.get("description")
                or data.get("vehicle", {}).get("description")
                or page_props.get("description")
            )

            p, cur = _parse_price(price)
            listing.update({
                "title": _clean_text(title),
                "description": _clean_text(desc),
                "price": p,
                "currency": cur or "EUR",
                "images": [i.get("url") if isinstance(i, dict) else i for i in images if i],
            })
        except Exception:
            pass

    # 2) JSON-LD
    if not listing.get("title"):
        for obj in _parse_json_ld(soup):
            if obj.get("@type") in ("Vehicle", "Product"):
                listing["title"] = _first(obj.get("name"))
                offer = obj.get("offers") or {}
                p, cur = _parse_price(offer)
                listing["price"], listing["currency"] = p, cur
                listing["description"] = _first(obj.get("description"))
                imgs = obj.get("image")
                if isinstance(imgs, list):
                    listing["images"] = [i for i in imgs if isinstance(i, str)]
                elif isinstance(imgs, str):
                    listing["images"] = [imgs]
                break

    # 3) DOM-Fallback
    if not listing.get("title"):
        listing["title"] = _first(
            _clean_text((soup.find("h1") or {}).get_text() if soup.find("h1") else ""),
            _from_meta(soup, "og:title"), soup.title.string if soup.title else None
        )
    if not listing.get("description"):
        cand = soup.find("div", {"class": re.compile("description", re.I)}) or soup.find("p")
        if cand:
            listing["description"] = _clean_text(cand.get_text())

    if not listing.get("price"):
        listing["price"], listing["currency"] = _parse_price(
            _first(_from_meta(soup, "product:price:amount"), _from_meta(soup, "og:price:amount"))
            or _from_meta(soup, "og:price") or (soup.find(text=re.compile(r"€")) or "")
        )

    if not listing.get("images"):
        ogimg = _from_meta(soup, "og:image")
        if ogimg:
            listing["images"] = [ogimg]

    return listing


def _kleinanzeigen_parser(soup: BeautifulSoup) -> Dict[str, Any]:
    listing: Dict[str, Any] = {}

    # 1) JSON-LD (falls vorhanden)
    for obj in _parse_json_ld(soup):
        if obj.get("@type") in ("Product", "Offer"):
            listing["title"] = _first(obj.get("name"))
            p, cur = _parse_price(obj.get("offers") or obj)
            listing["price"], listing["currency"] = p, cur
            listing["description"] = _first(obj.get("description"))
            imgs = obj.get("image")
            if isinstance(imgs, list):
                listing["images"] = [i for i in imgs if isinstance(i, str)]
            elif isinstance(imgs, str):
                listing["images"] = [imgs]
            break

    # 2) DOM-Selektoren
    if not listing.get("title"):
        h1 = soup.find("h1") or soup.find("h1", {"id": "viewad-title"})
        listing["title"] = _clean_text(h1.get_text()) if h1 else _from_meta(soup, "og:title")

    if not listing.get("description"):
        desc = soup.find("div", {"class": "ad-description"}) \
            or soup.find("div", {"id": "viewad-description"}) \
            or soup.find("section", {"class": "description"})
        if desc:
            listing["description"] = _clean_text(desc.get_text())

    if not listing.get("price"):
        price_node = soup.find("meta", {"property": "product:price:amount"}) \
            or soup.find("meta", {"name": "product:price:amount"})
        if price_node:
            p, cur = _parse_price(price_node.get("content", ""))
            listing["price"], listing["currency"] = p, cur or "EUR"
        else:
            # Fallback: Textsuche
            listing["price"], listing["currency"] = _parse_price(
                (soup.find(text=re.compile(r"€")) or "")
            )

    if not listing.get("images"):
        ogimg = _from_meta(soup, "og:image")
        if ogimg:
            listing["images"] = [ogimg]

    return listing


# =========================
# Public API
# =========================

def extract_listing(url: str) -> Dict[str, Any]:
    """
    Holt strukturiert Infos (title, description, price, currency, mileage, first_registration,
    power, fuel, transmission, location, images, seller, combined_text, url, domain).
    """
    session = _make_session()
    try:
        resp = session.get(url, timeout=12)
        resp.raise_for_status()
    except Exception as e:
        return {
            "url": url,
            "domain": urlparse(url).netloc,
            "error": f"Fehler beim Laden: {e}",
            "combined_text": ""
        }

    soup = BeautifulSoup(resp.text, "html.parser")
    domain = urlparse(url).netloc

    # Domain-Router
    if "mobile.de" in domain:
        listing = _mobile_de_parser(soup)
    elif "autoscout24" in domain:
        listing = _autoscout24_parser(soup)
    elif "kleinanzeigen" in domain or "ebay-kleinanzeigen" in domain:
        listing = _kleinanzeigen_parser(soup)
    else:
        # generischer Fallback
        listing = {
            "title": _first(_from_meta(soup, "og:title"), soup.title.string if soup.title else None),
            "description": _first(_from_meta(soup, "og:description"), _from_meta(soup, "description")),
            "price": _parse_price(_from_meta(soup, "product:price:amount"))[0],
            "currency": "EUR",
            "images": [_from_meta(soup, "og:image")] if _from_meta(soup, "og:image") else [],
        }

    # Normalisierung & Combined Text
    title = _clean_text(listing.get("title"))
    desc = _clean_text(listing.get("description"))
    price = listing.get("price")
    currency = listing.get("currency") or "EUR"

    # combined_text → ideal für deine /analyze-Logik
    parts = [
        title,
        desc,
        f"Preis: {price} {currency}" if price else "",
    ]
    combined_text = _clean_text(" | ".join([p for p in parts if p]))

    listing.update({
        "url": url,
        "domain": domain,
        "title": title,
        "description": desc,
        "price": price,
        "currency": currency,
        "images": listing.get("images", []),
        "combined_text": combined_text or _extract_all_text(soup, limit=4000),
    })
    return listing


def extract_text_from_url(url: str) -> str:
    """
    Kompatibilitätsfunktion zu deiner bestehenden /analyze-Pipeline.
    Nutzt extract_listing() und liefert combined_text zurück.
    """
    try:
        data = extract_listing(url)
        if data.get("error"):
            # Falls die Seite geblockt/leer ist, trotzdem irgendeinen Text liefern
            return f"{data.get('title') or ''} {data.get('description') or ''}".strip() or data["error"]
        return data.get("combined_text") or f"{data.get('title', '')} {data.get('description', '')}".strip()
    except Exception as e:
        return f"Fehler beim Laden oder Analysieren der URL: {e}"

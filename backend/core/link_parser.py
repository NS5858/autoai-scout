import re
import json
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# =========================
# HTTP Session & Utils
# =========================

def _make_session() -> requests.Session:
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
    """
    Akzeptiert:
    - 13500 / 13500.0
    - "13.500 €"
    - {"price": 13500, "priceCurrency": "EUR"}
    """
    if val is None:
        return None, None
    if isinstance(val, (int, float)):
        return int(val), "EUR"
    if isinstance(val, dict):
        p = val.get("price") or val.get("priceSpecification", {}).get("price")
        cur = val.get("priceCurrency") or val.get("priceSpecification", {}).get("priceCurrency")
        try:
            p = int(float(p)) if p is not None else None
        except Exception:
            p = None
        return p, (cur or "EUR")
    if isinstance(val, str):
        cur = "EUR" if ("€" in val or "eur" in val.lower()) else None
        p = _to_int(val)
        return p, cur
    return None, None


def _from_meta(soup: BeautifulSoup, prop: str, key: str = "content") -> Optional[str]:
    tag = soup.find("meta", {"property": prop}) or soup.find("meta", {"name": prop})
    return tag.get(key) if tag and tag.has_attr(key) else None


def _first(*vals) -> Optional[str]:
    for v in vals:
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def _json_loads_safe(s: str) -> Optional[Any]:
    try:
        return json.loads(s)
    except Exception:
        return None


def _extract_all_text(soup: BeautifulSoup, limit: int = 6000) -> str:
    for tag in soup(["script", "style", "noscript"]):
        tag.extract()
    text = " ".join(soup.stripped_strings)
    return _clean_text(text)[:limit]


# =========================
# Structured data helpers
# =========================

def _parse_json_ld(soup: BeautifulSoup) -> List[Dict[str, Any]]:
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
    node = soup.find("script", id="__NEXT_DATA__")
    return _json_loads_safe(node.text) if node else None


# =========================
# Normalization helpers
# =========================

BRANDS = [
    "alfa romeo","alpina","aston martin","audi","bentley","bmw","bugatti","cadillac",
    "chevrolet","chrysler","citroen","cupra","dacia","daewoo","daihatsu","dodge","ds",
    "ferrari","fiat","ford","honda","hyundai","infiniti","isuzu","iveco","jaguar","jeep",
    "kia","ktm","lamborghini","lancia","land rover","lexus","lotus","maserati","mazda",
    "mclaren","mercedes","mercedes-benz","mini","mitsubishi","nissan","opel","peugeot",
    "polestar","pontiac","porsche","renault","rolls-royce","rover","saab","seat",
    "skoda","smart","ssangyong","subaru","suzuki","tesla","toyota","trabant","volkswagen","vw","volvo"
]

# kleine Modell-Hinweise (erweiterbar)
MODEL_HINTS = [
    r"[ac] ?\d{2,3}", r"[bde] ?\d{2,3}", r"[sg] ?\d{2,3}",
    r"[a-z]{1,2}\d{2,3}", r"\d{3,4}[a-z]{0,2}", r"golf ?\d", r"focus", r"corsa", r"passat", r"panda"
]

def _detect_brand(text: str) -> Optional[str]:
    t = text.lower()
    for b in BRANDS:
        if b in t:
            # normalisieren mercedes→mercedes-benz
            if b == "mercedes":
                return "mercedes-benz"
            if b == "vw":
                return "volkswagen"
            return b
    return None

def _detect_model(text: str) -> Optional[str]:
    t = text.lower()
    for pat in MODEL_HINTS:
        m = re.search(rf"\b({pat})\b", t, re.I)
        if m:
            return m.group(1)
    return None

def _detect_year(text: str) -> Optional[int]:
    # EZ 2015, Bj. 2014, etc.
    m = re.search(r"(?:ez|bj|baujahr|erstzulassung)[^\d]{0,10}(\d{4})", text, re.I)
    if m:
        y = int(m.group(1))
        if 1950 <= y <= 2030:
            return y
    # generischer 4-stelliger Jahrtreffer (vorsichtig)
    m2 = re.search(r"\b(19[5-9]\d|20[0-2]\d)\b", text)
    if m2:
        return int(m2.group(1))
    return None

def _detect_km(text: str) -> Optional[int]:
    m = re.search(r"(\d{1,3}(?:[.\s]\d{3})+|\d{4,6})\s*(?:km|kilometer)", text, re.I)
    if m:
        return _to_int(m.group(1))
    return None

def _detect_power(text: str) -> Tuple[Optional[int], Optional[int]]:
    # 125 kW (170 PS) | 170 PS | 125 kW
    kw = None
    ps = None
    m_kw = re.search(r"(\d{2,3})\s*kW", text, re.I)
    if m_kw:
        kw = int(m_kw.group(1))
        ps = int(round(kw * 1.35962))
        return kw, ps
    m_ps = re.search(r"(\d{2,3})\s*PS", text, re.I)
    if m_ps:
        ps = int(m_ps.group(1))
        kw = int(round(ps / 1.35962))
        return kw, ps
    return None, None

def _detect_fuel(text: str) -> Optional[str]:
    t = text.lower()
    if "diesel" in t: return "Diesel"
    if "benzin" in t or "otto" in t or "super" in t: return "Benzin"
    if "hybrid" in t: return "Hybrid"
    if "elektro" in t or "electric" in t or "bev" in t: return "Elektro"
    if "lpg" in t or "autogas" in t or "gas" in t: return "LPG/Autogas"
    if "cng" in t or "erdgas" in t: return "CNG/Erdgas"
    return None

def _detect_transmission(text: str) -> Optional[str]:
    t = text.lower()
    if "automatik" in t or "automatic" in t or "dsg" in t: return "Automatik"
    if "schalt" in t or "manuell" in t or "hand" in t: return "Schaltgetriebe"
    return None


# =========================
# Domain Parser
# =========================

def _mobile_de_parser(soup: BeautifulSoup) -> Dict[str, Any]:
    listing: Dict[str, Any] = {}
    # JSON-LD
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

    # DOM fallback
    if not listing.get("title"):
        listing["title"] = _first(
            _clean_text((soup.find("h1") or {}).get_text() if soup.find("h1") else ""),
            _from_meta(soup, "og:title"),
            soup.title.string if soup.title else None,
        )
    if not listing.get("description"):
        cands = [
            soup.find("div", {"class": "cBox-body"}),
            soup.find("div", {"id": "vip-description"}),
        ]
        for c in cands:
            if c:
                text = _clean_text(c.get_text())
                if text:
                    listing["description"] = text
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
    nx = _parse_next_data(soup)
    if nx:
        try:
            props = nx.get("props", {})
            page_props = props.get("pageProps", {})
            data = page_props.get("listing", {}) or page_props.get("initialState", {})
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
                "price": p, "currency": cur or "EUR",
                "images": [i.get("url") if isinstance(i, dict) else i for i in images if i],
            })
        except Exception:
            pass

    if not listing.get("title"):
        for obj in _parse_json_ld(soup):
            if obj.get("@type") in ("Vehicle", "Product"):
                listing["title"] = _first(obj.get("name"))
                p, cur = _parse_price(obj.get("offers") or {})
                listing["price"], listing["currency"] = p, cur
                listing["description"] = _first(obj.get("description"))
                imgs = obj.get("image")
                if isinstance(imgs, list):
                    listing["images"] = [i for i in imgs if isinstance(i, str)]
                elif isinstance(imgs, str):
                    listing["images"] = [imgs]
                break

    if not listing.get("title"):
        listing["title"] = _first(
            _clean_text((soup.find("h1") or {}).get_text() if soup.find("h1") else ""),
            _from_meta(soup, "og:title"),
            soup.title.string if soup.title else None,
        )
    if not listing.get("description"):
        cand = soup.find("div", {"class": re.compile("description", re.I)}) or soup.find("p")
        if cand:
            listing["description"] = _clean_text(cand.get_text())
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


def _kleinanzeigen_parser(soup: BeautifulSoup) -> Dict[str, Any]:
    listing: Dict[str, Any] = {}
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

    if not listing.get("title"):
        h1 = soup.find("h1") or soup.find("h1", {"id": "viewad-title"})
        listing["title"] = _clean_text(h1.get_text()) if h1 else _from_meta(soup, "og:title")
    if not listing.get("description"):
        desc = (
            soup.find("div", {"class": "ad-description"})
            or soup.find("div", {"id": "viewad-description"})
            or soup.find("section", {"class": "description"})
        )
        if desc:
            listing["description"] = _clean_text(desc.get_text())
    if not listing.get("price"):
        price_node = soup.find("meta", {"property": "product:price:amount"}) \
            or soup.find("meta", {"name": "product:price:amount"})
        if price_node:
            p, cur = _parse_price(price_node.get("content", ""))
            listing["price"], listing["currency"] = p, cur or "EUR"
        else:
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
    Liefert strukturierte Felder + combined_text:
    brand, model, year, mileage, fuel, power_kw, power_ps, transmission,
    price, currency, title, description, images, domain, url, combined_text, error?.
    """
    session = _make_session()
    domain = urlparse(url).netloc

    try:
        resp = session.get(url, timeout=12)
        resp.raise_for_status()
    except Exception as e:
        return {
            "url": url,
            "domain": domain,
            "error": f"Fehler beim Laden: {e}",
            "title": "",
            "description": "",
            "price": None,
            "currency": None,
            "images": [],
            "combined_text": "",
        }

    soup = BeautifulSoup(resp.text, "html.parser")

    # 1) Domain-spezifisch
    if "mobile.de" in domain:
        base = _mobile_de_parser(soup)
    elif "autoscout24" in domain:
        base = _autoscout24_parser(soup)
    elif "kleinanzeigen" in domain or "ebay-kleinanzeigen" in domain:
        base = _kleinanzeigen_parser(soup)
    else:
        base = {
            "title": _first(_from_meta(soup, "og:title"), soup.title.string if soup.title else None),
            "description": _first(_from_meta(soup, "og:description"), _from_meta(soup, "description")),
            "price": _parse_price(_from_meta(soup, "product:price:amount"))[0],
            "currency": "EUR",
            "images": [_from_meta(soup, "og:image")] if _from_meta(soup, "og:image") else [],
        }

    title = _clean_text(base.get("title"))
    description = _clean_text(base.get("description"))
    price = base.get("price")
    currency = base.get("currency") or ("EUR" if price else None)
    images = base.get("images", []) or []

    # 2) Intelligent normalisieren
    text_for_nlp = f"{title} | {description}"
    brand = _detect_brand(text_for_nlp) or _detect_brand(_extract_all_text(soup, limit=2000))
    model = _detect_model(text_for_nlp)
    year = _detect_year(text_for_nlp)
    mileage = _detect_km(text_for_nlp)
    power_kw, power_ps = _detect_power(text_for_nlp)
    fuel = _detect_fuel(text_for_nlp)
    transmission = _detect_transmission(text_for_nlp)

    # 3) Combined text für deine Heuristik
    parts = [
        title,
        description,
        f"Preis: {price} {currency}" if price else "",
        f"Kilometer: {mileage}" if mileage else "",
        f"Baujahr: {year}" if year else "",
        f"Leistung: {power_kw} kW ({power_ps} PS)" if (power_kw or power_ps) else "",
        f"Kraftstoff: {fuel}" if fuel else "",
        f"Getriebe: {transmission}" if transmission else "",
    ]
    combined_text = _clean_text(" | ".join([p for p in parts if p])) or _extract_all_text(soup, limit=4000)

    return {
        "url": url,
        "domain": domain,
        "title": title,
        "description": description,
        "price": price,
        "currency": currency,
        "images": images,
        "brand": brand,
        "model": model,
        "year": year,
        "mileage": mileage,
        "power_kw": power_kw,
        "power_ps": power_ps,
        "fuel": fuel,
        "transmission": transmission,
        "combined_text": combined_text,
    }


def extract_text_from_url(url: str) -> str:
    """
    Kompatibilität zur bestehenden /analyze-Route:
    liefert den besten Text für deine Heuristik.
    """
    data = extract_listing(url)
    if data.get("error"):
        return data["error"]
    return data.get("combined_text") or f"{data.get('title','')} {data.get('description','')}".strip()

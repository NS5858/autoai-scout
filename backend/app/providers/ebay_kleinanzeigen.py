from typing import Any, Dict, Optional, List
from selectolax.parser import HTMLParser
from app.providers.base import Provider
from app.schemas import ListingData, ListingVehicle, ListingSeller, ListingImage

class EbayKleinanzeigenProvider(Provider):
    domain = "ebay-kleinanzeigen"

    def extract(self, url: str, html: str, prefer_lang: str = "de") -> ListingData:
        tree = HTMLParser(html)
        title = _meta(tree, "og:title")
        desc = _meta(tree, "og:description")
        img = _meta(tree, "og:image")
        price = _price_from_text(desc) or _price_from_text(title)

        vehicle = ListingVehicle(
            make=_kv(tree, "Marke"),
            model=_kv(tree, "Modell"),
            year=_int(_kv(tree, "Erstzulassung")),
            mileage_km=_int(_kv(tree, "Kilometerstand")),
            fuel_type=_kv(tree, "Kraftstoffart"),
            transmission=_kv(tree, "Getriebe"),
            power_kw=_int(_kv(tree, "Leistung")),
            body_type=_kv(tree, "Fahrzeugtyp"),
            color=_kv(tree, "Farbe"),
        )

        seller = ListingSeller(
            name=_seller_name(tree),
            type="private",
            location=_kv(tree, "PLZ") or _kv(tree, "Ort"),
        )

        images = []
        if img:
            try:
                images.append(ListingImage(url=img))
            except Exception:
                pass

        return ListingData(
            url=url,
            domain=self.domain,
            title=title,
            price_eur=price,
            description=desc,
            vehicle=vehicle,
            seller=seller,
            images=images,
            raw={"note": "Parsed from OGP + attribute table"},
        )

def _meta(tree: HTMLParser, prop: str) -> Optional[str]:
    n = tree.css_first(f'meta[property="{prop}"]')
    return n.attributes.get("content") if n else None

def _kv(tree: HTMLParser, label: str) -> Optional[str]:
    # Sucht in Detailtabellen nach Labeln (robust-ish)
    for row in tree.css("dl, table, ul li"):
        txt = row.text(separator=" ", strip=True)
        if label.lower() in txt.lower():
            parts = txt.split(":")
            if len(parts) > 1:
                return parts[1].strip()
    return None

def _seller_name(tree: HTMLParser) -> Optional[str]:
    n = tree.css_first('[data-testid="user-profile-link"]') or tree.css_first(".userprofile-about-me h2")
    return n.text(strip=True) if n else None

def _int(s: Optional[str]) -> Optional[int]:
    if not s:
        return None
    import re
    m = re.search(r"(\d{4})", s)
    if m:
        return int(m.group(1))
    m2 = re.search(r"(\d[\d\.]*)", s)
    if m2:
        try:
            return int(m2.group(1).replace(".", ""))
        except Exception:
            return None
    return None

def _price_from_text(s: Optional[str]) -> Optional[float]:
    if not s:
        return None
    import re
    m = re.search(r"([\d\.]{1,3}(?:\.\d{3})*(?:,\d{1,2})?)\s*€", s)
    if not m:
        return None
    try:
        return float(m.group(1).replace(".", "").replace(",", "."))
    except Exception:
        return None

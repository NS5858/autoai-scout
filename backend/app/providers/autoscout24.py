from typing import Any, Dict, Optional, List
from selectolax.parser import HTMLParser
from app.providers.base import Provider
from app.services.jsonld import extract_jsonld
from app.schemas import ListingData, ListingVehicle, ListingSeller, ListingImage

class AutoScoutProvider(Provider):
    domain = "autoscout24"

    def extract(self, url: str, html: str, prefer_lang: str = "de") -> ListingData:
        tree = HTMLParser(html)
        ld = self._from_jsonld(html) or {}
        title = ld.get("name") or self._og(tree, "og:title")
        price_eur = self._price_eur(ld) or self._price_from_html(tree)

        vehicle = ListingVehicle(
            make=_s(ld, "brand.name") or _s(ld, "brand"),
            model=_s(ld, "model"),
            year=_i(ld, "vehicleModelDate") or _i(ld, "productionDate"),
            mileage_km=_i(ld, "mileageFromOdometer.value"),
            fuel_type=_s(ld, "fuelType"),
            transmission=_s(ld, "vehicleTransmission"),
            power_kw=_i(ld, "power"),
            body_type=_s(ld, "bodyType"),
            color=_s(ld, "color"),
        )

        seller = ListingSeller(
            name=_s(ld, "seller.name"),
            type=_s(ld, "seller.@type"),
            location=_s(ld, "seller.address.addressLocality"),
            phone=None,
        )

        images = self._images(ld, tree)

        return ListingData(
            url=url,
            domain=self.domain,
            title=title,
            price_eur=price_eur,
            description=ld.get("description") or self._og(tree, "og:description"),
            vehicle=vehicle,
            seller=seller,
            images=images,
            raw={"jsonld": ld},
        )

    def _from_jsonld(self, html: str) -> Optional[Dict[str, Any]]:
        blocks = extract_jsonld(html)
        # Suche Vehicle/Offer Strukturen
        for b in blocks:
            if b.get("@type") in ("Product", "Vehicle", "Car"):
                return b
            # verschachtelt in "offers" etc.
            if "offers" in b and isinstance(b["offers"], dict):
                return b
        return None

    def _og(self, tree: HTMLParser, prop: str) -> Optional[str]:
        node = tree.css_first(f'meta[property="{prop}"]')
        return node.attributes.get("content") if node else None

    def _price_eur(self, ld: Dict[str, Any]) -> Optional[float]:
        offers = ld.get("offers") if isinstance(ld.get("offers"), dict) else None
        price = offers.get("price") if offers else ld.get("price")
        currency = offers.get("priceCurrency") if offers else ld.get("priceCurrency")
        if price is None:
            return None
        try:
            val = float(str(price).replace(".", "").replace(",", "."))
            if not currency or currency.upper() == "EUR":
                return val
            return val  # naive: Währungsumrechnung weggelassen
        except Exception:
            return None

    def _price_from_html(self, tree: HTMLParser) -> Optional[float]:
        # Fallback: suche nach data-testid / Preisblöcken
        candidates = []
        for n in tree.css("[data-testid*=price]"):
            txt = n.text(strip=True)
            candidates.append(txt)
        for txt in candidates:
            val = _parse_price(txt)
            if val:
                return val
        return None

    def _images(self, ld: Dict[str, Any], tree: HTMLParser) -> List[ListingImage]:
        out: List[ListingImage] = []
        imgs = ld.get("image")
        if isinstance(imgs, list):
            for u in imgs:
                try:
                    out.append(ListingImage(url=u))
                except Exception:
                    continue
        elif isinstance(imgs, str):
            try:
                out.append(ListingImage(url=imgs))
            except Exception:
                pass
        if not out:
            og = self._og(tree, "og:image")
            if og:
                try:
                    out.append(ListingImage(url=og))
                except Exception:
                    pass
        return out

def _s(d: Dict[str, Any], path: str) -> Optional[str]:
    cur: Any = d
    for p in path.split("."):
        if not isinstance(cur, dict) or p not in cur:
            return None
        cur = cur[p]
    return str(cur) if cur is not None else None

def _i(d: Dict[str, Any], path: str) -> Optional[int]:
    val = _s(d, path)
    if val is None:
        return None
    try:
        return int(str(val).split(".")[0])
    except Exception:
        return None

def _parse_price(txt: str) -> Optional[float]:
    import re
    m = re.search(r"([\d\.]{1,3}(?:\.\d{3})*(?:,\d{1,2})?)\s*€", txt)
    if not m:
        return None
    val = m.group(1).replace(".", "").replace(",", ".")
    try:
        return float(val)
    except Exception:
        return None

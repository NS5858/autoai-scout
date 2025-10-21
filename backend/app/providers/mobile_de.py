from typing import Any, Dict, Optional, List
from selectolax.parser import HTMLParser
from app.providers.base import Provider
from app.services.jsonld import extract_jsonld
from app.schemas import ListingData, ListingVehicle, ListingSeller, ListingImage

class MobileDEProvider(Provider):
    domain = "mobile"

    def extract(self, url: str, html: str, prefer_lang: str = "de") -> ListingData:
        tree = HTMLParser(html)
        ld = self._best_jsonld(html) or {}
        title = ld.get("name") or self._og(tree, "og:title")

        price_eur = self._price_eur(ld) or self._price_from_html(tree)

        vehicle = ListingVehicle(
            make=_s(ld, "brand.name") or _s(ld, "brand"),
            model=_s(ld, "model"),
            year=_i(ld, "vehicleModelDate"),
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
        )

        images = []
        og = self._og(tree, "og:image")
        if og:
            try:
                images.append(ListingImage(url=og))
            except Exception:
                pass

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

    def _best_jsonld(self, html: str) -> Optional[Dict[str, Any]]:
        for b in extract_jsonld(html):
            t = b.get("@type")
            if t in ("Product", "Vehicle", "Car"):
                return b
        return None

    def _og(self, tree: HTMLParser, prop: str) -> Optional[str]:
        node = tree.css_first(f'meta[property="{prop}"]')
        return node.attributes.get("content") if node else None

    def _price_eur(self, ld: Dict[str, Any]) -> Optional[float]:
        offers = ld.get("offers") if isinstance(ld.get("offers"), dict) else None
        price = offers.get("price") if offers else ld.get("price")
        if price is None:
            return None
        try:
            return float(str(price).replace(".", "").replace(",", "."))
        except Exception:
            return None

    def _price_from_html(self, tree: HTMLParser) -> Optional[float]:
        # Sehr einfacher Fallback
        n = tree.css_first('meta[itemprop="price"]')
        if n and n.attributes.get("content"):
            try:
                return float(n.attributes["content"])
            except Exception:
                return None
        return None

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

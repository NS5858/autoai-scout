from typing import Optional, List
from selectolax.parser import HTMLParser
from app.providers.base import Provider
from app.schemas import ListingData, ListingVehicle, ListingSeller, ListingImage

class GenericProvider(Provider):
    domain = "generic"

    def extract(self, url: str, html: str, prefer_lang: str = "de") -> ListingData:
        tree = HTMLParser(html)
        title = _meta(tree, "og:title") or (tree.css_first("title").text() if tree.css_first("title") else None)
        desc = _meta(tree, "og:description")
        img = _meta(tree, "og:image")

        images: List[ListingImage] = []
        if img:
            try:
                images.append(ListingImage(url=img))
            except Exception:
                pass

        # Keine Annahmen: generisch, minimale Felder
        return ListingData(
            url=url,
            domain=self.domain,
            title=title,
            price_eur=None,
            description=desc,
            vehicle=ListingVehicle(),
            seller=ListingSeller(),
            images=images,
            raw={"note": "Generic OGP fallback"},
        )

def _meta(tree: HTMLParser, prop: str) -> Optional[str]:
    n = tree.css_first(f'meta[property="{prop}"]')
    return n.attributes.get("content") if n else None

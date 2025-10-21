from typing import Dict, Type
from app.providers.base import Provider
from app.providers.generic import GenericProvider
from app.providers.autoscout24 import AutoScoutProvider
from app.providers.mobile_de import MobileDEProvider
from app.providers.ebay_kleinanzeigen import EbayKleinanzeigenProvider

_REGISTRY: Dict[str, Provider] = {
    "autoscout24": AutoScoutProvider(),
    "mobile": MobileDEProvider(),          # tldextract gibt "mobile" für mobile.de
    "ebay-kleinanzeigen": EbayKleinanzeigenProvider(),
}

_GENERIC = GenericProvider()

def get_provider(domain_key: str) -> Provider:
    return _REGISTRY.get(domain_key, _GENERIC)

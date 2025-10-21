from abc import ABC, abstractmethod
from typing import Optional
from app.schemas import ListingData

class Provider(ABC):
    domain: str = "generic"

    @abstractmethod
    def extract(self, url: str, html: str, prefer_lang: str = "de") -> ListingData:
        ...

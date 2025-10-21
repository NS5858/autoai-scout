from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Dict, Any

class HealthResponse(BaseModel):
    status: str
    service: str

class ListingImage(BaseModel):
    url: HttpUrl
    width: Optional[int] = None
    height: Optional[int] = None

class ListingVehicle(BaseModel):
    make: Optional[str] = None
    model: Optional[str] = None
    trim: Optional[str] = None
    year: Optional[int] = None
    mileage_km: Optional[int] = None
    power_kw: Optional[int] = None
    fuel_type: Optional[str] = None
    transmission: Optional[str] = None
    vin: Optional[str] = None
    body_type: Optional[str] = None
    doors: Optional[int] = None
    color: Optional[str] = None
    owners: Optional[int] = None
    emission_class: Optional[str] = None
    consumption_l_100km: Optional[float] = None

class ListingSeller(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None  # private | dealer
    phone: Optional[str] = None
    location: Optional[str] = None

class ListingData(BaseModel):
    url: HttpUrl
    domain: str
    title: Optional[str] = None
    price_eur: Optional[float] = None
    currency: Optional[str] = "EUR"
    description: Optional[str] = None
    vehicle: ListingVehicle = ListingVehicle()
    seller: ListingSeller = ListingSeller()
    images: List[ListingImage] = Field(default_factory=list)
    raw: Dict[str, Any] = Field(default_factory=dict)

class ValueEstimation(BaseModel):
    method: str
    estimated_value_eur: Optional[float] = None
    conf_low_eur: Optional[float] = None
    conf_high_eur: Optional[float] = None
    notes: Optional[str] = None
    features_used: Dict[str, Any] = Field(default_factory=dict)

class AnalyzeRequest(BaseModel):
    url: HttpUrl
    prefer_lang: Optional[str] = "de"

class AnalyzeResponse(BaseModel):
    listing: ListingData
    valuation: ValueEstimation

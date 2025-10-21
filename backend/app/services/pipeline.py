from fastapi import HTTPException
from app.link_parser import normalize_url, domain_key
from app.providers.registry import get_provider
from app.services.fetcher import fetch_html
from app.services.estimator import estimate_value
from app.schemas import AnalyzeResponse

async def analyze(url: str, prefer_lang: str = "de") -> AnalyzeResponse:
    url = normalize_url(url)
    dom = domain_key(url)
    provider = get_provider(dom)

    html = await fetch_html(url)
    listing = provider.extract(url, html, prefer_lang=prefer_lang)

    if not listing or listing.url is None:
        raise HTTPException(status_code=422, detail="Parsing failed for this URL.")

    valuation = estimate_value(listing)
    return AnalyzeResponse(listing=listing, valuation=valuation)

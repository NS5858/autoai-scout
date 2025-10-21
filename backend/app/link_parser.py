import tldextract
from urllib.parse import urlparse, urlunparse

def normalize_url(url: str) -> str:
    p = urlparse(url)
    scheme = p.scheme or "https"
    netloc = p.netloc.lower()
    path = p.path
    query = p.query
    return urlunparse((scheme, netloc, path, "", query, ""))

def domain_key(url: str) -> str:
    ext = tldextract.extract(url)
    # e.g. autoscout24.de -> autoscout24
    return ext.domain.lower()

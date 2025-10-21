import httpx
from app.config import USER_AGENT, HTTP_TIMEOUT, HTTP_MAX_BYTES

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
}

async def fetch_html(url: str) -> str:
    limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
    async with httpx.AsyncClient(
        headers=HEADERS, timeout=HTTP_TIMEOUT, limits=limits, follow_redirects=True
    ) as client:
        r = await client.get(url)
        r.raise_for_status()
        content = r.content[:HTTP_MAX_BYTES]
        return content.decode(r.encoding or "utf-8", errors="ignore")

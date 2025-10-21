import os

USER_AGENT = os.getenv(
    "AUTOAI_UA",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36 AutoAI-Scout"
)
HTTP_TIMEOUT = float(os.getenv("AUTOAI_HTTP_TIMEOUT", "15"))
HTTP_MAX_BYTES = int(os.getenv("AUTOAI_HTTP_MAX_BYTES", "2_500_000"))

# NomadShare - URL Shortener Service (external API)

import logging
import requests
from app.config import SHORTLINK_URL, SHORTLINK_API

logger = logging.getLogger(__name__)


async def shorten(long_url: str) -> str:
    """Shorten a URL via the configured shortener API. Falls back to the long URL."""
    if not SHORTLINK_URL or not SHORTLINK_API:
        return long_url

    try:
        response = requests.get(
            f"https://{SHORTLINK_URL}/api",
            params={"api": SHORTLINK_API, "url": long_url},
            timeout=10,
        )
        if response.status_code == 200:
            return response.text.strip()
        logger.warning(f"Failed to shorten URL: {response.status_code}")
        return long_url
    except Exception as e:
        logger.error(f"Error shortening URL: {e}")
        return long_url

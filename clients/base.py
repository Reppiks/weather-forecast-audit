from typing import Any

import httpx

DEFAULT_TIMEOUT = 10.0


class APIError(Exception):
    """Custom exception raised when an Open-Meteo API call fails"""


async def make_request(
    client: httpx.AsyncClient, url: str, params: dict[str, Any]
) -> dict[str, Any]:
    """Executes an async GET request using a shared AsyncClient.

    Handles timeouts, status errors, and network issues by raising APIError.
    """
    try:
        response = await client.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        raise APIError(f"API returned status {e.response.status_code} for {url}") from e
    except httpx.RequestError as e:
        raise APIError(f"Network error while connecting to {url}: {e}") from e

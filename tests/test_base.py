import httpx
import pytest
import respx
from clients.base import APIError, make_request


@respx.mock
async def test_make_request_success():
    """Verify make_request returns parsed JSON on HTTP 200."""
    url = "https://api.example.com/test"
    respx.get(url).respond(json={"status": "ok"})

    async with httpx.AsyncClient() as client:
        result = await make_request(client, url, params={})
        assert result == {"status": "ok"}


@respx.mock
async def test_make_request_http_error():
    """Verify APIError is raised on 4xx/5xx HTTP responses."""
    url = "https://api.example.com/test"

    # Simply return a 500 status code response
    respx.get(url).respond(status_code=500)

    async with httpx.AsyncClient() as client:
        with pytest.raises(APIError, match="API returned status 500"):
            await make_request(client, url, params={})


@respx.mock
async def test_make_request_network_error():
    """Verify APIError is raised on network connection failures."""
    url = "https://api.example.com/test"

    # Network failures happen during client.get(), so side_effect with RequestError is correct here
    respx.get(url).side_effect = httpx.RequestError("Connection failed")

    async with httpx.AsyncClient() as client:
        with pytest.raises(APIError, match="Network error"):
            await make_request(client, url, params={})

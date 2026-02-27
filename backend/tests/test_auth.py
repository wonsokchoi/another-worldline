import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.mark.asyncio
async def test_register_sends_code():
    """Register endpoint should return a verification code in dev mode."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/auth/register",
            json={"phone_number": "+821099998888"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Verification code sent"
        assert data["phone_number"] == "+821099998888"
        assert "dev_code" in data
        assert len(data["dev_code"]) == 6


@pytest.mark.asyncio
async def test_verify_invalid_code():
    """Verify with wrong code should return 400."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/auth/verify",
            json={"phone_number": "+821099998888", "code": "000000"},
        )
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_protected_endpoint_without_token():
    """Accessing protected endpoint without auth should return 401 or 403."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/characters",
            json={"name": "테스트"},
        )
        assert response.status_code in (401, 403)

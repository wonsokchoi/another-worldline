"""Tests for ranking endpoints."""
import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from tests.conftest import make_test_user, make_test_character, make_mock_db


@pytest.mark.asyncio
async def test_rankings_no_auth():
    """GET /rankings without auth should fail."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/rankings")
        assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_rankings_empty(client_factory):
    """GET /rankings with no characters should return empty list."""
    user = make_test_user()
    user.characters = []
    db = make_mock_db()

    call_count = 0

    async def side_effect_execute(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        mock_result = MagicMock()

        if call_count == 1:
            # First query: get ranked characters (empty)
            mock_result.all.return_value = []
        elif call_count == 2:
            # Second query: total count
            mock_result.scalar.return_value = 0
        return mock_result

    db.execute = AsyncMock(side_effect=side_effect_execute)

    async with client_factory(user=user, db=db) as client:
        response = await client.get("/rankings")
        assert response.status_code == 200
        data = response.json()
        assert data["rankings"] == []
        assert data["total_characters"] == 0
        assert data["my_rank"] is None


@pytest.mark.asyncio
async def test_rankings_with_characters(client_factory):
    """GET /rankings should return sorted character list."""
    user = make_test_user()
    db = make_mock_db()

    # Create mock characters for ranking
    char1 = make_test_character(uuid.uuid4(), name="용사1")
    char1.rarity_score = 95.0
    char1.worldline_count = 10

    user1 = make_test_user(phone="01011111111")
    user1.nickname = "플레이어1"

    char2 = make_test_character(uuid.uuid4(), name="마법사2")
    char2.rarity_score = 80.0
    char2.worldline_count = 5

    user2 = make_test_user(phone="01022222222")
    user2.nickname = "플레이어2"

    # User has no characters
    user.characters = []

    call_count = 0

    async def side_effect_execute(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        mock_result = MagicMock()

        if call_count == 1:
            # Ranked characters
            mock_result.all.return_value = [(char1, user1), (char2, user2)]
        elif call_count == 2:
            # Total count
            mock_result.scalar.return_value = 2
        return mock_result

    db.execute = AsyncMock(side_effect=side_effect_execute)

    async with client_factory(user=user, db=db) as client:
        response = await client.get("/rankings")
        assert response.status_code == 200
        data = response.json()
        assert len(data["rankings"]) == 2
        assert data["rankings"][0]["character_name"] == "용사1"
        assert data["rankings"][0]["rank"] == 1
        assert data["rankings"][1]["character_name"] == "마법사2"
        assert data["rankings"][1]["rank"] == 2
        assert data["total_characters"] == 2

"""Tests for character endpoints."""
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from tests.conftest import make_test_user, make_test_character, make_mock_db


@pytest.mark.asyncio
async def test_create_character(client_factory):
    """POST /characters should create a new character."""
    user = make_test_user()
    db = make_mock_db()

    # Mock refresh to simulate DB-assigned defaults
    async def mock_refresh(obj):
        if getattr(obj, 'id', None) is None:
            obj.id = uuid.uuid4()
        if getattr(obj, 'created_at', None) is None:
            obj.created_at = datetime.now(timezone.utc)
        if getattr(obj, 'updated_at', None) is None:
            obj.updated_at = datetime.now(timezone.utc)
        # Ensure default values that SQLAlchemy would set
        if getattr(obj, 'race', None) is None:
            obj.race = "인간"
        # Set defaults matching the Character model
        defaults = {
            'hp': 100, 'mp': 50,
            'strength': 10, 'intelligence': 10, 'agility': 10,
            'luck': 10, 'charm': 10,
            'skills': [], 'equipment': {}, 'pets': [], 'relationships': [],
            'rarity_score': 0.0, 'worldline_count': 0,
        }
        for attr, default_val in defaults.items():
            if getattr(obj, attr, None) is None:
                obj.__dict__[attr] = default_val

    db.refresh = AsyncMock(side_effect=mock_refresh)

    async with client_factory(user=user, db=db) as client:
        response = await client.post(
            "/characters",
            json={"name": "테스트캐릭터"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "테스트캐릭터"
        assert data["race"] == "인간"
        assert data["stats"]["hp"] == 100
        # DB add should have been called
        db.add.assert_called_once()
        db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_create_character_empty_name(client_factory):
    """POST /characters with empty name creates character (no length validation)."""
    user = make_test_user()
    db = make_mock_db()

    async def mock_refresh(obj):
        if getattr(obj, 'id', None) is None:
            obj.id = uuid.uuid4()
        if getattr(obj, 'created_at', None) is None:
            obj.created_at = datetime.now(timezone.utc)
        if getattr(obj, 'updated_at', None) is None:
            obj.updated_at = datetime.now(timezone.utc)
        if getattr(obj, 'race', None) is None:
            obj.race = "인간"
        defaults = {
            'hp': 100, 'mp': 50,
            'strength': 10, 'intelligence': 10, 'agility': 10,
            'luck': 10, 'charm': 10,
            'skills': [], 'equipment': {}, 'pets': [], 'relationships': [],
            'rarity_score': 0.0, 'worldline_count': 0,
        }
        for attr, default_val in defaults.items():
            if getattr(obj, attr, None) is None:
                obj.__dict__[attr] = default_val

    db.refresh = AsyncMock(side_effect=mock_refresh)

    async with client_factory(user=user, db=db) as client:
        response = await client.post(
            "/characters",
            json={"name": ""},
        )
        # Empty string is valid for str type — no min_length validation in schema
        assert response.status_code == 201


@pytest.mark.asyncio
async def test_get_character_not_found(client_factory):
    """GET /characters/{id} with non-existent ID should return 404."""
    user = make_test_user()
    db = make_mock_db()

    # Mock query result returning None
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute = AsyncMock(return_value=mock_result)

    async with client_factory(user=user, db=db) as client:
        response = await client.get(f"/characters/{uuid.uuid4()}")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_character_success(client_factory):
    """GET /characters/{id} should return character details."""
    user = make_test_user()
    db = make_mock_db()
    char = make_test_character(user.id)

    # Mock query result
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = char
    db.execute = AsyncMock(return_value=mock_result)

    async with client_factory(user=user, db=db) as client:
        response = await client.get(f"/characters/{char.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "아리아"
        assert data["race"] == "인간"
        assert "stats" in data
        assert data["stats"]["hp"] == 100
        assert data["stats"]["mp"] == 50


@pytest.mark.asyncio
async def test_create_character_without_auth():
    """POST /characters without auth should return 401/403."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/characters",
            json={"name": "노인증"},
        )
        assert response.status_code in (401, 403)

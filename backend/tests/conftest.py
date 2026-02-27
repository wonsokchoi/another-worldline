"""Test fixtures for Another Worldline backend."""
import uuid
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.character import Character
from app.core.security import create_access_token


# --- Mock DB Session ---

def make_mock_db():
    """Create a mock async DB session."""
    db = AsyncMock(spec=AsyncSession)
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.flush = AsyncMock()
    db.close = AsyncMock()
    db.add = MagicMock()
    return db


# --- Mock User ---

def make_test_user(user_id=None, phone="01012345678"):
    """Create a test user object."""
    user = MagicMock(spec=User)
    user.id = user_id or uuid.uuid4()
    user.phone_number = phone
    user.phone_verified = True
    user.nickname = "테스터"
    user.daily_free_pulls_used = 0
    user.last_pull_reset_date = None
    user.coupon_balance = 0
    user.characters = []
    user.created_at = datetime.now(timezone.utc)
    user.updated_at = datetime.now(timezone.utc)
    return user


def make_test_character(user_id, name="아리아", char_id=None):
    """Create a test character object."""
    char = MagicMock(spec=Character)
    char.id = char_id or uuid.uuid4()
    char.user_id = user_id
    char.name = name
    char.race = "인간"
    char.hp = 100
    char.mp = 50
    char.strength = 10
    char.intelligence = 10
    char.agility = 10
    char.luck = 10
    char.charm = 10
    char.skills = ["기본 검술"]
    char.equipment = {"weapon": "나무 검"}
    char.pets = []
    char.relationships = []
    char.rarity_score = 50.0
    char.worldline_count = 1
    char.created_at = datetime.now(timezone.utc)
    char.updated_at = datetime.now(timezone.utc)
    return char


# --- Fixtures ---

@pytest.fixture
def test_user():
    return make_test_user()


@pytest.fixture
def test_character(test_user):
    return make_test_character(test_user.id)


@pytest.fixture
def auth_token(test_user):
    """Generate a valid JWT token for test user."""
    return create_access_token(data={"sub": str(test_user.id)})


@pytest.fixture
def mock_db():
    return make_mock_db()


@pytest.fixture
def client_factory():
    """Factory to create test clients with optional auth and DB overrides."""

    def _create(user=None, db=None):
        overrides = {}
        if db is not None:
            async def _get_db_override():
                yield db
            overrides[get_db] = _get_db_override

        if user is not None:
            async def _get_user_override():
                return user
            overrides[get_current_user] = _get_user_override

        for dep, override in overrides.items():
            app.dependency_overrides[dep] = override

        transport = ASGITransport(app=app)
        client = AsyncClient(transport=transport, base_url="http://test")
        return client

    yield _create

    # Cleanup
    app.dependency_overrides.clear()

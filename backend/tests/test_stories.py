"""Tests for story endpoints."""
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone, timedelta

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.config import settings
from tests.conftest import make_test_user, make_test_character, make_mock_db


@pytest.mark.asyncio
async def test_pull_story_no_auth():
    """POST /stories/pull without auth should fail."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/stories/pull",
            json={"character_id": str(uuid.uuid4())},
        )
        assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_pull_story_character_not_found(client_factory):
    """POST /stories/pull with invalid character should return 404."""
    user = make_test_user()
    db = make_mock_db()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute = AsyncMock(return_value=mock_result)

    async with client_factory(user=user, db=db) as client:
        response = await client.post(
            "/stories/pull",
            json={"character_id": str(uuid.uuid4())},
        )
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_pull_story_daily_limit(client_factory):
    """POST /stories/pull should enforce daily free pull limit."""
    user = make_test_user()
    user.daily_free_pulls_used = settings.FREE_PULLS_PER_DAY  # Already exhausted
    user.coupon_balance = 0
    kst = timezone(timedelta(hours=9))
    user.last_pull_reset_date = datetime.now(kst)  # Reset already happened today

    db = make_mock_db()
    char = make_test_character(user.id)

    # First execute returns character, subsequent ones are for worldline query
    mock_char_result = MagicMock()
    mock_char_result.scalar_one_or_none.return_value = char
    db.execute = AsyncMock(return_value=mock_char_result)

    async with client_factory(user=user, db=db) as client:
        response = await client.post(
            "/stories/pull",
            json={"character_id": str(char.id)},
        )
        assert response.status_code == 429
        assert "exhausted" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_pull_story_success_with_mock_engine(client_factory):
    """POST /stories/pull should generate a story via mocked StoryEngine."""
    user = make_test_user()
    user.daily_free_pulls_used = 0
    user.last_pull_reset_date = None

    db = make_mock_db()
    char = make_test_character(user.id)
    # Ensure char has real stat attributes for the endpoint to modify
    char.hp = 100
    char.mp = 50
    char.strength = 10
    char.intelligence = 10
    char.agility = 10
    char.luck = 10
    char.charm = 10
    char.worldline_count = 0

    # Create a pre-built mock worldline (avoids SQLAlchemy default issues)
    mock_worldline = MagicMock()
    mock_worldline.id = uuid.uuid4()
    mock_worldline.character_id = char.id
    mock_worldline.worldline_number = 1
    mock_worldline.genre = "판타지"
    mock_worldline.is_active = True
    mock_worldline.story_count = 0

    # Setup multiple execute calls
    call_count = 0

    async def side_effect_execute(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        mock_result = MagicMock()
        if call_count == 1:
            mock_result.scalar_one_or_none.return_value = char
        elif call_count == 2:
            mock_result.scalar_one_or_none.return_value = mock_worldline
        elif call_count == 3:
            mock_result.scalars.return_value.all.return_value = []
        return mock_result

    db.execute = AsyncMock(side_effect=side_effect_execute)

    # Mock refresh to set story attributes after "commit"
    story_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    async def mock_refresh(obj):
        obj.__dict__.update({'id': story_id, 'created_at': now})

    db.refresh = AsyncMock(side_effect=mock_refresh)

    # Mock the StoryEngine
    with patch("app.api.routes.stories.StoryEngine") as MockEngine:
        mock_engine = MockEngine.return_value
        mock_engine.generate_story = AsyncMock(return_value={
            "content": "마법의 숲에서 모험이 시작되었다.",
            "stat_changes": {"hp": 5, "strength": 2},
            "items_gained": {"skills": ["불꽃 마법"], "equipment": {}, "pets": []},
        })

        async with client_factory(user=user, db=db) as client:
            response = await client.post(
                "/stories/pull",
                json={"character_id": str(char.id)},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["content"] == "마법의 숲에서 모험이 시작되었다."
            assert "genre" in data
            assert data["worldline_number"] == 1
            mock_engine.generate_story.assert_called_once()


@pytest.mark.asyncio
async def test_story_history_no_auth():
    """GET /stories/{character_id}/history without auth should fail."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(f"/stories/{uuid.uuid4()}/history")
        assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_story_history_not_found(client_factory):
    """GET /stories/{character_id}/history with invalid character should return 404."""
    user = make_test_user()
    db = make_mock_db()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute = AsyncMock(return_value=mock_result)

    async with client_factory(user=user, db=db) as client:
        response = await client.get(f"/stories/{uuid.uuid4()}/history")
        assert response.status_code == 404

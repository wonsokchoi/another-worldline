"""Tests for rarity calculator service."""
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.rarity_calculator import RarityCalculator
from tests.conftest import make_test_character, make_mock_db


@pytest.mark.asyncio
async def test_rarity_single_character():
    """With only one character, rarity should be 50.0."""
    calc = RarityCalculator()
    db = make_mock_db()
    char = make_test_character(user_id="u1")

    call_count = 0

    async def mock_execute(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        mock_result = MagicMock()
        if call_count == 1:
            # Total count = 1
            mock_result.scalar.return_value = 1
        return mock_result

    db.execute = AsyncMock(side_effect=mock_execute)
    score = await calc.calculate_rarity(char, db)
    assert score == 50.0


@pytest.mark.asyncio
async def test_rarity_top_character():
    """Top ranked character should have high rarity score."""
    calc = RarityCalculator()
    db = make_mock_db()
    char = make_test_character(user_id="u1")
    char.hp = 999
    char.mp = 999
    char.strength = 100
    char.intelligence = 100
    char.agility = 100
    char.luck = 100
    char.charm = 100
    char.worldline_count = 100

    call_count = 0

    async def mock_execute(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        mock_result = MagicMock()
        if call_count == 1:
            mock_result.scalar.return_value = 100  # 100 characters total
        elif call_count == 2:
            mock_result.scalar.return_value = 0  # 0 characters above this stat total
        elif call_count == 3:
            mock_result.scalar.return_value = 0  # 0 characters above this worldline count
        return mock_result

    db.execute = AsyncMock(side_effect=mock_execute)
    score = await calc.calculate_rarity(char, db)
    assert score == 100.0


@pytest.mark.asyncio
async def test_rarity_bottom_character():
    """Lowest ranked character should have low rarity score."""
    calc = RarityCalculator()
    db = make_mock_db()
    char = make_test_character(user_id="u1")
    char.hp = 1
    char.mp = 1
    char.strength = 1
    char.intelligence = 1
    char.agility = 1
    char.luck = 1
    char.charm = 1
    char.worldline_count = 0

    call_count = 0

    async def mock_execute(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        mock_result = MagicMock()
        if call_count == 1:
            mock_result.scalar.return_value = 100  # 100 total
        elif call_count == 2:
            mock_result.scalar.return_value = 99  # 99 above in stats
        elif call_count == 3:
            mock_result.scalar.return_value = 99  # 99 above in worldlines
        return mock_result

    db.execute = AsyncMock(side_effect=mock_execute)
    score = await calc.calculate_rarity(char, db)
    assert score == 1.0


@pytest.mark.asyncio
async def test_rarity_weighted_calculation():
    """Rarity should be 60% stats + 40% worldlines weighted."""
    calc = RarityCalculator()
    db = make_mock_db()
    char = make_test_character(user_id="u1")

    call_count = 0

    async def mock_execute(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        mock_result = MagicMock()
        if call_count == 1:
            mock_result.scalar.return_value = 10  # 10 total
        elif call_count == 2:
            mock_result.scalar.return_value = 5  # 5 above = 50th percentile stats
        elif call_count == 3:
            mock_result.scalar.return_value = 2  # 2 above = 80th percentile worldlines
        return mock_result

    db.execute = AsyncMock(side_effect=mock_execute)
    score = await calc.calculate_rarity(char, db)
    # Expected: 50 * 0.6 + 80 * 0.4 = 30 + 32 = 62.0
    assert score == 62.0


def test_stat_fields_complete():
    """RarityCalculator should track all 7 stat fields."""
    calc = RarityCalculator()
    expected = ["hp", "mp", "strength", "intelligence", "agility", "luck", "charm"]
    assert calc.STAT_FIELDS == expected

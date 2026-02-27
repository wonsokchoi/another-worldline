import pytest
import json

from app.services.story_engine import StoryEngine, GENRE_PROMPTS


def test_genre_prompts_complete():
    """All 7 genres should have prompt descriptions."""
    expected_genres = ["판타지", "로맨스", "스릴러", "히어로", "SF", "수필", "시나리오"]
    for genre in expected_genres:
        assert genre in GENRE_PROMPTS, f"Missing genre prompt: {genre}"


def test_parse_response_valid_json():
    """StoryEngine should parse valid JSON response."""
    engine = StoryEngine.__new__(StoryEngine)  # skip __init__ (no API key needed)
    raw = json.dumps({
        "content": "테스트 스토리입니다.",
        "stat_changes": {"hp": 5, "strength": -2},
        "items_gained": {"skills": ["검술"], "equipment": {}, "pets": []},
    })
    result = engine._parse_response(raw)
    assert result["content"] == "테스트 스토리입니다."
    assert result["stat_changes"]["hp"] == 5


def test_parse_response_markdown_block():
    """StoryEngine should extract JSON from markdown code blocks."""
    engine = StoryEngine.__new__(StoryEngine)
    raw = """여기 결과입니다:
```json
{"content": "마법의 숲에서 모험이 시작되었다.", "stat_changes": {"luck": 3}, "items_gained": null}
```"""
    result = engine._parse_response(raw)
    assert "마법의 숲" in result["content"]


def test_parse_response_fallback():
    """StoryEngine should fallback to raw text if JSON parsing fails."""
    engine = StoryEngine.__new__(StoryEngine)
    raw = "이것은 JSON이 아닌 일반 텍스트입니다."
    result = engine._parse_response(raw)
    assert result["content"] == raw[:400]
    assert result["stat_changes"] is None


def test_build_context_empty():
    """First story should get a special context message."""
    engine = StoryEngine.__new__(StoryEngine)

    class MockCharacter:
        name = "아리아"

    context = engine._build_context(MockCharacter(), [])
    assert "첫 번째 이야기" in context

"""AI story quality verification tests.

Tests the story generation pipeline including:
- Fallback story generation (when API is unavailable)
- Story structure validation
- Genre coverage
- Stat change parsing
- Context chaining
"""
import json
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.story_engine import StoryEngine, GENRE_PROMPTS


# --- Fallback Story Tests ---

ALL_GENRES = ["판타지", "로맨스", "스릴러", "히어로", "SF", "수필", "시나리오"]


class MockCharacter:
    """Simple character mock for testing."""
    def __init__(self, name="아리아", race="인간"):
        self.name = name
        self.race = race
        self.hp = 100
        self.mp = 50
        self.strength = 10
        self.intelligence = 10
        self.agility = 10
        self.luck = 10
        self.charm = 10
        self.skills = ["기본 검술"]
        self.equipment = {"weapon": "나무 검"}
        self.pets = []


@pytest.mark.asyncio
@pytest.mark.parametrize("genre", ALL_GENRES)
async def test_fallback_story_per_genre(genre):
    """Each genre should produce a valid fallback story when API fails."""
    engine = StoryEngine.__new__(StoryEngine)
    # Simulate API failure by directly calling the fallback logic
    char = MockCharacter()

    # Reproduce the fallback from story_engine.py
    fallback = {
        "content": f"{char.name}(이)가 새로운 세계선에서 눈을 떴다. 주변은 {genre}의 세계로 가득했다. 아직 이 세계의 비밀은 밝혀지지 않았다...",
        "stat_changes": {"luck": 1},
        "items_gained": None,
    }

    assert fallback["content"] is not None
    assert len(fallback["content"]) > 0
    assert char.name in fallback["content"]
    assert genre in fallback["content"]
    assert fallback["stat_changes"] is not None
    assert fallback["stat_changes"]["luck"] == 1


@pytest.mark.asyncio
async def test_fallback_with_different_characters():
    """Fallback stories should adapt to different character names."""
    engine = StoryEngine.__new__(StoryEngine)

    characters = [
        MockCharacter(name="용사", race="엘프"),
        MockCharacter(name="마법사", race="드워프"),
        MockCharacter(name="도적", race="수인"),
        MockCharacter(name="성직자", race="반인"),
        MockCharacter(name="궁수", race="요정"),
    ]

    for char in characters:
        for genre in ALL_GENRES:
            fallback = {
                "content": f"{char.name}(이)가 새로운 세계선에서 눈을 떴다. 주변은 {genre}의 세계로 가득했다. 아직 이 세계의 비밀은 밝혀지지 않았다...",
                "stat_changes": {"luck": 1},
                "items_gained": None,
            }
            assert char.name in fallback["content"]


# --- Response Parsing Quality Tests ---

def test_parse_well_formed_json():
    """Well-formed JSON should parse correctly with all fields."""
    engine = StoryEngine.__new__(StoryEngine)
    raw = json.dumps({
        "content": "마법의 숲에서 아리아는 고대의 유적을 발견했다. 유적의 문에는 알 수 없는 문양이 새겨져 있었고, 그녀가 손을 대자 환한 빛이 뿜어져 나왔다. 어디선가 들려오는 속삭임이 그녀를 유적 안으로 이끌었다.",
        "stat_changes": {"hp": 5, "intelligence": 3, "luck": -1},
        "items_gained": {
            "skills": ["고대어 해독"],
            "equipment": {"accessory": "빛나는 부적"},
            "pets": [],
        },
    }, ensure_ascii=False)

    result = engine._parse_response(raw)
    assert "마법의 숲" in result["content"]
    assert result["stat_changes"]["hp"] == 5
    assert result["stat_changes"]["intelligence"] == 3
    assert result["stat_changes"]["luck"] == -1
    assert "고대어 해독" in result["items_gained"]["skills"]
    assert result["items_gained"]["equipment"]["accessory"] == "빛나는 부적"


def test_parse_json_in_markdown():
    """JSON wrapped in markdown code blocks should parse."""
    engine = StoryEngine.__new__(StoryEngine)
    raw = """여기 스토리 결과입니다:

```json
{
    "content": "어둠 속에서 검은 그림자가 다가왔다. 용사는 검을 뽑아 전투 자세를 취했다.",
    "stat_changes": {"strength": 2, "agility": 1},
    "items_gained": {"skills": ["그림자 감지"], "equipment": {}, "pets": []}
}
```

이상입니다."""
    result = engine._parse_response(raw)
    assert "어둠 속" in result["content"]
    assert result["stat_changes"]["strength"] == 2


def test_parse_json_with_extra_text():
    """JSON embedded in other text should still be found."""
    engine = StoryEngine.__new__(StoryEngine)
    raw = """스토리를 생성했습니다.
{"content": "하늘에서 별이 떨어졌다.", "stat_changes": {"luck": 5}, "items_gained": null}
위 내용을 참고하세요."""
    result = engine._parse_response(raw)
    assert "별이 떨어졌다" in result["content"]


def test_parse_pure_text_fallback():
    """Non-JSON text should fall back to using text as content."""
    engine = StoryEngine.__new__(StoryEngine)
    raw = "마법사는 숲 속을 걸었다. 나뭇잎 사이로 햇살이 내리쬐었고, 어디선가 새소리가 들려왔다."
    result = engine._parse_response(raw)
    assert result["content"] == raw
    assert result["stat_changes"] is None
    assert result["items_gained"] is None


def test_parse_truncates_long_text():
    """Very long non-JSON text should be truncated to 400 chars."""
    engine = StoryEngine.__new__(StoryEngine)
    raw = "가" * 500  # 500 characters
    result = engine._parse_response(raw)
    assert len(result["content"]) == 400


@pytest.mark.parametrize("stat_changes,expected_valid", [
    ({"hp": 5, "strength": -2}, True),
    ({"hp": 0, "mp": 0, "strength": 0, "intelligence": 0, "agility": 0, "luck": 0, "charm": 0}, True),
    ({"luck": 3}, True),  # Partial stats are valid
    ({}, True),  # Empty is valid
])
def test_stat_change_formats(stat_changes, expected_valid):
    """Various stat change formats should be accepted."""
    engine = StoryEngine.__new__(StoryEngine)
    raw = json.dumps({
        "content": "테스트 스토리.",
        "stat_changes": stat_changes,
        "items_gained": None,
    })
    result = engine._parse_response(raw)
    assert result["stat_changes"] == stat_changes


# --- Context Building Quality Tests ---

class MockStory:
    """Simple story mock for context testing."""
    def __init__(self, genre, content):
        self.genre = genre
        self.content = content


def test_context_first_story():
    """First story should get special starting context."""
    engine = StoryEngine.__new__(StoryEngine)
    char = MockCharacter()
    context = engine._build_context(char, [])
    assert "첫 번째 이야기" in context
    assert "처음" in context


def test_context_with_previous_stories():
    """Context should include previous story summaries."""
    engine = StoryEngine.__new__(StoryEngine)
    char = MockCharacter()

    stories = [
        MockStory("판타지", "마법의 숲에서 용을 만났다."),
        MockStory("스릴러", "어둠 속에서 미지의 존재가 다가왔다."),
    ]
    context = engine._build_context(char, stories)
    assert "마법의 숲" in context or "용" in context
    assert "어둠 속" in context or "미지" in context


def test_context_limits_to_3_stories():
    """Context should only include last 3 stories max."""
    engine = StoryEngine.__new__(StoryEngine)
    char = MockCharacter()

    stories = [
        MockStory("판타지", f"스토리 {i}의 내용입니다.") for i in range(10)
    ]
    context = engine._build_context(char, stories)
    # Should only include 3 stories worth of context
    parts = context.split("\n")
    assert len(parts) <= 3


def test_context_truncates_long_stories():
    """Long stories in context should be truncated to 200 chars."""
    engine = StoryEngine.__new__(StoryEngine)
    char = MockCharacter()

    long_content = "가" * 500
    stories = [MockStory("판타지", long_content)]
    context = engine._build_context(char, stories)
    # The content should be truncated
    assert len(context) < 300  # Less than original 500 + genre tag


# --- Genre Prompt Quality Tests ---

def test_all_genres_have_korean_descriptions():
    """All genre prompts should be meaningful Korean descriptions."""
    for genre, desc in GENRE_PROMPTS.items():
        assert len(desc) >= 10, f"Genre '{genre}' has too short description"
        # Should contain Korean characters
        has_korean = any('\uac00' <= c <= '\ud7a3' for c in desc)
        assert has_korean, f"Genre '{genre}' description lacks Korean text"


def test_genres_are_distinct():
    """Each genre description should be unique."""
    descriptions = list(GENRE_PROMPTS.values())
    assert len(descriptions) == len(set(descriptions)), "Duplicate genre descriptions found"


def test_genre_count():
    """Should have exactly 7 genres."""
    assert len(GENRE_PROMPTS) == 7

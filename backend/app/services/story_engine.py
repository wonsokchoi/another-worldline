import json
import re
from typing import Optional

import anthropic

from app.core.config import settings
from app.models.character import Character
from app.models.story import Story

GENRE_PROMPTS = {
    "판타지": "마법과 모험이 가득한 판타지 세계에서의 이야기",
    "로맨스": "가슴 설레는 만남과 감정의 교차가 있는 로맨스 이야기",
    "스릴러": "긴장감 넘치는 위기와 반전이 있는 스릴러 이야기",
    "히어로": "초능력과 정의로운 영웅의 활약이 담긴 히어로 이야기",
    "SF": "미래 기술과 우주를 배경으로 한 SF 이야기",
    "수필": "일상 속 깊은 사유와 감성이 담긴 수필",
    "시나리오": "영화 같은 장면 전환과 대사가 있는 시나리오",
}


class StoryEngine:
    def __init__(self):
        self.client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    async def generate_story(
        self,
        character: Character,
        genre: str,
        previous_stories: list[Story],
    ) -> dict:
        """Generate a story paragraph using Claude API."""

        # Build context from previous stories
        context = self._build_context(character, previous_stories)
        genre_desc = GENRE_PROMPTS.get(genre, genre)

        prompt = f"""당신은 '다른 세계선'이라는 멀티버스 소설 앱의 AI 작가입니다.
캐릭터 정보와 이전 스토리를 바탕으로 새로운 이야기를 한 문단(200-400자) 생성하세요.

## 캐릭터 정보
- 이름: {character.name}
- 종족: {character.race}
- 체력: {character.hp}, 마나: {character.mp}
- 힘: {character.strength}, 지능: {character.intelligence}, 민첩: {character.agility}
- 행운: {character.luck}, 매력: {character.charm}
- 스킬: {json.dumps(character.skills or [], ensure_ascii=False)}
- 장비: {json.dumps(character.equipment or {}, ensure_ascii=False)}
- 펫: {json.dumps(character.pets or [], ensure_ascii=False)}

## 장르
{genre_desc}

## 이전 스토리 요약
{context}

## 규칙
1. 한국어로 작성
2. 200-400자의 한 문단
3. 캐릭터의 현재 능력치를 반영
4. 이전 스토리와 자연스럽게 이어지도록
5. 해당 장르의 분위기를 살릴 것
6. 마지막에 다음에 이어질 떡밥을 남길 것

## 출력 형식 (반드시 JSON)
{{
    "content": "스토리 내용...",
    "stat_changes": {{"hp": 0, "mp": 0, "strength": 0, "intelligence": 0, "agility": 0, "luck": 0, "charm": 0}},
    "items_gained": {{"skills": [], "equipment": {{}}, "pets": []}}
}}

stat_changes는 이 스토리로 인해 변동되는 능력치입니다 (-5~+5 범위).
items_gained는 새로 획득한 스킬/장비/펫입니다 (없으면 빈 값).
"""

        try:
            response = await self.client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )

            # Parse JSON response
            text = response.content[0].text
            result = self._parse_response(text)
            return result

        except Exception as e:
            # Fallback story on API error
            return {
                "content": f"{character.name}(이)가 새로운 세계선에서 눈을 떴다. 주변은 {genre}의 세계로 가득했다. 아직 이 세계의 비밀은 밝혀지지 않았다...",
                "stat_changes": {"luck": 1},
                "items_gained": None,
            }

    def _build_context(self, character: Character, previous_stories: list[Story]) -> str:
        if not previous_stories:
            return "첫 번째 이야기입니다. 캐릭터가 처음 세계에 도착한 장면으로 시작하세요."

        context_parts = []
        for story in reversed(previous_stories[:3]):
            context_parts.append(f"[{story.genre}] {story.content[:200]}")

        return "\n".join(context_parts)

    def _parse_response(self, text: str) -> dict:
        """Parse Claude's JSON response, handling potential formatting issues."""
        try:
            # Try direct JSON parse
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try extracting JSON from markdown code block
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try finding JSON object in text
        json_match = re.search(r'\{[^{}]*"content"[^{}]*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        # Last resort: use the text as content
        return {
            "content": text[:400],
            "stat_changes": None,
            "items_gained": None,
        }

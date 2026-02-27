from pydantic import BaseModel


class RankingEntry(BaseModel):
    rank: int
    character_name: str
    user_nickname: str | None
    rarity_score: float
    worldline_count: int
    race: str


class RankingResponse(BaseModel):
    rankings: list[RankingEntry]
    total_characters: int
    my_rank: int | None = None

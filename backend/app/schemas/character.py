from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CharacterCreateRequest(BaseModel):
    name: str


class CharacterStatsResponse(BaseModel):
    hp: int
    mp: int
    strength: int
    intelligence: int
    agility: int
    luck: int
    charm: int


class CharacterResponse(BaseModel):
    id: str
    name: str
    race: str
    stats: CharacterStatsResponse
    skills: list
    equipment: dict
    pets: list
    relationships: list
    rarity_score: float
    worldline_count: int
    created_at: datetime

    model_config = {"from_attributes": True}

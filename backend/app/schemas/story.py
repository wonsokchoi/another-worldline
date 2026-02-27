from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class StoryPullRequest(BaseModel):
    character_id: str


class StoryResponse(BaseModel):
    id: str
    genre: str
    content: str
    worldline_number: int
    sequence_number: int
    stat_changes: dict | None
    items_gained: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}


class StoryHistoryResponse(BaseModel):
    stories: list[StoryResponse]
    total: int

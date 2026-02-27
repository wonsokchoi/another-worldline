import random
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.character import Character
from app.models.story import Story
from app.models.worldline import Worldline
from app.schemas.story import StoryPullRequest, StoryResponse, StoryHistoryResponse
from app.services.story_engine import StoryEngine
from app.core.config import settings

router = APIRouter()

GENRES = ["판타지", "로맨스", "스릴러", "히어로", "SF", "수필", "시나리오"]


@router.post("/pull", response_model=StoryResponse)
async def pull_story(
    request: StoryPullRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Pull a new random story for a character (3 free per day)."""
    # Check character ownership
    result = await db.execute(
        select(Character).where(
            Character.id == request.character_id,
            Character.user_id == current_user.id,
        )
    )
    character = result.scalar_one_or_none()
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")

    # Check daily pull limit
    kst = timezone(timedelta(hours=9))
    now_kst = datetime.now(kst)
    today_reset = now_kst.replace(hour=0, minute=0, second=0, microsecond=0)

    if (
        current_user.last_pull_reset_date is None
        or current_user.last_pull_reset_date < today_reset
    ):
        current_user.daily_free_pulls_used = 0
        current_user.last_pull_reset_date = now_kst

    if current_user.daily_free_pulls_used >= settings.FREE_PULLS_PER_DAY:
        if current_user.coupon_balance <= 0:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Daily free pulls exhausted. Use a coupon for extra pulls.",
            )
        current_user.coupon_balance -= 1
    else:
        current_user.daily_free_pulls_used += 1

    # Pick random genre
    genre = random.choice(GENRES)

    # Get or create active worldline
    result = await db.execute(
        select(Worldline).where(
            Worldline.character_id == character.id,
            Worldline.is_active == True,
        )
    )
    worldline = result.scalar_one_or_none()

    if worldline is None:
        character.worldline_count += 1
        worldline = Worldline(
            character_id=character.id,
            worldline_number=character.worldline_count,
            genre=genre,
        )
        db.add(worldline)
        await db.flush()

    # Get previous stories for context
    result = await db.execute(
        select(Story)
        .where(Story.character_id == character.id)
        .order_by(Story.created_at.desc())
        .limit(5)
    )
    previous_stories = result.scalars().all()

    # Generate story via AI
    engine = StoryEngine()
    story_result = await engine.generate_story(
        character=character,
        genre=genre,
        previous_stories=previous_stories,
    )

    # Create story record
    worldline.story_count += 1
    story = Story(
        character_id=character.id,
        worldline_id=worldline.id,
        genre=genre,
        content=story_result["content"],
        stat_changes=story_result.get("stat_changes"),
        items_gained=story_result.get("items_gained"),
        sequence_number=worldline.story_count,
    )
    db.add(story)

    # Apply stat changes
    if story_result.get("stat_changes"):
        for stat, change in story_result["stat_changes"].items():
            if hasattr(character, stat):
                current_val = getattr(character, stat)
                setattr(character, stat, max(0, current_val + change))

    await db.commit()
    await db.refresh(story)

    return StoryResponse(
        id=str(story.id),
        genre=story.genre,
        content=story.content,
        worldline_number=worldline.worldline_number,
        sequence_number=story.sequence_number,
        stat_changes=story.stat_changes,
        items_gained=story.items_gained,
        created_at=story.created_at,
    )


@router.get("/{character_id}/history", response_model=StoryHistoryResponse)
async def get_story_history(
    character_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 20,
    offset: int = 0,
):
    """Get story history for a character."""
    # Verify ownership
    result = await db.execute(
        select(Character).where(
            Character.id == character_id,
            Character.user_id == current_user.id,
        )
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Character not found")

    # Get stories
    result = await db.execute(
        select(Story)
        .where(Story.character_id == character_id)
        .order_by(Story.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    stories = result.scalars().all()

    # Get total count
    count_result = await db.execute(
        select(func.count()).where(Story.character_id == character_id)
    )
    total = count_result.scalar()

    return StoryHistoryResponse(
        stories=[
            StoryResponse(
                id=str(s.id),
                genre=s.genre,
                content=s.content,
                worldline_number=0,  # TODO: join with worldline
                sequence_number=s.sequence_number,
                stat_changes=s.stat_changes,
                items_gained=s.items_gained,
                created_at=s.created_at,
            )
            for s in stories
        ],
        total=total,
    )

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.character import Character
from app.schemas.ranking import RankingEntry, RankingResponse

router = APIRouter()


@router.get("", response_model=RankingResponse)
async def get_rankings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
):
    """Get global rarity rankings."""
    # Get top characters by rarity score
    result = await db.execute(
        select(Character, User)
        .join(User, Character.user_id == User.id)
        .order_by(Character.rarity_score.desc())
        .limit(limit)
    )
    rows = result.all()

    rankings = []
    for rank, (character, user) in enumerate(rows, 1):
        rankings.append(
            RankingEntry(
                rank=rank,
                character_name=character.name,
                user_nickname=user.nickname,
                rarity_score=character.rarity_score,
                worldline_count=character.worldline_count,
                race=character.race,
            )
        )

    # Total characters
    count_result = await db.execute(select(func.count()).select_from(Character))
    total = count_result.scalar()

    # My rank
    my_rank = None
    if current_user.characters:
        my_char = max(current_user.characters, key=lambda c: c.rarity_score)
        rank_result = await db.execute(
            select(func.count())
            .where(Character.rarity_score > my_char.rarity_score)
        )
        my_rank = rank_result.scalar() + 1

    return RankingResponse(
        rankings=rankings,
        total_characters=total,
        my_rank=my_rank,
    )

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.character import Character
from app.schemas.character import CharacterCreateRequest, CharacterResponse, CharacterStatsResponse

router = APIRouter()


@router.post("", response_model=CharacterResponse, status_code=status.HTTP_201_CREATED)
async def create_character(
    request: CharacterCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new character with given name."""
    character = Character(
        user_id=current_user.id,
        name=request.name,
    )
    db.add(character)
    await db.commit()
    await db.refresh(character)

    return _to_response(character)


@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character(
    character_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get character details including stats."""
    result = await db.execute(
        select(Character).where(
            Character.id == character_id,
            Character.user_id == current_user.id,
        )
    )
    character = result.scalar_one_or_none()

    if character is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found",
        )

    return _to_response(character)


def _to_response(character: Character) -> CharacterResponse:
    return CharacterResponse(
        id=str(character.id),
        name=character.name,
        race=character.race,
        stats=CharacterStatsResponse(
            hp=character.hp,
            mp=character.mp,
            strength=character.strength,
            intelligence=character.intelligence,
            agility=character.agility,
            luck=character.luck,
            charm=character.charm,
        ),
        skills=character.skills or [],
        equipment=character.equipment or {},
        pets=character.pets or [],
        relationships=character.relationships or [],
        rarity_score=character.rarity_score,
        worldline_count=character.worldline_count,
        created_at=character.created_at,
    )

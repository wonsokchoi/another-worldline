from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.character import Character


class RarityCalculator:
    """Calculate relative rarity scores for characters."""

    STAT_FIELDS = ["hp", "mp", "strength", "intelligence", "agility", "luck", "charm"]

    async def calculate_rarity(self, character: Character, db: AsyncSession) -> float:
        """
        Calculate rarity score (0.0 ~ 100.0) based on:
        1. Total stats compared to all characters
        2. Genre diversity (how many unique genres experienced)
        3. Worldline count
        """
        total_characters = await self._get_total_count(db)
        if total_characters <= 1:
            return 50.0

        # Stat ranking
        total_stats = sum(getattr(character, f) for f in self.STAT_FIELDS)
        stat_rank = await self._get_stat_rank(total_stats, db)
        stat_percentile = (1 - stat_rank / total_characters) * 100

        # Worldline count ranking
        wl_rank = await self._get_worldline_rank(character.worldline_count, db)
        wl_percentile = (1 - wl_rank / total_characters) * 100

        # Combined score (weighted)
        rarity = stat_percentile * 0.6 + wl_percentile * 0.4
        return round(min(100.0, max(0.0, rarity)), 2)

    async def _get_total_count(self, db: AsyncSession) -> int:
        result = await db.execute(select(func.count()).select_from(Character))
        return result.scalar() or 0

    async def _get_stat_rank(self, total_stats: int, db: AsyncSession) -> int:
        result = await db.execute(
            select(func.count()).where(
                (Character.hp + Character.mp + Character.strength +
                 Character.intelligence + Character.agility +
                 Character.luck + Character.charm) > total_stats
            )
        )
        return result.scalar() or 0

    async def _get_worldline_rank(self, worldline_count: int, db: AsyncSession) -> int:
        result = await db.execute(
            select(func.count()).where(
                Character.worldline_count > worldline_count
            )
        )
        return result.scalar() or 0

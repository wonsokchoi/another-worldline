import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Integer, Float, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class Character(Base):
    __tablename__ = "characters"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)

    name: Mapped[str] = mapped_column(String(100))
    race: Mapped[str] = mapped_column(String(50), default="인간")

    # Stats
    hp: Mapped[int] = mapped_column(Integer, default=100)
    mp: Mapped[int] = mapped_column(Integer, default=50)
    strength: Mapped[int] = mapped_column(Integer, default=10)
    intelligence: Mapped[int] = mapped_column(Integer, default=10)
    agility: Mapped[int] = mapped_column(Integer, default=10)
    luck: Mapped[int] = mapped_column(Integer, default=10)
    charm: Mapped[int] = mapped_column(Integer, default=10)

    # Equipment & extras (JSON for flexibility)
    skills: Mapped[dict | None] = mapped_column(JSON, default=list)
    equipment: Mapped[dict | None] = mapped_column(JSON, default=dict)
    pets: Mapped[dict | None] = mapped_column(JSON, default=list)
    relationships: Mapped[dict | None] = mapped_column(JSON, default=list)

    # Rarity score (computed from relative ranking)
    rarity_score: Mapped[float] = mapped_column(Float, default=0.0)

    # Worldline counter
    worldline_count: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="characters")
    stories: Mapped[list["Story"]] = relationship(back_populates="character", lazy="selectin")
    worldlines: Mapped[list["Worldline"]] = relationship(back_populates="character", lazy="selectin")

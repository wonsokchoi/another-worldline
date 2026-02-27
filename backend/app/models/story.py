import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Integer, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class Story(Base):
    __tablename__ = "stories"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    character_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("characters.id"), index=True)
    worldline_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("worldlines.id"), index=True)

    # Story content
    genre: Mapped[str] = mapped_column(String(50))  # 판타지, 로맨스, 스릴러, 히어로, SF, 수필, 시나리오
    content: Mapped[str] = mapped_column(Text)

    # Stat changes extracted from this story
    stat_changes: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    items_gained: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Sequence within worldline
    sequence_number: Mapped[int] = mapped_column(Integer, default=1)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    character: Mapped["Character"] = relationship(back_populates="stories")
    worldline: Mapped["Worldline"] = relationship(back_populates="stories")

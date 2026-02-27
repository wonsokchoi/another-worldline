import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class Worldline(Base):
    __tablename__ = "worldlines"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    character_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("characters.id"), index=True)

    worldline_number: Mapped[int] = mapped_column(Integer)  # 제N세계선
    genre: Mapped[str] = mapped_column(String(50))

    # Status
    is_active: Mapped[bool] = mapped_column(default=True)
    story_count: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    character: Mapped["Character"] = relationship(back_populates="worldlines")
    stories: Mapped[list["Story"]] = relationship(back_populates="worldline", lazy="selectin")

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    phone_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    nickname: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Daily pull tracking
    daily_free_pulls_used: Mapped[int] = mapped_column(Integer, default=0)
    last_pull_reset_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Paid coupons
    coupon_balance: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    characters: Mapped[list["Character"]] = relationship(back_populates="user", lazy="selectin")

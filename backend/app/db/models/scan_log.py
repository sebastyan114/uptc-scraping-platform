import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class ScanLog(Base):
    __tablename__="scan_logs"

    
    id: Mapped[uuid.UUID]=mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    analysis_id: Mapped[uuid.UUID]=mapped_column(
        UUID(as_uuid=True),
        ForeingKey("analyses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    target_url: Mapped[str]=mapped_column(
        Text,
        nullable=False,
    )

    module:Mapped[str]=mapped_column(
        String(100),
        nullable=False,
    )

    level: Mapped[str]=mapped_column(
        String(20),
        nullable=False,
        default="error",
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
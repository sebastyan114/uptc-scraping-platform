import uuid
from datetime import datetime,timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Finding(Base):
    __tablename__="findings"

    
    id: Mapped[uuid.UUID]=mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    analysis_id: Mapped[uuid.UUID]=mapped_column(
        UUID(as_uuid=True),
        ForeignKey("analyses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    finding_type:Mapped[str]=mapped_column(
        String(150),
        nullable=False,
    )

    severity: Mapped[str]=mapped_column(
        String(20),
        nullable=False,
    )

    description: Mapped[str]=mapped_column(
        Text,
        nullable=False,
    )

    source: Mapped[str]=mapped_column(
        String(100),
        nullable=False,
    )

    evidence: Mapped[str|None]=mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
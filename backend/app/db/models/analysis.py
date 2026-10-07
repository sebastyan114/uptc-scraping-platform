import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Analysis(Base):
    __tablename__="analyses"

    id: Mapped[uuid.UUID]=mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    target_url:Mapped[str]=mapped_column(
        Text,
        nullable=False,
    )

    status:Mapped[str] =mapped_column(
        String(30),
        nullable=False,
        default="running"
    )
    current_stage: Mapped[str|None]=mapped_column(
        String(50),
        nullable=True,
    )
    scan_mode: Maped[str]=mapped_column(
        String(20),
        nullable=False,
        default="passive",
    )

    created_at: Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    finished_at: Mapped[datetime| None]=mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    error_message:Mapped[str|None]=mapped_column(
        Text,
        nullable=True,
    )
    
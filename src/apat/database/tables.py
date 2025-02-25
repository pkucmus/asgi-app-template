import uuid
from datetime import datetime
from typing import Annotated

from sqlalchemy import (
    DateTime,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from apat.database.database import metadata

PrimaryKeyColumn = Annotated[
    uuid.UUID,
    mapped_column(
        UUID, primary_key=True, nullable=False, server_default=text("gen_random_uuid()")
    ),
]
AutoAddColumn = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        server_default=text("current_timestamp(0)"),
        nullable=True,
        default=None,
    ),
]
AutoAddNowColumn = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        server_default=text("current_timestamp(0)"),
        nullable=False,
        default=None,
        onupdate=text("current_timestamp(0)"),
    ),
]


class Base(DeclarativeBase):
    __abstract__ = True
    metadata = metadata


class UUIDBase(Base):
    __abstract__ = True

    id: Mapped[PrimaryKeyColumn]


class TemporalBase(Base):
    __abstract__ = True

    created_at: Mapped[AutoAddColumn]
    updated_at: Mapped[AutoAddNowColumn]


class BaseTable(UUIDBase, TemporalBase):
    __abstract__ = True

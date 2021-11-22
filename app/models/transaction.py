from enum import Enum, IntEnum
from sqlmodel import SQLModel, Field
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy.sql.expression import text
from pydantic import EmailStr, validator
import re

from app.models import account


class TransactionType(IntEnum):
    debit = 1,
    credit = 2


class TransactionBase(SQLModel):
    type: TransactionType
    amount: float = Field(default=0)
    status: bool = Field(default=False)
    details: str


class Transaction(TransactionBase, table=True):
    uuid: Optional[UUID] = Field(
        default_factory=uuid4,
        primary_key=True,
        sa_column_kwargs={"server_default": text("uuid_generate_v4()")},
    )

    account_uuid: UUID = Field(foreign_key="account.uuid", index=True)

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": text("now()")},
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={
            "server_default": text("now()"),
            "server_onupdate": text("now()"),
        },
    )
    deleted_at: Optional[datetime]


class TransactionCreate(TransactionBase):
    pass


class TransactionRead(TransactionBase):
    uuid: UUID
    account_uuid: UUID
    created_at: UUID
    updated_at: UUID


class TransactionUpdate(SQLModel):
    type: Optional[TransactionType]
    details: Optional[str]

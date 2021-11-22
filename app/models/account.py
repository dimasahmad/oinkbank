from enum import Enum
from sqlmodel import SQLModel, Field
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy.sql.expression import text
from pydantic import EmailStr, validator
import re

from app.models.user import UserRead


class Currency(str, Enum):
    IDR = "IDR"


class AccountBase(SQLModel):
    number: int
    balance: float = Field(
        default=0, nullable=False, sa_column_kwargs={"server_default": "0"}
    )
    currency: Currency = Field(
        default=Currency.IDR, nullable=False, sa_column_kwargs={"server_default": "IDR"}
    )
    minimum_balance: float = Field(
        default=50_000, nullable=False, sa_column_kwargs={"server_default": "50000"}
    )
    interest: float


class Account(AccountBase, table=True):
    uuid: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        sa_column_kwargs={"server_default": text("uuid_generate_v4()")},
    )

    user_uuid: UUID = Field(foreign_key="user.uuid", index=True)

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


class AccountCreate(AccountBase):
    pass


class AccountRead(AccountBase):
    uuid: UUID
    created_at: datetime
    updated_at: datetime


class AccountUpdate(SQLModel):
    number: Optional[int]
    balance: Optional[float]
    currency: Optional[Currency]
    minimum_balance: Optional[float]
    interest: Optional[float]

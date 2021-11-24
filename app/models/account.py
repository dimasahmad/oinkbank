from sqlmodel import SQLModel, Field, Relationship, text
from pydantic import EmailStr, validator

from enum import Enum, IntEnum
from uuid import UUID, uuid4
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from app.models.branch import BranchRead
from app.models.user import UserRead

if TYPE_CHECKING:
    from app.models.branch import Branch
    from app.models.user import User
    from app.models.transaction import Transaction

class Currency(str, Enum):
    IDR = "IDR"


class AccountBase(SQLModel):
    number: str
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
    user_uuid: UUID = Field(foreign_key="user.uuid", index=True)
    branch_uuid: UUID = Field(foreign_key="branch.uuid", index=True)

    user: "User" = Relationship(back_populates="accounts")
    branch: "Branch" = Relationship(back_populates="accounts")

    uuid: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        sa_column_kwargs={"server_default": text("uuid_generate_v4()")},
    )
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

    transactions: List["Transaction"] = Relationship(back_populates="account")


class AccountCreate(AccountBase):
    user_uuid: UUID
    branch_uuid: UUID


class AccountRead(AccountBase):
    user: UserRead
    branch: BranchRead
    uuid: UUID
    created_at: datetime
    updated_at: datetime


class AccountUpdate(SQLModel):
    minimum_balance: Optional[float]
    interest: Optional[float]

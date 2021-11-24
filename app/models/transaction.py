from sqlmodel import SQLModel, Field, Relationship, text
from pydantic import EmailStr, validator

from enum import Enum, IntEnum
from uuid import UUID, uuid4
from datetime import date, datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel.main import Relationship

from app.models.account import AccountRead

if TYPE_CHECKING:
    from app.models.account import Account


class TransactionType(IntEnum):
    DEPOSIT = 1
    WITHDRAWAL = 2
    TRANSFER = 3
    INTEREST = 4
    FEE = 5

class TransferFund(SQLModel):
    account_number: str

class TransactionBase(SQLModel):
    type: TransactionType
    amount: float = Field(default=0)
    status: bool = Field(default=False)
    details: Optional[str]


class Transaction(TransactionBase, table=True):
    account_uuid: UUID = Field(foreign_key="account.uuid", index=True)
    account: "Account" = Relationship(back_populates="transactions")

    uuid: Optional[UUID] = Field(
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


class TransactionCreate(TransactionBase):
    transfer: Optional[TransferFund] = None


class TransactionRead(TransactionBase):
    # account: AccountRead
    account_uuid: UUID
    uuid: UUID
    created_at: datetime
    updated_at: datetime


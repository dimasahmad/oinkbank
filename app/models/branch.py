import re
from enum import Enum, IntEnum
from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import text
from pydantic import EmailStr, validator
from typing import TYPE_CHECKING, List, Optional

from app.models.address import AddressCreate, AddressRead, AddressUpdate

if TYPE_CHECKING:
    from app.models.address import Address
    from app.models.account import Account


class BranchType(str, Enum):
    KC = "KC"
    KCP = "KCP"


class BranchBase(SQLModel):
    name: str
    type: BranchType
    phone_number: str
    description: Optional[str]


class Branch(BranchBase, table=True):
    address_uuid: UUID = Field(foreign_key="address.uuid")
    address: "Address" = Relationship(back_populates="branch")

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

    accounts: List["Account"] = Relationship(back_populates="branch")


class BranchCreate(BranchBase):
    address: AddressCreate


class BranchRead(BranchBase):
    address: AddressRead
    uuid: UUID
    created_at: datetime
    updated_at: datetime


class BranchUpdate(SQLModel):
    name: Optional[str]
    phone_number: Optional[str]
    description: Optional[str]
    address: Optional[AddressUpdate]

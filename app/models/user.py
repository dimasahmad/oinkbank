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


class IdentityType(str, Enum):
    KTP = "KTP"
    SIM = "SIM"
    PASSPORT = "Passport"


class UserRole(IntEnum):
    ADMIN = 10
    CONSUMER = 1


class UserBase(SQLModel):
    username: str = Field(sa_column_kwargs={"unique": True})
    email: EmailStr = Field(sa_column_kwargs={"unique": True})
    phone_number: str = Field(sa_column_kwargs={"unique": True})
    full_name: str
    identity_number: str
    identity_type: IdentityType
    phone_number: str
    description: Optional[str]


class User(UserBase, table=True):
    role: UserRole = Field(default=1, sa_column_kwargs={"server_default": "1"})
    password_hash: bytes
    address_uuid: UUID = Field(foreign_key="address.uuid")
    address: "Address" = Relationship(back_populates="user")

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

    accounts: List["Account"] = Relationship(back_populates="user")


class UserCreate(UserBase):
    password: str
    address: AddressCreate


class UserRead(UserBase):
    address: AddressRead
    uuid: UUID
    created_at: datetime
    updated_at: datetime


class UserUpdate(SQLModel):
    username: Optional[str]
    email: Optional[str]
    phone_number: Optional[str]
    password: Optional[str]
    full_name: Optional[str]
    identity_number: Optional[str]
    identity_type: Optional[IdentityType]
    phone_number: Optional[str]
    description: Optional[str]
    address: Optional[AddressUpdate]

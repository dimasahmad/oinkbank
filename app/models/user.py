from enum import Enum
from sqlmodel import SQLModel, Field
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy.sql.expression import text
from pydantic import EmailStr, validator
import re


class IdentityType(str, Enum):
    ktp = "KTP"
    sim = "SIM"
    passport = "Passport"


class UserBase(SQLModel):
    username: str = Field(sa_column_kwargs={"unique": True})
    email: EmailStr = Field(sa_column_kwargs={"unique": True})
    phone_number: str = Field(sa_column_kwargs={"unique": True})
    name: str
    identity_number: int
    identity_type: IdentityType
    phone_number: str
    description: Optional[str]

    @validator("phone_number")
    def phone_number_must_have_10_digits(cls, v):
        match = re.match(r"0\d{9}", v)
        if (match is None) or (len(v) < 10):
            raise ValueError("Phone number must have 10 digits")
        return v


class User(UserBase, table=True):
    uuid: Optional[UUID] = Field(
        default_factory=uuid4,
        primary_key=True,
        sa_column_kwargs={"server_default": text("uuid_generate_v4()")},
    )

    password_hash: bytes

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


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    uuid: UUID
    created_at: datetime
    updated_at: datetime


class UserUpdate(SQLModel):
    username: Optional[str]
    email: Optional[str]
    phone_number: Optional[str]
    password: Optional[str]
    name: Optional[str]
    identity_number: Optional[int]
    identity_type: Optional[IdentityType]
    phone_number: Optional[str]
    description: Optional[str]

from sqlmodel import SQLModel, Field
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy.sql.expression import text
from pydantic import EmailStr, validator
import re

from app.models.address import AddressCreate, AddressRead, AddressUpdate


class BranchBase(SQLModel):
    name: str
    phone_number: str
    description: Optional[str]


class Branch(BranchBase, table=True):
    uuid: Optional[UUID] = Field(
        default_factory=uuid4,
        primary_key=True,
        sa_column_kwargs={"server_default": text("uuid_generate_v4()")},
    )

    address_uuid: UUID = Field(foreign_key="address.uuid")

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

class BranchCreate(BranchBase):
    address: AddressCreate

class BranchRead(BranchBase):
    uuid: UUID
    address: AddressRead
    created_at: datetime
    updated_at: datetime

class BranchUpdate(SQLModel):
    name: Optional[str]
    phone_number: Optional[str]
    description: Optional[str]
    address: Optional[AddressUpdate]
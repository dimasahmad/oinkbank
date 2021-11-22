from sqlmodel import SQLModel, Field
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy.sql.expression import text
from pydantic import EmailStr, validator
import re


class AddressBase(SQLModel):
    address: str
    rt: int
    rw: int
    subdistrict_uuid: UUID = Field(foreign_key="area.uuid")
    district_uuid: UUID = Field(foreign_key="area.uuid")
    city_uuid: UUID = Field(foreign_key="area.uuid")
    province_uuid: UUID = Field(foreign_key="area.uuid")


class Address(AddressBase, table=True):
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

class AddressCreate(AddressBase):
    pass

class AddressRead(AddressBase):
    uuid: UUID
    created_at: datetime
    updated_at: datetime

class AddressUpdate(SQLModel):
    address: Optional[str]
    rt: Optional[int]
    rw: Optional[int]
    subdistrict_uuid: Optional[UUID]
    district_uuid: Optional[UUID]
    city_uuid: Optional[UUID]
    province_uuid: Optional[UUID]
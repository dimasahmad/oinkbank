import re
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy.orm.relationships import RelationshipProperty, foreign, remote
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import text
from pydantic import EmailStr, validators
from typing import TYPE_CHECKING, Optional

from app.models.area import Area, AreaBase, AreaRead

if TYPE_CHECKING:
    from app.models.branch import Branch
    from app.models.user import User
    from app.models.area import Area


class AddressBase(SQLModel):
    address: str
    rt: int
    rw: int


class Address(AddressBase, table=True):
    subdistrict_uuid: UUID = Field(foreign_key="area.uuid")
    district_uuid: UUID = Field(foreign_key="area.uuid")
    city_uuid: UUID = Field(foreign_key="area.uuid")
    province_uuid: UUID = Field(foreign_key="area.uuid")

    province: Area = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "remote(Area.uuid) == foreign(Address.province_uuid)"
        }
    )
    city: Area = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "remote(Area.uuid) == foreign(Address.city_uuid)"
        }
    )
    district: Area = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "remote(Area.uuid) == foreign(Address.district_uuid)"
        }
    )
    subdistrict: Area = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "remote(Area.uuid) == foreign(Address.subdistrict_uuid)"
        }
    )

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

    user: Optional["User"] = Relationship(back_populates="address")
    branch: Optional["Branch"] = Relationship(back_populates="address")


class AddressCreate(AddressBase):
    subdistrict_uuid: UUID
    district_uuid: UUID
    city_uuid: UUID
    province_uuid: UUID


class AddressRead(AddressBase):
    subdistrict: AreaRead
    district: AreaRead
    city: AreaRead
    province: AreaRead

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

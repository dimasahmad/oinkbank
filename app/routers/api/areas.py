from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select
from app.dependencies import engine
from app.models.area import Area
from typing import List
from uuid import UUID

router = APIRouter()


@router.get("", response_model=List[Area])
def index(parent_uuid: UUID = None):
    with Session(engine) as session:
        statement = (
            select(Area)
            .where(Area.parent_uuid == parent_uuid, Area.deleted_at == None)
            .order_by(Area.name)
        )
        result = session.exec(statement).all()

        return result


@router.get("/{uuid}", response_model=Area)
def read(uuid: UUID):
    with Session(engine) as session:
        statement = (
            select(Area)
            .where(Area.parent_uuid == uuid, Area.deleted_at == None)
            .order_by(Area.name)
        )
        area = session.exec(statement).one_or_none()
        if not area:
            raise HTTPException(status_code=404, detail="Resource not found")

        return area

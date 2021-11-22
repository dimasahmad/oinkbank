from fastapi import APIRouter
from sqlmodel import Session, select
from app.dependencies import engine
from app.models.area import Area
from typing import List
from uuid import UUID

router = APIRouter()


@router.get("", response_model=List[Area])
def index(parent_uuid: UUID = None):
    with Session(engine) as session:
        statement = select(Area).where(Area.parent_uuid == parent_uuid, Area.deleted_at == None).order_by(Area.name)
        result = session.exec(statement).all()

        return result

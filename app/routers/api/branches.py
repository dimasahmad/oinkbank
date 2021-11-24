from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select
from typing import List
from uuid import UUID

from app.dependencies import db_session, engine, authenticate_user

from app.models.branch import Branch, BranchCreate, BranchRead, BranchUpdate
from app.models.address import Address
from app.models.user import User, UserRole


router = APIRouter()


@router.post("", response_model=BranchRead)
def create(
    create: BranchCreate,
    current_user: User = Depends(authenticate_user),
    session: Session = Depends(db_session),
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    # TODO: Find a way to use simple relation create, ex:
    # >>> Branch.from_orm(create)
    branch = Branch(**create.dict(exclude={"address": ...}))
    branch.address = Address(**create.address.dict())

    session.add(branch)
    session.commit()
    session.refresh(branch)

    return branch


@router.get("", response_model=List[BranchRead])
def index(session: Session = Depends(db_session)):
    statement = select(Branch).where(Branch.deleted_at == None)

    return session.exec(statement).all()


@router.get("/{uuid}", response_model=BranchRead)
def read(uuid: UUID, session: Session = Depends(db_session)):
    statement = (
        select(Branch, Address)
        .join(Address)
        .where(Branch.uuid == uuid, Branch.deleted_at == None)
    )
    branch, address = session.exec(statement).one_or_none()
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resourse not found"
        )

    return BranchRead(**branch.dict(), address=address)


@router.patch("/{uuid}", response_model=BranchRead)
def update(
    uuid: UUID,
    branch_update: BranchUpdate,
    current_user: User = Depends(authenticate_user),
    session: Session = Depends(db_session),
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    statement = (
        select(Branch, Address)
        .join(Address)
        .where(Branch.uuid == uuid, Branch.deleted_at == None)
    )
    branch, address = session.exec(statement).one_or_none()
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found"
        )

    branch_data = branch_update.dict(exclude_unset=True)
    for key, value in branch_data.items():
        if key == "address":
            address_data = value
            for k, v in address_data.items():
                setattr(address, k, v)

            address.updated_at = "now()"

            session.add(address)
            session.commit()
            session.refresh(address)

            continue

        setattr(branch, key, value)

    branch.updated_at = "now()"

    session.add(branch)
    session.commit()
    session.refresh(branch)

    return BranchRead(**branch.dict(), address=address)


@router.delete("/{uuid}")
def delete(
    uuid: UUID,
    current_user: User = Depends(authenticate_user),
    session: Session = Depends(db_session),
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    statement = (
        select(Branch, Address)
        .join(Address)
        .where(Branch.uuid == uuid, Branch.deleted_at == None)
    )
    branch, address = session.exec(statement).one_or_none()
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found"
        )

    # let the SQL server do the time calculation
    branch.deleted_at = "now()"
    address.deleted_at = "now()"

    session.add(branch)
    session.add(address)
    session.commit()

    return None, status.HTTP_204_NO_CONTENT

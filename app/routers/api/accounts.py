from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from sqlmodel import Session, select
from typing import List
from uuid import UUID

from app.dependencies import db_session, engine, authenticate_user
from app.models.account import Account, AccountCreate, AccountRead, AccountUpdate
from app.models.user import User, UserRole


router = APIRouter()


@router.post("", response_model=AccountRead)
def create(
    create: AccountCreate,
    current_user: User = Depends(authenticate_user),
    session: Session = Depends(db_session),
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    account = Account.from_orm(create)

    session.add(account)
    session.commit()
    session.refresh(account)

    return account


@router.get("", response_model=List[AccountRead])
def index(
    current_user: User = Depends(authenticate_user),
    session: Session = Depends(db_session),
):
    statement = select(Account).where(Account.deleted_at == None)

    return session.exec(statement).all()


@router.get("/{uuid}", response_model=AccountRead)
def read(
    uuid: UUID,
    current_user: User = Depends(authenticate_user),
    session: Session = Depends(db_session),
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    statement = select(Account).where(Account.uuid == uuid, Account.deleted_at == None)
    account = session.exec(statement).one_or_none()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found"
        )

    return account


@router.patch("/{uuid}", response_model=AccountRead)
def update(
    uuid: UUID,
    update: AccountUpdate,
    current_user: User = Depends(authenticate_user),
    session: Session = Depends(db_session),
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    statement = select(Account).where(Account.uuid == uuid, Account.deleted_at == None)
    account = session.exec(statement).one_or_none()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found"
        )

    account_data = update.dict(exclude_unset=True)
    for key, value in account_data.items():
        setattr(account, key, value)
    account.updated_at = "now()"

    session.add(account)
    session.commit()
    session.refresh(account)

    return account


@router.delete("/{uuid}")
def delete(
    uuid: UUID,
    current_user: User = Depends(authenticate_user),
    session: Session = Depends(db_session),
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    statement = select(Account).where(Account.uuid == uuid, Account.deleted_at == None)
    account = session.exec(statement).one_or_none()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found"
        )

    account.deleted_at = "now()"  # let the SQL server do the time calculation

    session.add(account)
    session.commit()

    return None, status.HTTP_204_NO_CONTENT

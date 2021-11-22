from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select
from app.dependencies import engine
from app.models.account import Account, AccountCreate, AccountRead, AccountUpdate
from typing import List
from uuid import UUID


router = APIRouter()


@router.post("", response_model=AccountRead)
def create(account_create: AccountCreate):
    with Session(engine) as session:
        account = Account(**account_create.dict())

        session.add(account)
        session.commit()
        session.refresh(account)

        return account


@router.get("", response_model=List[AccountRead])
def index():
    with Session(engine) as session:
        statement = select(Account).where(Account.deleted_at == None)

        return session.exec(statement).all()


@router.get("/{uuid}", response_model=AccountRead)
def read(uuid: UUID):
    with Session(engine) as session:
        statement = select(Account).where(Account.uuid == uuid, Account.deleted_at == None)
        account = session.exec(statement).one_or_none()
        if not account:
            raise HTTPException(status_code=404, detail="Resource not found")

        return account


@router.patch("/{uuid}", response_model=AccountRead)
def update(uuid: UUID, account_update: AccountUpdate):
    with Session(engine) as session:
        statement = select(Account).where(Account.uuid == uuid, Account.deleted_at == None)
        account = session.exec(statement).one_or_none()
        if not account:
            raise HTTPException(status_code=404, detail="Resource not found")

        account_data = account_update.dict(exclude_unset=True)
        for key, value in account_data.items():
            setattr(account, key, value)
        account.updated_at = "now()"

        session.add(account)
        session.commit()
        session.refresh(account)

        return account


@router.delete("/{uuid}")
def delete(uuid: UUID):
    with Session(engine) as session:
        statement = select(Account).where(Account.uuid == uuid, Account.deleted_at == None)
        account = session.exec(statement).one_or_none()
        if not account:
            raise HTTPException(status_code=404, detail="Resource not found")

        account.deleted_at = "now()"  # let the SQL server do the time calculation

        session.add(account)
        session.commit()

        return None, 204

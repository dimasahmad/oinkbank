from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select
from app.dependencies import engine
from app.models.transaction import Transaction, TransactionCreate, TransactionRead, TransactionUpdate
from typing import List
from uuid import UUID


router = APIRouter()


@router.post("", response_model=TransactionRead)
def create(transaction_create: TransactionCreate):
    with Session(engine) as session:
        transaction = Transaction(**transaction_create.dict())

        session.add(transaction)
        session.commit()
        session.refresh(transaction)

        return transaction


@router.get("", response_model=List[TransactionRead])
def index():
    with Session(engine) as session:
        statement = select(Transaction).where(Transaction.deleted_at == None)

        return session.exec(statement).all()


@router.get("/{uuid}", response_model=TransactionRead)
def read(uuid: UUID):
    with Session(engine) as session:
        statement = select(Transaction).where(Transaction.uuid == uuid, Transaction.deleted_at == None)
        transaction = session.exec(statement).one_or_none()
        if not transaction:
            raise HTTPException(status_code=404, detail="Resource not found")

        return transaction


@router.patch("/{uuid}", response_model=TransactionRead)
def update(uuid: UUID, transaction_update: TransactionUpdate):
    with Session(engine) as session:
        statement = select(Transaction).where(Transaction.uuid == uuid, Transaction.deleted_at == None)
        transaction = session.exec(statement).one_or_none()
        if not transaction:
            raise HTTPException(status_code=404, detail="Resource not found")

        transaction_data = transaction_update.dict(exclude_unset=True)
        for key, value in transaction_data.items():
            setattr(transaction, key, value)
        transaction.updated_at = "now()"

        session.add(transaction)
        session.commit()
        session.refresh(transaction)

        return transaction


@router.delete("/{uuid}")
def delete(uuid: UUID):
    with Session(engine) as session:
        statement = select(Transaction).where(Transaction.uuid == uuid, Transaction.deleted_at == None)
        transaction = session.exec(statement).one_or_none()
        if not transaction:
            raise HTTPException(status_code=404, detail="Resource not found")

        transaction.deleted_at = "now()"  # let the SQL server do the time calculation

        session.add(transaction)
        session.commit()

        return None, 204

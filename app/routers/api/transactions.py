from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from pydantic.schema import model_schema
from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID

from app.dependencies import db_session, engine, authenticate_user
from app.models.account import Account
from app.models.transaction import (
    Transaction,
    TransactionCreate,
    TransactionRead,
    TransactionType,
)
from app.models.user import User, UserRole


router = APIRouter()


@router.post("", response_model=TransactionRead)
def create(
    account_uuid: UUID,
    create: TransactionCreate,
    current_user: User = Depends(authenticate_user),
    session: Session = Depends(db_session),
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    statement = select(Account).where(
        Account.uuid == account_uuid, Account.deleted_at == None
    )
    account = session.exec(statement).one_or_none()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found"
        )

    transaction: Transaction = Transaction(
        **create.dict(exclude={"transfer": ...}), account_uuid=account.uuid
    )

    if transaction.type == TransactionType.DEPOSIT:
        account.balance += transaction.amount
        if account.balance < account.minimum_balance:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Balance too low"
            )

    if (
        transaction.type == TransactionType.WITHDRAWAL
        or transaction.type == TransactionType.TRANSFER
    ):
        account.balance -= transaction.amount
        if account.balance < account.minimum_balance:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient funds"
            )

        if transaction.type == TransactionType.TRANSFER:
            transaction.details = f"Transfer to {create.transfer.account_number}"
            dest = session.exec(
                select(Account).where(
                    Account.number == create.transfer.account_number,
                    Account.deleted_at == None,
                )
            ).one_or_none()
            if not dest:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Transfer destination not found",
                )
            dest.balance += transaction.amount
            dest.updated_at = "now()"
            session.add(dest)
            session.commit()

    account.updated_at = "now()"
    session.add(account)
    session.commit()

    session.add(transaction)
    session.commit()
    session.refresh(transaction)

    return transaction


@router.get("", response_model=List[TransactionRead])
def index(
    account_uuid: UUID,
    current_user: User = Depends(authenticate_user),
    session: Session = Depends(db_session),
):
    statement = select(Transaction).where(
        Transaction.account_uuid == account_uuid, Transaction.deleted_at == None
    )

    return session.exec(statement).all()


@router.get("/{uuid}", response_model=TransactionRead)
def read(
    uuid: UUID,
    account_uuid: UUID,
    current_user: User = Depends(authenticate_user),
    session: Session = Depends(db_session),
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    statement = select(Transaction).where(
        Transaction.account_uuid == account_uuid,
        Transaction.uuid == uuid,
        Transaction.deleted_at == None,
    )
    transaction = session.exec(statement).one_or_none()
    if not transaction:
        raise HTTPException(status_code=404, detail="Resource not found")

    return transaction


@router.delete("/{uuid}")
def delete(
    uuid: UUID,
    account_uuid: UUID,
    current_user: User = Depends(authenticate_user),
    session: Session = Depends(db_session),
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    statement = select(Transaction).where(
        Transaction.account_uuid == account_uuid,
        Transaction.uuid == uuid,
        Transaction.deleted_at == None,
    )
    transaction = session.exec(statement).one_or_none()
    if not transaction:
        raise HTTPException(status_code=404, detail="Resource not found")

    transaction.deleted_at = "now()"  # let the SQL server do the time calculation

    session.add(transaction)
    session.commit()

    return None, status.HTTP_204_NO_CONTENT

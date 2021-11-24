from datetime import date, datetime, timedelta, time
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select
from sqlalchemy import func
from typing import List, Optional
from uuid import UUID

from app.dependencies import db_session, engine, authenticate_user
from app.models.address import Address
from app.models.branch import Branch, BranchRead
from app.models.account import Account
from app.models.transaction import Transaction, TransactionType
from app.models.report import AccountInactive, AccountsUsers, BranchReport, Transactions
from app.models.user import User, UserRole


router = APIRouter()


@router.get("/accounts_users", response_model=AccountsUsers)
def branches(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(authenticate_user),
    session: Session = Depends(db_session),
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    accounts_stmt = select(func.count(Account.uuid).label("account_count"))
    users_stmt = select(func.count(User.uuid).label("users_count"))

    if start_date:
        accounts_stmt = accounts_stmt.where(
            Account.created_at >= datetime.combine(start_date, time(0, 0, 0))
        )
        users_stmt = users_stmt.where(
            User.created_at >= datetime.combine(start_date, time(0, 0, 0))
        )
    if end_date:
        accounts_stmt = accounts_stmt.where(
            Account.created_at <= datetime.combine(end_date, time(0, 0, 0))
        )
        users_stmt = users_stmt.where(
            User.created_at <= datetime.combine(end_date, time(0, 0, 0))
        )

    return AccountsUsers(
        accounts_count=session.exec(accounts_stmt).one(),
        users_count=session.exec(users_stmt).one(),
    )


@router.get("/transactions", response_model=Transactions)
def branches(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(authenticate_user),
    session: Session = Depends(db_session),
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    deposits_stmt = select(
        func.count(Transaction.amount).label("deposits_count"),
        func.sum(Transaction.amount).label("deposits_total"),
    ).where(Transaction.type == TransactionType.DEPOSIT)
    withdrawals_stmt = select(
        func.count(Transaction.amount).label("withdrawals_count"),
        func.sum(Transaction.amount).label("withdrawals_total"),
    ).where(Transaction.type == TransactionType.WITHDRAWAL)

    if start_date:
        deposits_stmt = deposits_stmt.where(
            Transaction.created_at >= datetime.combine(start_date, time(0, 0, 0))
        )
        withdrawals_stmt = withdrawals_stmt.where(
            Transaction.created_at >= datetime.combine(start_date, time(0, 0, 0))
        )
    if end_date:
        deposits_stmt = deposits_stmt.where(
            Transaction.created_at >= datetime.combine(start_date, time(0, 0, 0))
        )
        withdrawals_stmt = withdrawals_stmt.where(
            Transaction.created_at >= datetime.combine(start_date, time(0, 0, 0))
        )

    deposits_count, deposits_total = session.exec(deposits_stmt).one()
    withdrawals_count, withdrawals_total = session.exec(withdrawals_stmt).one()

    return Transactions(
        deposits_count=deposits_count,
        deposits_total=deposits_total,
        withdrawals_count=withdrawals_count,
        withdrawals_total=withdrawals_total,
    )


@router.get("/total_balance")
def branches(
    current_user: User = Depends(authenticate_user),
    session: Session = Depends(db_session),
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    balance_stmt = select(func.sum(Account.balance).label("balance_total")).where(Account.deleted_at == None)

    return {"balance_total": session.exec(balance_stmt).one()}


@router.get("/inactive_accounts", response_model=List[AccountInactive])
def accounts(
    current_user: User = Depends(authenticate_user),
    session: Session = Depends(db_session),
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    statement = select(Account).where(
        Account.updated_at < datetime.utcnow() - timedelta(days=90),
        Account.deleted_at == None,
    )
    result = [
        AccountInactive(
            account=account, days_inactive=(datetime.utcnow() - account.updated_at).days
        )
        for account in session.exec(statement).all()
    ]

    return result

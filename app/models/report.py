from sqlmodel import SQLModel, Field, text
from typing import List, Optional, Union
from uuid import UUID, uuid4
from datetime import date, datetime
from pydantic import EmailStr, validator
import re
from app.models.account import AccountRead

from app.models.user import User, UserRead


class AccountsUsers(SQLModel):
    accounts_count: int
    users_count: int


class Transactions(SQLModel):
    deposits_count: int
    deposits_total: float
    withdrawals_count: int
    withdrawals_total: float


class AccountInactive(SQLModel):
    account: AccountRead
    days_inactive: int

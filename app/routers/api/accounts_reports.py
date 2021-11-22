from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select
from app.dependencies import engine
from app.models.transaction import Transaction, TransactionCreate, TransactionRead, TransactionUpdate
from typing import List
from uuid import UUID


router = APIRouter()
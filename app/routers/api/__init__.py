from fastapi import APIRouter
from . import reports, users, branches, accounts, transactions, areas, token

api = APIRouter()

api.include_router(users.router, prefix="/users", tags=["users"])
api.include_router(branches.router, prefix="/branches", tags=["branches"])
api.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
api.include_router(transactions.router, prefix="/accounts/{account_uuid}/transactions", tags=["transactions"])
api.include_router(reports.router, prefix="/reports", tags=["branches", "reports"])

api.include_router(areas.router, prefix="/areas", tags=["areas"])

# Authentication endpoint
api.include_router(token.router, prefix="/token")

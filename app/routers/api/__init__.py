from fastapi import APIRouter
from . import users, branches, branches_reports, accounts, accounts_reports, transactions, areas

api = APIRouter()
api.include_router(users.router, prefix="/users", tags=["users"])
api.include_router(branches.router, prefix="/branches", tags=["branches"])
# api.include_router(branches_reports, prefix="/brances/reports", tags=["branches", "reports"])
api.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
# api.include_router(accounts_reports.router, prefix="/accounts/reports", tags=["accounts", "reports"])
api.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api.include_router(areas.router, prefix="/areas", tags=["areas"])

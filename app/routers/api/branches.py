from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select
from app.dependencies import engine
from app.models.branch import Branch, BranchCreate, BranchRead, BranchUpdate
from app.models.address import Address
from typing import List
from uuid import UUID


router = APIRouter()


@router.post("", response_model=BranchRead)
def create(branch_create: BranchCreate):
    with Session(engine) as session:
        address = Address(**branch_create.address.dict())
        session.add(address)
        session.commit()
        session.refresh(address)

        branch = Branch(**branch_create.dict(), address_uuid=address.uuid)
        session.add(branch)
        session.commit()
        session.refresh(branch)

    return BranchRead(**branch.dict(), address=address)


@router.get("", response_model=List[BranchRead])
def index():
    with Session(engine) as session:
        statement = (
            select(Branch, Address).join(Address).where(Branch.deleted_at == None)
        )

        return [
            BranchRead(**branch.dict(), address=address)
            for branch, address in session.exec(statement)
        ]


@router.get("/{uuid}", response_model=BranchRead)
def read(uuid: UUID):
    with Session(engine) as session:
        statement = (
            select(Branch, Address)
            .join(Address)
            .where(Branch.uuid == uuid, Branch.deleted_at == None)
        )
        branch, address = session.exec(statement).one()

        return BranchRead(**branch.dict(), address=address)


@router.patch("/{uuid}", response_model=BranchRead)
def update(uuid: UUID, branch_update: BranchUpdate):
    with Session(engine) as session:
        statement = (
            select(Branch, Address)
            .join(Address)
            .where(Branch.uuid == uuid, Branch.deleted_at == None)
        )
        branch, address = session.exec(statement).one_or_none()
        if not branch:
            raise HTTPException(status_code=404, detail="Branch not found")

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
def delete(uuid: UUID):
    with Session(engine) as session:
        statement = (
            select(Branch, Address)
            .join(Address)
            .where(Branch.uuid == uuid, Branch.deleted_at == None)
        )
        branch, address = session.exec(statement).one_or_none()
        if not branch:
            raise HTTPException(status_code=404, detail="Branch not found")

        # let the SQL server do the time calculation
        branch.deleted_at = "now()"
        address.deleted_at = "now()"

        session.add(branch)
        session.add(address)
        session.commit()

        return None, 204

from datetime import datetime
from typing import List
from uuid import UUID
from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from app.dependencies import engine, pwd
from app.models.user import User, UserCreate, UserRead, UserUpdate

router = APIRouter()


@router.post("", response_model=UserRead)
def create(user_create: UserCreate):
    """Create a new user"""
    with Session(engine) as session:
        password_hash = pwd.hash(user_create.password)
        user = User(**user_create.dict(), password_hash=password_hash)

        session.add(user)
        session.commit()
        session.refresh(user)

        return user


@router.get("", response_model=List[UserRead])
def index():
    """Get all users"""
    with Session(engine) as session:
        statement = select(User).where(User.deleted_at == None)

        return session.exec(statement).all()


@router.get("/{uuid}", response_model=UserRead)
def read(uuid: UUID):
    """Get a user"""
    with Session(engine) as session:
        statement = select(User).where(User.uuid == uuid, User.deleted_at == None)
        user = session.exec(statement).one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user


@router.patch("/{uuid}", response_model=UserRead)
def update(uuid: UUID, user_update: UserUpdate):
    """Update a user"""
    with Session(engine) as session:
        statement = select(User).where(User.uuid == uuid, User.deleted_at == None)
        user = session.exec(statement).one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user_data = user_update.dict(exclude_unset=True)
        for key, value in user_data.items():
            if key == "password":
                key = "password_hash"
                value = str(pwd.hash(value)).encode()
            setattr(user, key, value)
        user.updated_at = "now()"

        session.add(user)
        session.commit()
        session.refresh(user)

        return user


@router.delete("/{uuid}")
def delete(uuid: UUID):
    """User soft-delete"""
    with Session(engine) as session:
        statement = select(User).where(User.uuid == uuid, User.deleted_at == None)
        user = session.exec(statement).one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.deleted_at = "now()"  # let the SQL server do the time calculation

        session.add(user)
        session.commit()

        return None, 204

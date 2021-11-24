from typing import List
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session, select

from app.dependencies import db_session, engine, pwd, authenticate_user
from app.models.user import User, UserCreate, UserRead, UserRole, UserUpdate


router = APIRouter()


@router.post("", response_model=UserRead)
def create(user_create: UserCreate, session: Session = Depends(db_session)):
    password_hash = pwd.hash(user_create.password)
    user = User(**user_create.dict(), password_hash=password_hash)

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@router.get("", response_model=List[UserRead])
def index(
    current_user: User = Depends(authenticate_user),
    session: Session = Depends(db_session),
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    statement = select(User).where(
        User.role <= UserRole.CONSUMER, User.deleted_at == None
    )

    return session.exec(statement).all()


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(authenticate_user)):
    return current_user


@router.get("/{uuid}", response_model=UserRead)
def read(
    uuid: UUID,
    current_user: User = Depends(authenticate_user),
    session: Session = Depends(db_session),
):
    if current_user.uuid != uuid and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    statement = select(User).where(User.uuid == uuid, User.deleted_at == None)
    user = session.exec(statement).one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found"
        )

    return user


@router.patch("/me", response_model=UserRead)
def update_me(
    user_update: UserUpdate,
    current_user: User = Depends(authenticate_user),
    session: Session = Depends(db_session),
):
    statement = select(User).where(
        User.uuid == current_user.uuid, User.deleted_at == None
    )
    user = session.exec(statement).one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found"
        )

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


@router.patch("/{uuid}", response_model=UserRead)
def update(
    uuid: UUID,
    user_update: UserUpdate,
    current_user: User = Depends(authenticate_user),
    session: Session = Depends(db_session),
):
    if current_user.uuid != uuid and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    statement = select(User).where(User.uuid == uuid, User.deleted_at == None)
    user = session.exec(statement).one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found"
        )

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
def delete(
    uuid: UUID,
    current_user: User = Depends(authenticate_user),
    session: Session = Depends(db_session),
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    statement = select(User).where(User.uuid == uuid, User.deleted_at == None)
    user = session.exec(statement).one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found"
        )

    user.deleted_at = "now()"  # let the SQL server do the time calculation

    session.add(user)
    session.commit()

    return None, status.HTTP_204_NO_CONTENT

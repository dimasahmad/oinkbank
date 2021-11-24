from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestFormStrict
from jose import jwt
from sqlmodel import Session, select
from app.dependencies import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    SECRET_KEY,
    TOKEN_ALGORITHM,
    db_session,
    engine,
    pwd,
)
from app.models.user import User


router = APIRouter()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=TOKEN_ALGORITHM)
    return encoded_jwt


@router.post("")
async def login(
    form_data: OAuth2PasswordRequestFormStrict = Depends(),
    session: Session = Depends(db_session),
):
    statement = select(User).where(
        User.username == form_data.username, User.deleted_at == None
    )
    user = session.exec(statement).one_or_none()

    # use a dummy hash if user not found to simulate time to hash a password
    password_hash = user.password_hash if user else pwd._dummy_hash
    if not pwd.verify(form_data.password, password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

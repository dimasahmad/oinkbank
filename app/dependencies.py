from fastapi import Depends, HTTPException, status
from sqlmodel import create_engine, Session, select
from jose import JWTError, jwt

from app.models.user import User


SQLALCHEMY_DATABASE_URI = "postgresql://bootcamp:bootcamp@localhost:5432/oinkbank"
SQLALCHEMY_TRACK_MODIFICATIONS = False

# openssl rand -hex 32
SECRET_KEY = "9c35f683e7f17dfe734294cc38895a79177bc330db6e63dc56328170c3aaf81c"
TOKEN_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)

def db_session():
    with Session(engine) as session:
        yield session

from passlib.context import CryptContext

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def authenticate_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[TOKEN_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    with Session(engine) as session:
        statement = select(User).where(
            User.username == username, User.deleted_at == None
        )
        user = session.exec(statement).one_or_none()
        if user is None:
            raise credentials_exception

        return user

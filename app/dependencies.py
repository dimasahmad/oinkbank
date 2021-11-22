SQLALCHEMY_DATABASE_URI = "postgresql://bootcamp:bootcamp@localhost:5432/oinkbank"
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECURITY_PASSWORD_HASH = "bcrypt"
SECURITY_PASSWORD_SALT = "118626655623976839892210812865932028617"

from sqlmodel import create_engine

engine = create_engine(
    "postgresql://bootcamp:bootcamp@localhost:5432/oinkbank", echo=True
)

from passlib.context import CryptContext

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

from datetime import datetime, timedelta, timezone
from typing import Annotated

import sqlalchemy.exc
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from sqlalchemy.orm import Session
from sqlalchemy import select, update

from db import get_session
from app.models.user import User, Role
from app.schemas.user import UserCreate, UserRead, UserUpdate
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, api_root
from log_utils import logger


class Token(BaseModel):
    access_token: str
    token_type: str
    role: int


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{api_root}/auth/jwt/login")

auth_router = APIRouter(prefix="/auth", tags=["鉴权"])


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str, db: Session):
    user = db.execute(select(User).where(User.username == username)).scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def current_user(token: Annotated[str, Depends(oauth2_scheme)],
                       db: Annotated[Session, Depends(get_session)]) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("id")
        if user_id is None:
            logger.error(f"current_user: failed to get user_id from token")
            raise credentials_exception
    except JWTError as e:
        logger.error(f"current_user: failed to decode jwt", exc_info=e)
        raise credentials_exception
    user = db.get(User, user_id)
    if user is None:
        raise credentials_exception
    return user


async def current_superuser(user: Annotated[User, Depends(current_user)]) -> User:
    if user.role != Role.Admin:
        logger.warn(f"auth: permission denied: {user}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You don't have permission to perform this action")
    return user


def create_user(user_dict: UserCreate, db: Session) -> UserRead:
    user = User(**user_dict.model_dump(exclude={'password'}),
                hashed_password=get_password_hash(user_dict.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    user_model = UserRead.model_validate(user)
    return user_model


@auth_router.post("/register")
def register(user_dict: UserCreate, db: Session = Depends(get_session)) -> UserRead:
    try:
        return create_user(user_dict, db)
    except sqlalchemy.exc.IntegrityError as e:
        logger.warn(f"register: probably username duplication", exc_info=e)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Duplicate username.")


@auth_router.post("/register_superuser", dependencies=[Depends(current_superuser)])
def register_superuser(user_dict: UserCreate, db: Session = Depends(get_session)) -> UserRead:
    user_schema = create_user(user_dict, db)
    db.execute(update(User).where(User.id == user_schema.id).values(role=Role.Admin))
    db.commit()
    user_schema.role = Role.Admin
    return user_schema


@auth_router.post("/jwt/login")
def login_for_access_token(
    user_dict: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_session)
) -> Token:
    user = authenticate_user(user_dict.username, user_dict.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "id": user.id}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer", role=user.role)


@auth_router.get("/me")
def read_users_me(user: Annotated[User, Depends(current_user)]) -> UserRead:
    return UserRead.model_validate(user)


@auth_router.patch("/me")
def update_users_me(user_dict: UserUpdate, user: User = Depends(current_user),
                    db: Session = Depends(get_session)) -> UserRead:
    if user_dict.password is not None:
        hashed_password = get_password_hash(user_dict.password)
        query = (update(User).where(User.id == user.id)
                 .values(hashed_password=hashed_password,
                         **user_dict.model_dump(exclude={"password"}, exclude_none=True)))
    else:
        query = (update(User).where(User.id == user.id)
                 .values(**user_dict.model_dump(exclude={"password"}, exclude_none=True)))
    db.execute(query)
    db.commit()
    user = db.get(User, user.id)
    return UserRead.model_validate(user)

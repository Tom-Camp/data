from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings
from app.models.users import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = settings.secret_key
ALGORITHM = settings.hash_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def role_checker(allowed_roles: List[str]):
    async def check_role(user: User = Depends(get_current_user)):
        if user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user

    return check_role


async def authenticate_user(username: str, password: str):
    user = await User.find_one(User.username == username)
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception: HTTPException = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        try:
            payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=ALGORITHM)
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.JWTClaimsError:
            raise HTTPException(status_code=401, detail="Invalid token")
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = await User.find_one(User.username == username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

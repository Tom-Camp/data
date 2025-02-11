from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings
from app.models.users import Role, User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = settings.secret_key
ALGORITHM = settings.hash_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = 30


async def authenticate_user(username: str, password: str):
    user = await User.find_one(User.username == username)
    if not user:
        return False
    if not pwd_context.verify(password, user.password):
        return False
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await User.find_one({"username": username})
    if user is None:
        raise credentials_exception
    return user


async def get_current_user_with_role(
    current_user: User = Depends(get_current_user),
    required_role: Role = Role.AUTHENTICATED,
) -> User:
    if required_role and current_user.role.value < required_role.value:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user


def require_role(required_role: Role):
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if required_role and current_user.role.value < required_role.value:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return current_user

    return role_checker


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    pwd_context,
    role_checker,
)
from app.models.users import User, UserCreate, UserList

router = APIRouter()


@router.post("/users", response_model=User)
async def create_user(
    new_user: UserCreate, user: User = Depends(role_checker(["admin"]))
):
    existing_user = await User.find_one(User.username == new_user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    existing_email = await User.find_one(User.email == new_user.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(new_user.password)

    new_user = User(
        username=new_user.username,
        email=new_user.email,
        hashed_password=hashed_password,
        role=new_user.role,
    )

    await new_user.insert()

    return new_user


@router.get("/users/{user_id}")
async def get_user(user_id: str):
    user = await User.get(user_id)
    return user


@router.get("/users", response_model=list[UserList])
async def list_users():
    users = await User.find_all().to_list()
    return users


@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})  # type: ignore[attr-defined]
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

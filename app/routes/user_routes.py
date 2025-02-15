from datetime import datetime, timezone

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from password_validator import PasswordValidator

from app.auth import authenticate_user, create_access_token, pwd_context, require_role
from app.models.users import Role, User, UserCreate, UserShow

router = APIRouter()

schema = PasswordValidator()
schema.min(10).max(
    100
).has().uppercase().has().lowercase().has().digits().has().symbols()


@router.post("/users", response_model=UserShow)
async def create_user(
    new_user: UserCreate, user: User = Depends(require_role(Role.ADMIN))
):
    existing_user = await User.find_one(User.username == new_user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    existing_email = await User.find_one(User.email == new_user.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    if not schema.validate(new_user.password):
        raise HTTPException(status_code=400, detail="Password not strong enough")

    hashed_password = pwd_context.hash(new_user.password)
    user = User(
        username=new_user.username,
        email=new_user.email,
        password=hashed_password,
        role=new_user.role,
    )
    await user.insert()

    return user


@router.get("/users/{user_id}", response_model=UserShow)
async def get_user(user_id: PydanticObjectId):
    user = await User.get(user_id)
    return user


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: PydanticObjectId, user: User = Depends(require_role(Role.ADMIN))
):
    existing_user = await User.get(user_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    await existing_user.delete()
    return {"message": "User deleted successfully"}


@router.put("/users/{user_id}", response_model=UserShow)
async def update_user(
    user_id: PydanticObjectId,
    updated_user: UserCreate,
    user: User = Depends(require_role(Role.ADMIN)),
):
    existing_user = await User.get(user_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = updated_user.model_dump(exclude_unset=True)
    update_data["password"] = pwd_context.hash(updated_user.password)
    update_data["updated_date"] = datetime.now(timezone.utc)

    update_query = {"$set": update_data}

    await existing_user.update(update_query)
    return await User.get(user_id)


@router.get("/users", response_model=list[UserShow])
async def list_users():
    users = await User.find_all().to_list()
    return users


@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/current/user", response_model=UserShow)
async def read_users_me(current_user: User = Depends(require_role(Role.AUTHENTICATED))):
    return current_user

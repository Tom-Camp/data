from contextlib import asynccontextmanager

from beanie import init_beanie
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from app.auth import pwd_context
from app.config import settings
from app.models.devices import Device
from app.models.journals import Journal
from app.models.users import Role, User
from app.routes import device_routes, journal_routes, user_routes


async def init_db():
    client = AsyncIOMotorClient(settings.mongodb_uri)
    await init_beanie(
        database=client[settings.mongo_db],
        document_models=[User, Journal, Device],
    )
    return client


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        client = await init_db()
        print(f"Connected to MongoDB. Database '{settings.mongo_db}' is ready.")

        default_user = await User.find_one(User.username == settings.initial_user_name)

        if not default_user:
            hashed_password = pwd_context.hash(settings.initial_user_pass)
            new_user = User(
                username=settings.initial_user_name,
                email=settings.initial_user_mail,
                hashed_password=hashed_password,
                role=Role.ADMIN,
            )
            await new_user.insert()
            print(f"Created default user: {settings.initial_user_name}")
        else:
            print(f"Default user {settings.initial_user_name} already exists")

        yield
    except Exception as e:
        print(f"Error during database initialization: {e}")
        raise
    finally:
        if "client" in locals():
            client.close()
            print("Closed MongoDB connection")


app = FastAPI(
    lifespan=lifespan,
    title=settings.app_name,
)

app.include_router(device_routes.router, prefix="/api")
app.include_router(journal_routes.router, prefix="/api")
app.include_router(user_routes.router, prefix="/api")

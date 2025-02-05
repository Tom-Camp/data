from contextlib import asynccontextmanager

from beanie import init_beanie
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from app.auth import pwd_context
from app.config import settings
from app.models.journals import Journal
from app.models.users import User
from app.routes import journal_routes, user_routes


async def init_db():
    client = AsyncIOMotorClient(settings.database_url)
    await init_beanie(
        database=client[settings.database_name],
        document_models=[User, Journal],
    )
    return client


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = await init_db()
    print(f"Connected to MongoDB. Database '{settings.database_name}' is ready.")

    db_list = await client.list_database_names()
    if settings.database_name not in db_list:
        hashed_password = pwd_context.hash(settings.initial_user_pass)
        new_user = User(
            username=settings.initial_user_name,
            email=settings.initial_user_mail,
            hashed_password=hashed_password,
        )
        await new_user.insert()

    yield
    client.close()
    print("Closed MongoDB connection")


app = FastAPI(
    lifespan=lifespan,
    title=settings.app_name,
)

app.include_router(journal_routes.router, prefix="/api")
app.include_router(user_routes.router, prefix="/api")

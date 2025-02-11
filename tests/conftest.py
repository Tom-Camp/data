import os
import sys

import pytest_asyncio
from beanie import init_beanie
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.auth import pwd_context  # noqa: E402
from app.main import app  # noqa: E402
from app.models.devices import Device, DeviceCreate  # noqa: E402
from app.models.journals import Journal  # noqa: E402
from app.models.users import Role, User  # noqa: E402


@pytest_asyncio.fixture(loop_scope="session", scope="session", autouse=True)
async def beanie_init():
    client = AsyncMongoMockClient()
    await init_beanie(
        database=client["testdb"],
        document_models=[User, Journal, Device, DeviceCreate],
    )
    return client


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def async_client(beanie_init):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def create_test_users(beanie_init):
    hashed_password = pwd_context.hash("password123")
    user_list: list[User] = []
    users: dict = {
        "admin": Role.ADMIN,
        "editor": Role.EDITOR,
        "auth": Role.AUTHENTICATED,
    }
    for username, role in users.items():
        user_list.append(
            User(
                username=f"{username}_user",
                email=f"{username}@example.com",
                password=hashed_password,
                role=role,
            )
        )
    await User.insert_many(user_list)

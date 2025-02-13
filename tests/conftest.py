import os
import sys

import pytest_asyncio
from beanie import init_beanie
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.auth import pwd_context  # noqa: E402
from app.main import app  # noqa: E402
from app.models.devices import Device  # noqa: E402
from app.models.journals import Journal  # noqa: E402
from app.models.users import Role, User  # noqa: E402


@pytest_asyncio.fixture(loop_scope="session", scope="session", autouse=True)
async def beanie_init():
    client = AsyncMongoMockClient()
    await init_beanie(
        database=client["testdb"],
        document_models=[User, Journal, Device],
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
    hashed_password = pwd_context.hash("Password!23")
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


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def journal_data():
    journal_data = {
        "title": "Test Journal",
        "description": "This is a test journal",
        "entries": [
            {
                "title": "Entry 1",
                "date": "2021-09-01",
                "body": "This is the first entry in the test journal",
                "location": "POINT (-81.0295357 34.927908)",
                "images": [
                    "/path/to/image.jpg",
                ],
            },
            {
                "title": "Entry 2",
                "date": "2021-09-01",
                "body": "This is the second entry in the test journal",
                "location": "POINT (-81.0295357 34.927908)",
                "images": [
                    "/path/to/another/image.jpg",
                ],
            },
        ],
    }
    return journal_data

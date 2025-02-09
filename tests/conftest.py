import os
import sys

import pytest
import pytest_asyncio
from beanie import init_beanie
from mongomock_motor import AsyncMongoMockClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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


@pytest.fixture(scope="session")
def user_create_data():
    return


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def create_test_users(beanie_init, user_create_data):
    user_list: list[User] = [
        User(
            username="admin_user",
            email="admin@example.com",
            password="password123",
            role=Role.ADMIN,
        ),
        User(
            username="editor_user",
            email="editor@example.com",
            password="password123",
            role=Role.EDITOR,
        ),
        User(
            username="auth_user",
            email="auth@example.com",
            password="password123",
            role=Role.AUTHENTICATED,
        ),
    ]
    await User.insert_many(user_list)

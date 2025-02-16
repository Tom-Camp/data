import os

import pytest
from fastapi import HTTPException

from app.auth import create_access_token, get_current_user
from app.config import Settings


@pytest.mark.asyncio
async def test_get_current_user_with_null_username():
    token = create_access_token(data={"sub": None})
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"
    assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}


@pytest.mark.asyncio
async def test_get_current_user_with_invalid_username():
    token = create_access_token(data={"sub": "invalid_user"})
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"
    assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}


@pytest.mark.asyncio
async def test_mongodb_uri():
    os.environ["MONGO_DB"] = "mongo_api"
    os.environ["MONGO_HOST"] = "localhost"
    os.environ["MONGO_PASS"] = "test"
    os.environ["MONGO_PORT"] = "27017"
    os.environ["MONGO_USER"] = "tester"
    os.environ["DB_USER"] = "testuser"
    os.environ["DB_PASS"] = "test_pass"
    settings = Settings()
    assert (
        settings.mongodb_uri
        == "mongodb://testuser:test_pass@localhost:27017/mongo_api?authSource=admin"
    )

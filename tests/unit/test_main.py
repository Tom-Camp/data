from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from app.models.users import Role


@pytest.fixture(scope="function")
def mock_settings():
    settings = MagicMock()
    settings.mongodb_uri = "mongodb://testdb:27017"
    settings.mongo_db = "test_db"
    settings.initial_user_name = "admin"
    settings.initial_user_mail = "admin@example.com"
    settings.initial_user_pass = "password123"
    return settings


@pytest.fixture(scope="function")
def mock_client():
    client = AsyncMock(spec=AsyncIOMotorClient)
    client.__getitem__.return_value = AsyncMock()
    return client


@pytest.mark.asyncio
async def test_init_db_successful(mock_settings):
    with (
        patch("app.main.AsyncIOMotorClient") as mock_motor_client,
        patch("app.main.init_beanie") as mock_init_beanie,
        patch("app.main.settings", mock_settings),
    ):
        mock_instance = AsyncMock()
        mock_motor_client.return_value = mock_instance
        mock_init_beanie.return_value = None

        from app.main import init_db

        result = await init_db()

        mock_motor_client.assert_called_once_with(mock_settings.mongodb_uri)
        mock_init_beanie.assert_called_once()
        assert result == mock_instance


@pytest.mark.asyncio
async def test_lifespan_new_user_creation(mock_settings, mock_client):
    app = FastAPI()

    with (
        patch("app.main.init_db", return_value=mock_client),
        patch("app.main.settings", mock_settings),
        patch("app.main.pwd_context.hash", return_value="hashed_password"),
        patch("app.main.User") as mock_user_model,
    ):
        mock_user_model.find_one = AsyncMock(return_value=None)

        mock_instance = AsyncMock()
        mock_instance.insert = AsyncMock()
        mock_user_model.return_value = mock_instance

        from app.main import lifespan

        async with lifespan(app):
            mock_user_model.find_one.assert_called_once()

            mock_user_model.assert_called_once_with(
                username=mock_settings.initial_user_name,
                email=mock_settings.initial_user_mail,
                password="hashed_password",
                role=Role.ADMIN,
            )

            mock_instance.insert.assert_called_once()


@pytest.mark.asyncio
async def test_lifespan_existing_user(mock_settings, mock_client):
    app = FastAPI()

    with (
        patch("app.main.init_db", return_value=mock_client),
        patch("app.main.settings", mock_settings),
        patch("app.main.User") as mock_user_model,
    ):
        existing_user = MagicMock()
        mock_user_model.find_one = AsyncMock(return_value=existing_user)

        from app.main import lifespan

        async with lifespan(app):
            mock_user_model.find_one.assert_called_once()
            mock_user_model.assert_not_called()


@pytest.mark.asyncio
async def test_lifespan_database_error(mock_settings):
    app = FastAPI()

    with (
        patch("app.main.init_db", side_effect=Exception("Database connection failed")),
        patch("app.main.settings", mock_settings),
    ):
        from app.main import lifespan

        with pytest.raises(Exception) as exc_info:
            async with lifespan(app):
                pass

        assert str(exc_info.value) == "Database connection failed"


@pytest.mark.asyncio
async def test_lifespan_cleanup(mock_settings, mock_client):
    app = FastAPI()

    with (
        patch("app.main.init_db", return_value=mock_client),
        patch("app.main.settings", mock_settings),
        patch("app.main.User") as mock_user_model,
    ):
        mock_user_model.find_one = AsyncMock(return_value=None)

        mock_instance = AsyncMock()
        mock_instance.insert = AsyncMock()
        mock_user_model.return_value = mock_instance

        from app.main import lifespan

        async with lifespan(app):
            pass

        mock_client.close.assert_called_once()

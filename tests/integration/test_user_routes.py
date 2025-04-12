import pytest
from beanie import PydanticObjectId

from app.models.users import User


class TestUserRoutes:
    header: dict[str, str] = {"Content-Type": "application/json"}

    @pytest.mark.asyncio
    async def test_admin_login_token(self, create_test_users, async_client):
        user_data = {
            "username": "admin_user",
            "password": "Password!23",
        }
        response = await async_client.post(
            "/api/token",
            data=user_data,
        )
        assert "access_token" in response.json()
        self.header["Authorization"] = f"Bearer {response.json()['access_token']}"

    @pytest.mark.asyncio
    async def test_admin_create_user(self, create_test_users, async_client):
        user_data = {
            "username": "test_user_1",
            "password": "Password!23",
            "email": "test_user_1@example.com",
        }
        response = await async_client.post(
            "/api/users",
            headers=self.header,
            json=user_data,
        )
        assert response.json()["username"] == "test_user_1"

    @pytest.mark.asyncio
    async def test_admin_create_existing_user(self, create_test_users, async_client):
        user_data = {
            "username": "test_user_1",
            "password": "Password!23",
            "email": "test_user_1@example.com",
        }
        response = await async_client.post(
            "/api/users",
            headers=self.header,
            json=user_data,
        )
        assert response.json()["detail"] == "Username already registered"

    @pytest.mark.asyncio
    async def test_admin_create_existing_email(self, create_test_users, async_client):
        user_data = {
            "username": "test_user_2",
            "password": "Password!23",
            "email": "test_user_1@example.com",
        }
        response = await async_client.post(
            "/api/users",
            headers=self.header,
            json=user_data,
        )
        assert response.json()["detail"] == "Email already registered"

    @pytest.mark.asyncio
    async def test_admin_create_weak_email(self, create_test_users, async_client):
        user_data = {
            "username": "test_user_2",
            "password": "password123",
            "email": "test_user_2@example.com",
        }
        response = await async_client.post(
            "/api/users",
            headers=self.header,
            json=user_data,
        )
        assert response.json()["detail"] == "Password not strong enough"

    @pytest.mark.asyncio
    async def test_admin_get_user(self, create_test_users, async_client):
        user = await User.find_one(User.username == "test_user_1")
        response = await async_client.get(
            f"/api/users/{user.id}",
            headers=self.header,
        )
        assert response.json()["username"] == "test_user_1"

    @pytest.mark.asyncio
    async def test_admin_incorrect_user_id(self, create_test_users, async_client):
        response = await async_client.get(
            "/api/users/123456",
            headers=self.header,
        )
        assert response.json()["detail"] == "Invalid request data"

    @pytest.mark.asyncio
    async def test_admin_update_user(self, create_test_users, async_client):
        user = await User.find_one(User.username == "test_user_1")
        user_data = {
            "username": "test_user_1_updated",
            "email": user.email,
            "password": user.password,
        }
        response = await async_client.put(
            f"/api/users/{user.id}",
            headers=self.header,
            json=user_data,
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_admin_update_nonexistant_user(self, create_test_users, async_client):
        pid = PydanticObjectId()
        user_data = {
            "username": "test_user_1_updated",
            "email": "test_user@example.com",
            "password": "Password!23",
        }
        response = await async_client.put(
            f"/api/users/{str(pid)}",
            headers=self.header,
            json=user_data,
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_admin_delete_user(self, create_test_users, async_client):
        user = await User.find_one(User.username == "test_user_1_updated")
        response = await async_client.delete(
            f"/api/users/{user.id}",
            headers=self.header,
        )
        assert response.json()["message"] == "User deleted successfully"

    @pytest.mark.asyncio
    async def test_admin_delete_nonexistant_user(self, create_test_users, async_client):
        pid = PydanticObjectId()
        response = await async_client.delete(
            f"/api/users/{str(pid)}",
            headers=self.header,
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_admin_get_current_user(self, async_client):
        response = await async_client.get(
            "/api/current/user",
            headers=self.header,
        )
        assert response.json()["username"] == "admin_user"

    @pytest.mark.asyncio
    async def test_nonadmin_login_token(self, create_test_users, async_client):
        for user in ["editor_user", "auth_user"]:
            user_data = {
                "username": user,
                "password": "Password!23",
            }
            response = await async_client.post(
                "/api/token",
                data=user_data,
            )
            assert "access_token" in response.json()

    @pytest.mark.asyncio
    async def test_nonadmin_create_user(self, create_test_users, async_client):
        for user in ["editor_user", "auth_user"]:
            user_data = {
                "username": user,
                "password": "Password!23",
            }
            response = await async_client.post(
                "/api/token",
                data=user_data,
            )
            self.header["Authorization"] = f"Bearer {response.json()['access_token']}"
            user_data = {
                "username": "test_user_3",
                "password": "Password!23",
                "email": "test_user_3@example.com",
            }
            response = await async_client.post(
                "/api/users",
                headers=self.header,
                json=user_data,
            )
            assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_nonadmin_get_user(self, create_test_users, async_client):
        for user in ["editor_user", "auth_user"]:
            user_data = {
                "username": user,
                "password": "Password!23",
            }
            response = await async_client.post(
                "/api/token",
                data=user_data,
            )
            self.header["Authorization"] = f"Bearer {response.json()['access_token']}"
            user = await User.find_one(User.username == "admin_user")
            response = await async_client.get(
                f"/api/users/{user.id}",
                headers=self.header,
            )
            assert response.json()["username"] == "admin_user"

    @pytest.mark.asyncio
    async def test_nonadmin_update_user(self, create_test_users, async_client):
        for user in ["editor_user", "auth_user"]:
            user_data = {
                "username": user,
                "password": "Password!23",
            }
            response = await async_client.post(
                "/api/token",
                data=user_data,
            )
            self.header["Authorization"] = f"Bearer {response.json()['access_token']}"
            user = await User.find_one(User.username == "admin_user")
            user_data = {
                "username": "admin_user_updated",
                "email": user.email,
                "password": user.password,
            }
            response = await async_client.put(
                f"/api/users/{user.id}",
                headers=self.header,
                json=user_data,
            )
            assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_nonadmin_delete_user(self, create_test_users, async_client):
        for user in ["editor_user", "auth_user"]:
            user_data = {
                "username": user,
                "password": "Password!23",
            }
            response = await async_client.post(
                "/api/token",
                data=user_data,
            )
            self.header["Authorization"] = f"Bearer {response.json()['access_token']}"
            user = await User.find_one(User.username == "admin_user")
            response = await async_client.delete(
                f"/api/users/{user.id}",
                headers=self.header,
            )
            assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_nonadmin_get_current_user(self, async_client):
        for user in ["editor_user", "auth_user"]:
            user_data = {
                "username": user,
                "password": "Password!23",
            }
            response = await async_client.post(
                "/api/token",
                data=user_data,
            )
            self.header["Authorization"] = f"Bearer {response.json()['access_token']}"
            response = await async_client.get(
                "/api/current/user",
                headers=self.header,
            )
            assert response.json()["username"] == user

    @pytest.mark.asyncio
    async def test_get_user_list(self, create_test_users, async_client):
        response = await async_client.get(
            "/api/users",
            headers=self.header,
        )
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_unknown_user_login(self, create_test_users, async_client):
        user_data = {
            "username": "unknown_user",
            "password": "Password!23",
        }
        response = await async_client.post(
            "/api/token",
            data=user_data,
        )
        assert response.json()["detail"] == "Incorrect username or password"

    @pytest.mark.asyncio
    async def test_invalid_password_login(self, create_test_users, async_client):
        user_data = {
            "username": "admin_user",
            "password": "password",
        }
        response = await async_client.post(
            "/api/token",
            data=user_data,
        )
        assert response.json()["detail"] == "Incorrect username or password"


@pytest.mark.asyncio
async def test_root_redirect(async_client):
    response = await async_client.get("/")
    assert response.status_code == 307

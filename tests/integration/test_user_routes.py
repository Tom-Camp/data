import pytest

from app.models.users import User


class TestUserRoutes:
    header: dict[str, str] = {"Content-Type": "application/json"}

    @pytest.mark.asyncio
    async def test_admin_login_token(self, create_test_users, async_client):
        user_data = {
            "username": "admin_user",
            "password": "password123",
        }
        response = await async_client.post(
            "/api/token",
            data=user_data,
        )
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "token_type" in response.json()
        self.header["Authorization"] = f"Bearer {response.json()['access_token']}"

    @pytest.mark.asyncio
    async def test_admin_create_user(self, create_test_users, async_client):
        user_data = {
            "username": "test_user_1",
            "password": "password123",
            "email": "test_user_1@example.com",
        }
        response = await async_client.post(
            "/api/users",
            headers=self.header,
            json=user_data,
        )
        assert response.status_code == 200
        assert response.json()["username"] == "test_user_1"

    @pytest.mark.asyncio
    async def test_admin_create_existing_user(self, create_test_users, async_client):
        user_data = {
            "username": "test_user_1",
            "password": "password123",
            "email": "test_user_1@example.com",
        }
        response = await async_client.post(
            "/api/users",
            headers=self.header,
            json=user_data,
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Username already registered"

    @pytest.mark.asyncio
    async def test_admin_create_existing_email(self, create_test_users, async_client):
        user_data = {
            "username": "test_user_2",
            "password": "password123",
            "email": "test_user_1@example.com",
        }
        response = await async_client.post(
            "/api/users",
            headers=self.header,
            json=user_data,
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Email already registered"

    @pytest.mark.asyncio
    async def test_admin_get_user(self, create_test_users, async_client):
        user = await User.find_one(User.username == "test_user_1")
        response = await async_client.get(
            f"/api/users/{user.id}",
            headers=self.header,
        )
        assert response.status_code == 200
        assert response.json()["username"] == "test_user_1"

    @pytest.mark.asyncio
    async def test_admin_incorrect_user_id(self, create_test_users, async_client):
        response = await async_client.get(
            "/api/users/123456",
            headers=self.header,
        )
        assert response.status_code == 422
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
    async def test_admin_delete_user(self, create_test_users, async_client):
        user = await User.find_one(User.username == "test_user_1_updated")
        response = await async_client.delete(
            f"/api/users/{user.id}",
            headers=self.header,
        )
        assert response.status_code == 200
        assert response.json()["message"] == "User deleted successfully"

    @pytest.mark.asyncio
    async def test_admin_get_current_user(self, async_client):
        response = await async_client.get(
            "/api/current/user",
            headers=self.header,
        )
        assert response.status_code == 200
        assert response.json()["username"] == "admin_user"

    @pytest.mark.asyncio
    async def test_editor_login_token(self, create_test_users, async_client):
        user_data = {
            "username": "editor_user",
            "password": "password123",
        }
        response = await async_client.post(
            "/api/token",
            data=user_data,
        )
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "token_type" in response.json()
        self.header["Authorization"] = f"Bearer {response.json()['access_token']}"

    @pytest.mark.asyncio
    async def test_editor_create_user(self, create_test_users, async_client):
        user_data = {
            "username": "test_user_3",
            "password": "password123",
            "email": "test_user_3@example.com",
        }
        response = await async_client.post(
            "/api/users",
            headers=self.header,
            json=user_data,
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_editor_get_user(self, create_test_users, async_client):
        user = await User.find_one(User.username == "auth_user")
        response = await async_client.get(
            f"/api/users/{user.id}",
            headers=self.header,
        )
        assert response.status_code == 200
        assert response.json()["username"] == "auth_user"

    @pytest.mark.asyncio
    async def test_editor_update_user(self, create_test_users, async_client):
        user = await User.find_one(User.username == "auth_user")
        user_data = {
            "username": "auth_user_updated",
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
    async def test_editor_delete_user(self, create_test_users, async_client):
        user = await User.find_one(User.username == "auth_user")
        response = await async_client.delete(
            f"/api/users/{user.id}",
            headers=self.header,
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_auth_login_token(self, create_test_users, async_client):
        user_data = {
            "username": "auth_user",
            "password": "password123",
        }
        response = await async_client.post(
            "/api/token",
            data=user_data,
        )
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "token_type" in response.json()
        self.header["Authorization"] = f"Bearer {response.json()['access_token']}"

    @pytest.mark.asyncio
    async def test_auth_create_user(self, create_test_users, async_client):
        user_data = {
            "username": "test_user_3",
            "password": "password123",
            "email": "test_user_3@example.com",
        }
        response = await async_client.post(
            "/api/users",
            headers=self.header,
            json=user_data,
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_auth_get_user(self, create_test_users, async_client):
        user = await User.find_one(User.username == "editor_user")
        response = await async_client.get(
            f"/api/users/{user.id}",
            headers=self.header,
        )
        assert response.status_code == 200
        assert response.json()["username"] == "editor_user"

    @pytest.mark.asyncio
    async def test_auth_update_user(self, create_test_users, async_client):
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
    async def test_auth_delete_user(self, create_test_users, async_client):
        user = await User.find_one(User.username == "editor_user")
        response = await async_client.delete(
            f"/api/users/{user.id}",
            headers=self.header,
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_auth_get_current_user(self, async_client):
        response = await async_client.get(
            "/api/current/user",
            headers=self.header,
        )
        assert response.status_code == 200
        assert response.json()["username"] == "auth_user"

    @pytest.mark.asyncio
    async def test_get_user_list(self, create_test_users, async_client):
        response = await async_client.get(
            "/api/users",
            headers=self.header,
        )
        assert response.status_code == 200
        assert len(response.json()) == 3
        assert response.json()[0]["username"] == "admin_user"
        assert response.json()[1]["username"] == "editor_user"
        assert response.json()[2]["username"] == "auth_user"

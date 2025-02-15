import pytest
from beanie import PydanticObjectId

from app.models.users import User


class TestPages:
    header: dict[str, str] = {"Content-Type": "application/json"}

    @pytest.mark.asyncio
    async def test_page_create(self, async_client, create_test_users):
        user_data = {
            "username": "admin_user",
            "password": "Password!23",
        }
        response = await async_client.post(
            "/api/token",
            data=user_data,
        )
        self.header = {"Authorization": f"Bearer {response.json()['access_token']}"}
        response = await async_client.post(
            "/api/pages",
            json={"title": "Posted Test Page", "body": "This is a posted test page"},
            headers=self.header,
        )
        user = await User.find_one(User.username == "admin_user")
        assert response.status_code == 200
        assert response.json()["title"] == "Posted Test Page"
        assert response.json()["body"] == "This is a posted test page"
        assert response.json()["author"]["id"] == str(user.id)
        assert response.json()["created_date"]
        assert response.json()["updated_date"]
        assert response.json()["_id"]

    @pytest.mark.asyncio
    async def test_page_list(self, async_client):
        response = await async_client.get("/api/pages")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_page_get(self, async_client):
        response = await async_client.get("/api/pages")
        page_id = response.json()[0]["_id"]

        response = await async_client.get(f"/api/pages/{page_id}")
        assert response.status_code == 200
        assert response.json()["_id"] == page_id
        assert response.json()["title"]
        assert response.json()["body"]
        assert response.json()["author"]
        assert response.json()["created_date"]
        assert response.json()["updated_date"]

        pid = PydanticObjectId()
        response = await async_client.get(f"/api/pages/{pid}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Page not found"

    @pytest.mark.asyncio
    async def test_page_update(self, async_client, create_test_users):
        user_data = {
            "username": "admin_user",
            "password": "Password!23",
        }
        response = await async_client.post(
            "/api/token",
            data=user_data,
        )
        self.header = {"Authorization": f"Bearer {response.json()['access_token']}"}
        response = await async_client.get("/api/pages")
        page_id = response.json()[0]["_id"]

        response = await async_client.put(
            f"/api/pages/{page_id}",
            json={"title": "Updated Test Page", "body": "This is an updated test page"},
            headers=self.header,
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Test Page"
        assert response.json()["body"] == "This is an updated test page"
        assert response.json()["updated_date"] > response.json()["created_date"]

import pytest

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

import pytest
from beanie import PydanticObjectId

from app.models.pages import Page


class TestPages:
    header: dict[str, str] = {"Content-Type": "application/json"}

    @pytest.mark.asyncio
    async def test_page_create(self, async_client, create_test_users):
        for user in ["admin_user", "editor_user"]:
            user_data = {
                "username": user,
                "password": "Password!23",
            }
            response = await async_client.post(
                "/api/token",
                data=user_data,
            )
            self.header = {"Authorization": f"Bearer {response.json()['access_token']}"}
            response = await async_client.post(
                "/api/pages",
                json={
                    "title": f"{user} Posted Test Page",
                    "body": "This is a posted test page",
                },
                headers=self.header,
            )
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_page_create_existing(self, async_client):
        user_data = {
            "username": "editor_user",
            "password": "Password!23",
        }
        response = await async_client.post(
            "/api/token",
            data=user_data,
        )
        self.header = {"Authorization": f"Bearer {response.json()['access_token']}"}
        response = await async_client.post(
            "/api/pages",
            json={
                "title": "editor_user Posted Test Page",
                "body": "This is an unauthorized test page",
            },
            headers=self.header,
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_page_create_auth_role(self, async_client):
        user_data = {
            "username": "author_user",
            "password": "Password!23",
        }
        response = await async_client.post(
            "/api/token",
            data=user_data,
        )
        response = await async_client.post(
            "/api/pages",
            json={
                "title": "Unauthorized Test Page",
                "body": "This is an unauthorized test page",
            },
            headers=self.header,
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_page_create_unauthenticated(self, async_client):
        response = await async_client.post(
            "/api/pages",
            json={
                "title": "Unauthorized Test Page",
                "body": "This is an unauthorized test page",
            },
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

    @pytest.mark.asyncio
    async def test_page_list(self, async_client):
        response = await async_client.get("/api/pages")
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_page_get(self, async_client):
        response = await async_client.get("/api/pages")
        page_id = response.json()[0]["_id"]

        response = await async_client.get(f"/api/pages/{page_id}")
        assert response.json()["_id"] == page_id

    @pytest.mark.asyncio
    async def test_page_not_found(self, async_client):
        pid = PydanticObjectId()
        response = await async_client.get(f"/api/pages/{pid}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_page_update(self, async_client, create_test_users):
        for user in ["admin_user", "editor_user"]:
            user_data = {
                "username": user,
                "password": "Password!23",
            }
            response = await async_client.post(
                "/api/token",
                data=user_data,
            )
            self.header = {"Authorization": f"Bearer {response.json()['access_token']}"}
            page = await Page.find_one(Page.title == f"{user} Posted Test Page")

            response = await async_client.put(
                f"/api/pages/{page.id}",
                json={
                    "title": f"Updated {user} Test Page",
                    "body": "This is an updated test page",
                },
                headers=self.header,
            )
            assert response.json()["title"] == f"Updated {user} Test Page"

    @pytest.mark.asyncio
    async def test_page_update_unauthorized(self, async_client):
        user_data = {
            "username": "auth_user",
            "password": "Password!23",
        }
        response = await async_client.post(
            "/api/token",
            data=user_data,
        )
        self.header = {"Authorization": f"Bearer {response.json()['access_token']}"}

        page = await Page.find_one(Page.title == "Updated editor_user Test Page")
        response = await async_client.put(
            f"/api/pages/{page.id}",
            json={
                "title": "Unauthorized Test Page",
                "body": "This is an unauthorized test page",
            },
            headers=self.header,
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_page_update_not_found(self, async_client):
        user_data = {
            "username": "editor_user",
            "password": "Password!23",
        }
        response = await async_client.post(
            "/api/token",
            data=user_data,
        )
        self.header = {"Authorization": f"Bearer {response.json()['access_token']}"}
        pid = PydanticObjectId()
        response = await async_client.put(
            f"/api/pages/{pid}",
            json={
                "title": "Not Found Test Page",
                "body": "This is a not found test page",
            },
            headers=self.header,
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_page_author_mismatch(self, async_client):
        user_data = {
            "username": "editor_user",
            "password": "Password!23",
        }
        response = await async_client.post(
            "/api/token",
            data=user_data,
        )
        self.header = {"Authorization": f"Bearer {response.json()['access_token']}"}

        page = await Page.find_one(Page.title == "Updated admin_user Test Page")
        response = await async_client.put(
            f"/api/pages/{page.id}",
            json={
                "title": "Unauthorized Test Page",
                "body": "This is an unauthorized test page",
            },
            headers=self.header,
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_page_admin_can_edit(self, async_client):
        user_data = {
            "username": "admin_user",
            "password": "Password!23",
        }
        response = await async_client.post(
            "/api/token",
            data=user_data,
        )
        self.header = {"Authorization": f"Bearer {response.json()['access_token']}"}

        page = await Page.find_one(Page.title == "Updated editor_user Test Page")
        response = await async_client.put(
            f"/api/pages/{page.id}",
            json={"title": "Admin Edited Test Page", "body": "This is a test page"},
            headers=self.header,
        )
        assert response.json()["title"] == "Admin Edited Test Page"

    @pytest.mark.asyncio
    async def test_page_admin_delete(self, async_client):
        user_data = {
            "username": "admin_user",
            "password": "Password!23",
        }
        response = await async_client.post(
            "/api/token",
            data=user_data,
        )
        self.header = {"Authorization": f"Bearer {response.json()['access_token']}"}

        page = await Page.find_one(Page.title == "Updated admin_user Test Page")
        response = await async_client.delete(
            f"/api/pages/{page.id}",
            headers=self.header,
        )
        assert response.json() == {"detail": "Page deleted"}

    @pytest.mark.asyncio
    async def test_page_admin_delete_not_found(self, async_client):
        user_data = {
            "username": "admin_user",
            "password": "Password!23",
        }
        response = await async_client.post(
            "/api/token",
            data=user_data,
        )
        self.header = {"Authorization": f"Bearer {response.json()['access_token']}"}

        pid = PydanticObjectId()
        response = await async_client.delete(
            f"/api/pages/{pid}",
            headers=self.header,
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_page_delete_unauthorized(self, async_client, create_test_users):
        for user in ["auth_user", "editor_user"]:
            user_data = {
                "username": "editor_user",
                "password": "Password!23",
            }
            response = await async_client.post(
                "/api/token",
                data=user_data,
            )
            self.header = {"Authorization": f"Bearer {response.json()['access_token']}"}

            page = await Page.find_one(Page.title == "Admin Edited Test Page")
            response = await async_client.delete(
                f"/api/pages/{page.id}",
                headers=self.header,
            )
            assert response.status_code == 403

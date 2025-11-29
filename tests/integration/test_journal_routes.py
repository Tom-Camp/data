from typing import List

import pytest
from beanie import PydanticObjectId

from app.models.journals import Journal
from app.models.users import User


class TestJournalRoutes:
    header: dict[str, str] = {"Content-Type": "application/json"}

    @pytest.mark.asyncio
    async def test_editor_create_journal(
        self, create_test_users, async_client, journal_data
    ):
        user_data = {
            "username": "editor_user",
            "password": "Password!23",
        }
        response = await async_client.post(
            "/api/token",
            data=user_data,
        )
        self.header["Authorization"] = f"Bearer {response.json()['access_token']}"

        response = await async_client.post(
            "/api/journals",
            json=journal_data,
            headers=self.header,
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_editor_get_journal(self, create_test_users, async_client):
        journal = await Journal.find_one(
            Journal.title == "Test Journal", fetch_links=True
        )
        response = await async_client.get(f"/api/journals/{journal.id}")
        assert response.json()["description"] == "This is a test journal"

    @pytest.mark.asyncio
    async def test_get_nonexistant_journal(self, async_client):
        pid = PydanticObjectId()
        response = await async_client.get(f"/api/journals/{str(pid)}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_editor_update_journal(self, async_client):
        journal = await Journal.find_one(Journal.title == "Test Journal")
        updated_journal = journal.model_dump(
            mode="json", exclude={"id", "author", "created_at", "updated_at"}
        )
        updated_journal["entries"].append(
            {
                "title": "Entry 3",
                "date": "2021-09-01",
                "body": "This is the  entry in the test journal",
                "location": "POINT (-81.0295357 34.927908)",
                "images": [
                    "/path/to/image.jpg",
                ],
            }
        )
        updated_journal["title"] = "Updated Journal"
        updated_journal["description"] = "This is an updated journal"
        response = await async_client.put(
            f"/api/journals/{str(journal.id)}",
            json=updated_journal,
            headers=self.header,
        )
        assert response.json()["description"] == "This is an updated journal"

    @pytest.mark.asyncio
    async def test_editor_cant_delete_journal(self, create_test_users, async_client):
        journal = await Journal.find_one(Journal.title == "Updated Journal")
        response = await async_client.delete(f"/api/journals/{str(journal.id)}")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_admin_delete_journal(self, create_test_users, async_client):
        user_data = {
            "username": "admin_user",
            "password": "Password!23",
        }
        response = await async_client.post(
            "/api/token",
            data=user_data,
        )
        self.header["Authorization"] = f"Bearer {response.json()['access_token']}"

        journal = await Journal.find_one(Journal.title == "Updated Journal")
        response = await async_client.delete(
            f"/api/journals/{str(journal.id)}",
            headers=self.header,
        )
        assert response.json() == {"message": "Journal deleted successfully"}

    @pytest.mark.asyncio
    async def test_admin_delete_nonexistant_journal(self, async_client):
        user_data = {
            "username": "admin_user",
            "password": "Password!23",
        }
        response = await async_client.post(
            "/api/token",
            data=user_data,
        )
        self.header["Authorization"] = f"Bearer {response.json()['access_token']}"
        pid = PydanticObjectId()
        response = await async_client.delete(
            f"/api/journals/{str(pid)}",
            headers=self.header,
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_admin_create_journal(
        self, create_test_users, async_client, journal_data
    ):
        user = await User.find_one(User.username == "admin_user")
        journal_data["author"] = str(user.id)
        response = await async_client.post(
            "/api/journals",
            json=journal_data,
            headers=self.header,
        )
        assert response.json()["title"] == "Test Journal"

    @pytest.mark.asyncio
    async def test_admin_create_existing_journal(
        self, create_test_users, async_client, journal_data
    ):
        user = await User.find_one(User.username == "admin_user")
        journal_data["author"] = str(user.id)
        response = await async_client.post(
            "/api/journals",
            json=journal_data,
            headers=self.header,
        )
        assert response.json()["detail"] == "Journal already registered"

    @pytest.mark.asyncio
    async def test_admin_get_journal(self, create_test_users, async_client):
        journal = await Journal.find_one(
            Journal.title == "Test Journal", fetch_links=True
        )
        response = await async_client.get(f"/api/journals/{journal.id}")
        assert response.json()["description"] == "This is a test journal"

    @pytest.mark.asyncio
    async def test_admin_update_journal(self, async_client):
        journal = await Journal.find_one(Journal.title == "Test Journal")
        updated_journal = journal.model_dump(
            mode="json", exclude={"id", "author", "created_at", "updated_at"}
        )
        updated_journal["entries"].append(
            {
                "title": "Entry 3",
                "date": "2021-09-01",
                "body": "This is the  entry in the test journal",
                "location": "POINT (-81.0295357 34.927908)",
                "images": [
                    "/path/to/image.jpg",
                ],
            }
        )
        updated_journal["title"] = "Updated Journal"
        updated_journal["description"] = "This is an updated journal"
        response = await async_client.put(
            f"/api/journals/{str(journal.id)}",
            json=updated_journal,
            headers=self.header,
        )
        assert response.json()["title"] == "Updated Journal"

    @pytest.mark.asyncio
    async def test_admin_update_nonexistant_journal(self, async_client):
        journal = await Journal.find_one(Journal.title == "Updated Journal")
        updated_journal = journal.model_dump(
            mode="json", exclude={"id", "author", "created_at", "updated_at"}
        )
        updated_journal["title"] = "Updated Journal"
        pid = PydanticObjectId()
        response = await async_client.put(
            f"/api/journals/{str(pid)}",
            json=updated_journal,
            headers=self.header,
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_auth_create_journal(
        self, create_test_users, async_client, journal_data
    ):
        user_data = {
            "username": "auth_user",
            "password": "Password!23",
        }
        response = await async_client.post(
            "/api/token",
            data=user_data,
        )
        self.header["Authorization"] = f"Bearer {response.json()['access_token']}"

        user = await User.find_one(User.username == "auth_user")
        journal_data["author"] = str(user.id)
        response = await async_client.post(
            "/api/journals",
            json=journal_data,
            headers=self.header,
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_auth_get_journal(self, create_test_users, async_client):
        journal = await Journal.find_one(
            Journal.title == "Updated Journal", fetch_links=True
        )
        response = await async_client.get(f"/api/journals/{journal.id}")
        assert response.json()["description"] == "This is an updated journal"

    @pytest.mark.asyncio
    async def test_auth_update_journal(self, async_client):
        journal = await Journal.find_one(Journal.title == "Updated Journal")
        updated_journal = journal.model_dump(
            mode="json", exclude={"id", "author", "created_at", "updated_at"}
        )
        updated_journal["entries"].append(
            {
                "title": "Entry 3",
                "date": "2021-09-01",
                "body": "This is the  entry in the test journal",
                "location": "POINT (-81.0295357 34.927908)",
                "images": [
                    "/path/to/image.jpg",
                ],
            }
        )
        updated_journal["title"] = "Updated Journal"
        updated_journal["description"] = "This is an updated journal"
        response = await async_client.put(
            f"/api/journals/{str(journal.id)}",
            json=updated_journal,
            headers=self.header,
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_auth_cant_delete_journal(self, create_test_users, async_client):
        journal = await Journal.find_one(Journal.title == "Updated Journal")
        response = await async_client.delete(f"/api/journals/{str(journal.id)}")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_journals(self, async_client):
        response = await async_client.get("/api/journals")
        assert isinstance(response.json(), List)

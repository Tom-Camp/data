from typing import List

import pytest
from beanie import PydanticObjectId

from app.models.devices import Device


class TestDevices:
    header: dict[str, str] = {"Content-Type": "application/json"}

    @pytest.mark.asyncio
    async def test_device_create(self, async_client, create_test_users):
        user_data = {
            "username": "admin_user",
            "password": "Password!23",
        }
        response = await async_client.post(
            "/api/token",
            data=user_data,
        )
        self.header["Authorization"] = f"Bearer {response.json()['access_token']}"

        response = await async_client.post(
            "/api/devices",
            json={
                "device_id": "posted_device",
                "notes": {
                    "step1": "Do something",
                    "step2": "Do something else",
                },
            },
            headers=self.header,
        )
        assert response.status_code == 200
        assert response.json()["device_id"] == "posted_device"
        assert response.json()["api_key"]
        assert response.json()["notes"] == {
            "step1": "Do something",
            "step2": "Do something else",
        }
        assert isinstance(response.json()["data"], List)

    @pytest.mark.asyncio
    async def test_device_get_api_key(self, async_client):
        device = await Device.find_one({"device_id": "posted_device"})
        response = await async_client.get(
            f"/api/devices/{str(device.id)}/key",
            headers=self.header,
        )
        assert response.status_code == 200
        assert response.json() == device.api_key
        self.header.pop("Authorization")
        self.header["X-API-KEY"] = response.json()

    @pytest.mark.asyncio
    async def test_device_data_post(self, async_client):
        device = await Device.find_one({"device_id": "posted_device"})
        response = await async_client.post(
            "/api/devices/data",
            json={
                "device_id": device.device_id,
                "notes": device.notes,
                "data": {"key": "value"},
            },
            headers=self.header,
        )
        assert response.status_code == 200
        assert response.json() == {"message": "Data received"}

    @pytest.mark.asyncio
    async def test_device_incorrect_data_post(self, async_client):
        response = await async_client.post(
            "/api/devices/data",
            json={"device_id": "new_device", "data": {"key": "value"}},
            headers=self.header,
        )
        assert response.status_code == 401
        assert response.json() == {"detail": "Mismatched device ID"}

    @pytest.mark.asyncio
    async def test_device_get(self, async_client):
        user_data = {
            "username": "admin_user",
            "password": "Password!23",
        }
        response = await async_client.post(
            "/api/token",
            data=user_data,
        )
        api_key = self.header["X-API-KEY"]
        self.header.pop("X-API-KEY")
        self.header["Authorization"] = f"Bearer {response.json()['access_token']}"
        device = await Device.find_one({"device_id": "posted_device"})
        response = await async_client.get(
            f"/api/devices/{str(device.id)}",
            headers=self.header,
        )
        assert response.status_code == 200
        assert response.json()["device_id"] == "posted_device"
        assert response.json()["api_key"] == api_key
        assert isinstance(response.json()["data"], List)
        assert response.json()["created_date"] is not None
        assert response.json()["updated_date"] is not None
        assert response.json()["data"][0]["data"] == {"key": "value"}
        assert response.json()["data"][0]["created_date"] is not None

    @pytest.mark.asyncio
    async def test_device_update(self, async_client, create_test_users):
        user_data = {
            "username": "admin_user",
            "password": "Password!23",
        }
        response = await async_client.post(
            "/api/token",
            data=user_data,
        )
        self.header = {"Authorization": f"Bearer {response.json()['access_token']}"}
        device = await Device.find_one({"device_id": "posted_device"})

        response = await async_client.put(
            f"/api/devices/{device.id}",
            json={
                "device_id": "Updated posted_device",
                "notes": {
                    "step1": "Do other things",
                },
            },
            headers=self.header,
        )
        assert response.status_code == 200
        assert response.json()["device_id"] == "Updated posted_device"
        assert response.json()["notes"].get("step1", None) == "Do other things"

    @pytest.mark.asyncio
    async def test_device_update_unauthorized(self, async_client):
        user_data = {
            "username": "auth_user",
            "password": "Password!23",
        }
        response = await async_client.post(
            "/api/token",
            data=user_data,
        )
        self.header = {"Authorization": f"Bearer {response.json()['access_token']}"}

        device = await Device.find_one({"device_id": "Updated posted_device"})
        response = await async_client.put(
            f"/api/devices/{device.id}",
            json={
                "device_id": "Unauthorized Test Page",
                "notes": {"note": "This is an unauthorized test page"},
            },
            headers=self.header,
        )
        assert response.status_code == 403
        assert response.json()["detail"] == "Permission denied"

    @pytest.mark.asyncio
    async def test_device_update_not_found(self, async_client):
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
        response = await async_client.put(
            f"/api/devices/{pid}",
            json={
                "device_id": "Not Found Test Device",
                "notes": {"notes": "This is a not found test page"},
            },
            headers=self.header,
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Device not found"

    @pytest.mark.asyncio
    async def test_get_unknown_device(self, async_client):
        response = await async_client.get(
            "/api/devices/123456789012345678901234",
            headers=self.header,
        )
        assert response.status_code == 404
        assert response.json() == {"detail": "Device not found"}

    @pytest.mark.asyncio
    async def test_device_list(self, async_client):
        response = await async_client.get("/api/devices")
        assert response.status_code == 200
        assert isinstance(response.json(), List)
        assert len(response.json()) == 1
        assert response.json()[0]["device_id"] == "Updated posted_device"
        assert response.json()[0]["data"][0]["data"] == {"key": "value"}
        assert response.json()[0]["created_date"] is not None
        assert response.json()[0]["updated_date"] is not None
        assert not hasattr(response.json()[0], "api_key")

    @pytest.mark.asyncio
    async def test_device_create_unauthorized(self, async_client, create_test_users):
        count: int = 1
        test_users: List[str] = ["editor_user", "auth_user"]
        for user in test_users:
            user_data = {
                "username": user,
                "password": "Password!23",
            }
            response = await async_client.post(
                "/api/token",
                data=user_data,
            )
            self.header["Authorization"] = f"Bearer {response.json()['access_token']}"
            response = await async_client.post(
                "/api/devices",
                json={"device_id": f"posted_device_{count}"},
            )
            assert response.status_code == 401
            count += 1

    @pytest.mark.asyncio
    async def test_device_delete_unauthorized(self, async_client, create_test_users):
        test_users: List[str] = ["editor_user", "auth_user"]
        device = await Device.find_one({"device_id": "Updated posted_device"})
        for user in test_users:
            user_data = {
                "username": user,
                "password": "Password!23",
            }
            response = await async_client.post(
                "/api/token",
                data=user_data,
            )
            self.header["Authorization"] = f"Bearer {response.json()['access_token']}"
            response = await async_client.delete(
                f"/api/devices/{str(device.id)}",
                headers=self.header,
            )
            assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_device_delete(self, async_client, create_test_users):
        user_data = {
            "username": "admin_user",
            "password": "Password!23",
        }
        response = await async_client.post(
            "/api/token",
            data=user_data,
        )
        self.header["Authorization"] = f"Bearer {response.json()['access_token']}"
        device = await Device.find_one({"device_id": "Updated posted_device"})
        response = await async_client.delete(
            f"/api/devices/{str(device.id)}",
            headers=self.header,
        )
        assert response.status_code == 200
        response = await async_client.get("/api/devices")
        assert response.status_code == 200
        assert len(response.json()) == 0

    @pytest.mark.asyncio
    async def test_unknown_device_delete(self, async_client, create_test_users):
        user_data = {
            "username": "admin_user",
            "password": "Password!23",
        }
        response = await async_client.post(
            "/api/token",
            data=user_data,
        )
        self.header["Authorization"] = f"Bearer {response.json()['access_token']}"
        did = PydanticObjectId()
        response = await async_client.delete(
            f"/api/devices/{str(did)}",
            headers=self.header,
        )
        assert response.status_code == 404
        assert response.json() == {"detail": "Device not found"}

    @pytest.mark.asyncio
    async def test_invalid_api_key(self, async_client):
        response = await async_client.post(
            "/api/devices/data",
            json={"device_id": "posted_device", "data": {"key": "value"}},
            headers={
                "Content-Type": "application/json",
                "X-API-KEY": "invalid_api_key",
            },
        )
        assert response.status_code == 401

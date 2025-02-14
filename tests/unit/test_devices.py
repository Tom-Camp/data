from datetime import datetime

import pytest

from app.models.devices import Device, DeviceData


class TestDeviceModel:
    @pytest.mark.asyncio
    async def test_device_creation(self, beanie_init):
        device = Device(
            device_id="test_device",
            data=[
                DeviceData(
                    data={
                        "test": "data",
                        "list": [1, 2, 3],
                    }
                ),
                DeviceData(
                    data={
                        "more": "data",
                        "some": {"nested": "data"},
                    }
                ),
            ],
        )
        await device.insert()
        assert isinstance(device.api_key, str)
        assert len(device.data) == 2
        assert device.data[0].data == {"test": "data", "list": [1, 2, 3]}
        assert isinstance(device.data[0].created_date, datetime)

    @pytest.mark.asyncio
    async def test_device_retrieval(self, beanie_init):
        device = await Device.find_one(
            Device.device_id == "test_device", fetch_links=True
        )
        assert device is not None

    @pytest.mark.asyncio
    async def test_device_update(self, beanie_init):
        device = await Device.find_one(
            Device.device_id == "test_device", fetch_links=True
        )
        data = DeviceData(
            data={
                "added": "data",
                "another": {"nested": "data"},
            }
        )
        device.data.append(data)
        await device.save()

        updated_device = await Device.get(device.id)
        assert len(updated_device.data) == 3

    @pytest.mark.asyncio
    async def test_device_delete(self, beanie_init):
        device = await Device.find_one(Device.device_id == "test_device")
        await device.delete()

        deleted_device = await Device.find_one(Device.device_id == "test_device")
        assert deleted_device is None

    @pytest.mark.asyncio
    async def test_device_data_creation(self, beanie_init):
        device_data = DeviceData(
            data={
                "test": "data",
                "list": [1, 2, 3],
            }
        )
        assert device_data.data == {"test": "data", "list": [1, 2, 3]}
        assert isinstance(device_data.created_date, datetime)

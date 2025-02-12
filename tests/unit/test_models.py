import pytest

from app.models.devices import Device, DeviceCreate, DeviceData
from app.models.journals import Entry, Journal
from app.models.users import User


class TestUserModel:
    @pytest.mark.asyncio
    async def test_user_creation(self, beanie_init):
        user = User(
            username="test_user",
            email="test@example.com",
            password="p4ssword!23",
        )

        await user.insert()
        assert user.username == "test_user"
        assert user.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_user_retrieval(self, beanie_init, create_test_users):
        user = await User.find_one(User.username == "admin_user")
        user_dict = user.model_dump(exclude={"password"})

        assert user is not None
        assert user.username == "admin_user"
        assert user.role.value == 3
        assert not hasattr(user_dict, "password")

    @pytest.mark.asyncio
    async def test_user_update(self, beanie_init, create_test_users):
        user = await User.find_one(User.username == "auth_user")
        new_email = "authenticated@example.com"
        user.email = new_email
        await user.save()

        updated_user = await User.get(user.id)
        assert updated_user.email == new_email

    @pytest.mark.asyncio
    async def test_user_delete(self, beanie_init):
        user = await User.find_one(User.username == "test_user")
        await user.delete()

        deleted_user = await User.find_one(User.username == "test_user")
        assert deleted_user is None


class TestJournalModel:
    @pytest.mark.asyncio
    async def test_journal_creation(self, beanie_init, journal_data):
        author = await User.find_one(User.username == "editor_user")
        journal_data = journal_data
        journal_data["author"] = author
        journal = Journal(**journal_data)
        await journal.insert()
        assert journal.title == "Test Journal"
        assert len(journal.entries) == 2

    @pytest.mark.asyncio
    async def test_journal_retrieval(self, beanie_init):
        journal = await Journal.find_one(
            Journal.title == "Test Journal", fetch_links=True
        )
        author = await journal.author.fetch()
        assert journal is not None
        assert author.username == "editor_user"

    @pytest.mark.asyncio
    async def test_journal_update(self, beanie_init):
        journal = await Journal.find_one(
            Journal.title == "Test Journal", fetch_links=True
        )
        title = "Updated Test Journal"
        journal.title = title
        new_entry = Entry(
            title="A Third Entry",
            date="2022-01-02 12:00:00",
            location="POINT (-81.0295357 34.927908)",
            body="This is a third test entry.",
            images=["/path/to/image.jpg"],
        )
        journal.entries.append(new_entry)
        await journal.save()

        updated_journal = await Journal.get(journal.id)
        assert updated_journal.title == "Updated Test Journal"
        assert len(updated_journal.entries) == 3

    @pytest.mark.asyncio
    async def test_journal_delete(self, beanie_init):
        journal = await Journal.find_one(Journal.title == "Updated Test Journal")
        await journal.delete()

        deleted_journal = await Journal.find_one(
            Journal.title == "Updated Test Journal"
        )
        assert deleted_journal is None


class TestDeviceModel:
    @pytest.mark.asyncio
    async def test_device_creation(self, beanie_init):
        device = DeviceCreate(
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

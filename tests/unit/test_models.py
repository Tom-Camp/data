import pytest
from beanie import PydanticObjectId

from app.models.devices import Device, DeviceCreate, DeviceData
from app.models.journals import Entry, Journal
from app.models.users import User, UserCreate


class TestUserModel:
    @pytest.mark.asyncio
    async def test_user_creation(beanie_init):
        user = UserCreate(
            username="test_user",
            email="test@example.com",
            password="p4ssword!23",
        )

        await user.insert()
        assert user.username == "test_user"
        assert user.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_user_retrieval(beanie_init, create_test_users):
        user = await User.find_one(User.username == "admin_user")

        assert user is not None
        assert user.username == "admin_user"
        assert user.role.value == 3
        assert not hasattr(user, "password")

    @pytest.mark.asyncio
    async def test_user_update(beanie_init, create_test_users):
        user = await User.find_one(User.username == "auth_user")
        new_email = "authenticated@example.com"
        user.email = new_email
        await user.save()

        updated_user = await User.get(user.id)
        assert updated_user.email == new_email

    @pytest.mark.asyncio
    async def test_user_delete(beanie_init):
        user = await User.find_one(User.username == "test_user")
        await user.delete()

        deleted_user = await User.find_one(User.username == "test_user")
        assert deleted_user is None


class TestJournalModel:
    @pytest.mark.asyncio
    async def test_journal_creation(beanie_init):
        author = await User.find_one(User.username == "editor_user")
        journal = Journal(
            title="Test Journal",
            author=PydanticObjectId(author.id),
            description="This is a test journal.",
            entries=[
                Entry(
                    title="Test Entry",
                    date="2022-01-01 12:00:00",
                    location="POINT (-81.0295357 34.927908)",
                    body="This is a test entry.",
                    images=["/path/to/image.jpg"],
                ),
                Entry(
                    title="Another Entry",
                    date="2022-01-02 12:00:00",
                    location="POINT (-81.0295357 34.927908)",
                    body="This is another test entry.",
                    images=["/path/to/image.jpg"],
                ),
            ],
        )
        await journal.insert()
        assert journal.title == "Test Journal"
        assert len(journal.entries) == 2

    @pytest.mark.asyncio
    async def test_journal_retrieval(beanie_init):
        journal = await Journal.find_one(
            Journal.title == "Test Journal", fetch_links=True
        )
        author = await journal.author.fetch()
        assert journal is not None
        assert author.username == "editor_user"

    @pytest.mark.asyncio
    async def test_journal_update(beanie_init):
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
    async def test_journal_delete(beanie_init):
        journal = await Journal.find_one(Journal.title == "Updated Test Journal")
        await journal.delete()

        deleted_journal = await Journal.find_one(
            Journal.title == "Updated Test Journal"
        )
        assert deleted_journal is None


class TestDeviceModel:
    @pytest.mark.asyncio
    async def test_device_creation(beanie_init):
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
    async def test_journal_retrieval(beanie_init):
        device = await Device.find_one(
            Device.device_id == "test_device", fetch_links=True
        )
        assert device is not None

    @pytest.mark.asyncio
    async def test_journal_update(beanie_init):
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
    async def test_device_delete(beanie_init):
        device = await Device.find_one(Device.device_id == "test_device")
        await device.delete()

        deleted_device = await Journal.find_one(Device.device_id == "test_device")
        assert deleted_device is None

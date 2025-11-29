from datetime import datetime

import pytest

from app.models.journals import Entry, Journal
from app.models.users import User


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

    @pytest.mark.asyncio
    async def test_journal_entry_creation(self, beanie_init):
        entry = Entry(
            title="A New Entry",
            date="2022-01-01 12:00:00",
            location="POINT (-81.0295357 34.927908)",
            body="This is a test entry.",
            images=["/path/to/image.jpg"],
        )
        assert entry.title == "A New Entry"
        assert entry.date == datetime(2022, 1, 1, 12)
        assert entry.location == "POINT (-81.0295357 34.927908)"
        assert entry.body == "This is a test entry."
        assert entry.images == ["/path/to/image.jpg"]

    @pytest.mark.asyncio
    async def test_journal_entry_date_validation(self, beanie_init):
        entry = Entry(
            title="A New Entry",
            date="",
            location="POINT (-81.0295357 34.927908)",
            body="This is a test entry.",
            images=["/path/to/image.jpg"],
        )
        assert isinstance(entry.date, datetime)

        entry = Entry(
            title="A New Entry",
            date="not-a-date",
            location="POINT (-81.0295357 34.927908)",
            body="This is a test entry.",
            images=["/path/to/image.jpg"],
        )
        assert isinstance(entry.date, datetime)

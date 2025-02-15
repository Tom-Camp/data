from datetime import datetime, timezone

import pytest

from app.models.pages import Page
from app.models.users import User


class TestPages:
    @pytest.mark.asyncio
    async def test_page_creation(self, beanie_init, create_test_users):
        user = await User.find_one(User.username == "admin_user")
        page = Page(
            author=user,
            title="Test Page",
            body="This is a test page",
        )

        await page.insert()
        assert page.author.username == "admin_user"
        assert page.body == "This is a test page"

    @pytest.mark.asyncio
    async def test_page_retrieval(self, beanie_init):
        page = await Page.find_one(Page.title == "Test Page", fetch_links=True)
        await page.fetch_all_links()
        assert page is not None
        assert page.author.username == "admin_user"
        assert page.body == "This is a test page"
        assert isinstance(page.created_date, datetime)
        assert isinstance(page.updated_date, datetime)

    @pytest.mark.asyncio
    async def test_page_update(self, beanie_init):
        new_body = "This is an authenticated page"
        page = await Page.find_one(Page.title == "Test Page")
        await page.update(
            {
                "$set": {
                    Page.body: new_body,
                    Page.updated_date: datetime.now(timezone.utc),
                }
            }
        )

        updated_page = await Page.get(page.id)
        assert updated_page.body == new_body
        assert updated_page.updated_date > updated_page.created_date

    @pytest.mark.asyncio
    async def test_page_delete(self, beanie_init):
        page = await Page.find_one(Page.title == "Test Page")
        await page.delete()

        deleted_page = await Page.find_one(Page.title == "Test Page")
        assert deleted_page is None

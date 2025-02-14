import pytest

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

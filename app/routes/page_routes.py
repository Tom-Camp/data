from fastapi import APIRouter, Depends, HTTPException

from app.auth import require_role
from app.models.pages import Page, PageCreate
from app.models.users import Role, User

router = APIRouter()


@router.post("/pages", response_model=Page)
async def create_page(
    page: PageCreate, user: User = Depends(require_role(Role.EDITOR))
):
    existing_page: Page = await Page.find_one(Page.title == page.title)
    if existing_page:
        raise HTTPException(status_code=400, detail="Page already registered")
    new_page: Page = Page(
        **page.model_dump(),
        author=user,
    )
    await new_page.insert()
    return new_page

from datetime import datetime, timezone

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


@router.get("/pages", response_model=list[Page])
async def list_pages():
    pages = await Page.find_all().to_list()
    return pages


@router.get("/pages/{page_id}", response_model=Page)
async def get_page(page_id: str):
    page = await Page.get(page_id)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return page


@router.put("/pages/{page_id}", response_model=Page)
async def update_page(
    page_id: str, page: PageCreate, user: User = Depends(require_role(Role.EDITOR))
):
    existing_page: Page = await Page.get(page_id)
    if not existing_page:
        raise HTTPException(status_code=404, detail="Page not found")
    await existing_page.fetch_link("author")
    if existing_page.author.id != user.id and user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Permission denied")

    update_data = {
        key: value
        for key, value in page.model_dump(exclude_unset=True).items()
        if value is not None
    }
    update_data["updated_date"] = datetime.now(timezone.utc)
    await existing_page.update({"$set": update_data})
    return await Page.get(page_id)


@router.delete("/pages/{page_id}")
async def delete_page(page_id: str, user: User = Depends(require_role(Role.ADMIN))):
    page = await Page.get(page_id)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    await page.delete()
    return {"detail": "Page deleted"}

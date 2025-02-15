from datetime import datetime, timezone

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException

from app.auth import require_role
from app.models.journals import Entry, Journal, JournalCreate, JournalUpdate
from app.models.users import Role, User

router = APIRouter()


@router.post("/journals", response_model=Journal)
async def create_journal(
    journal: JournalCreate, user: User = Depends(require_role(Role.EDITOR))
):
    existing_journal = await Journal.find_one(Journal.title == journal.title)
    if existing_journal:
        raise HTTPException(status_code=400, detail="Journal already registered")
    new_journal = Journal(
        **journal.model_dump(),
        author=user,
    )
    await new_journal.insert()
    return new_journal


@router.get("/journals")
async def list_journals():
    journals = await Journal.find_all().to_list()
    return journals


@router.get("/journals/{journal_id}")
async def get_user(journal_id: str):
    journal = await Journal.get(journal_id)
    if not journal:
        raise HTTPException(status_code=404, detail="Journal not found")
    return journal


@router.put("/journals/{journal_id}", response_model=Journal)
async def update_journal(
    journal_id: PydanticObjectId,
    journal_update: JournalUpdate,
    user: User = Depends(require_role(Role.EDITOR)),
):
    existing_journal = await Journal.get(journal_id)
    if not existing_journal:
        raise HTTPException(status_code=404, detail="Journal not found")

    update_data = journal_update.model_dump(exclude_unset=True)

    if "entries" in update_data:
        update_data["entries"] = [
            Entry(**entry).model_dump() for entry in update_data["entries"]
        ]

    update_query = {"$set": update_data}
    update_query["$set"]["updated_date"] = datetime.now(timezone.utc)

    await existing_journal.update(update_query)
    return await Journal.get(journal_id)


@router.delete("/journals/{journal_id}")
async def delete_journal(
    journal_id: PydanticObjectId, user: User = Depends(require_role(Role.ADMIN))
):
    existing_journal = await Journal.get(journal_id)
    if not existing_journal:
        raise HTTPException(status_code=404, detail="Journal not found")

    await existing_journal.delete()
    return {"message": "Journal deleted successfully"}

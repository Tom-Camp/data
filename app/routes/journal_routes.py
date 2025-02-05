from datetime import datetime

from _zoneinfo import ZoneInfo
from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException

from app.auth import get_current_user
from app.models.journals import Entry, Journal

router = APIRouter()


@router.post("/journals", response_model=Journal)
async def create_journal(
    journal: Journal, current_user: str = Depends(get_current_user)
):
    await journal.insert()
    return journal


@router.get("/journals")
async def list_journals():
    journals = await Journal.find_all().to_list()
    return journals


@router.get("/journals/{journal_id}")
async def get_user(journal_id: str):
    journal = await Journal.get(journal_id)
    return journal


@router.put("/journals/{journal_id}", response_model=Journal)
async def update_journal(
    journal_id: PydanticObjectId,
    journal_update: Journal,
    current_user: str = Depends(get_current_user),
):
    existing_journal = await Journal.get(journal_id)
    if not existing_journal:
        raise HTTPException(status_code=404, detail="Journal not found")

    update_data = journal_update.model_dump(exclude_unset=True)
    update_data["updated_date"] = datetime.now(ZoneInfo("America/New_York"))

    if "entries" in update_data:
        update_data["entries"] = [
            Entry(**entry).model_dump() for entry in update_data["entries"]
        ]

    update_query = {"$set": update_data}

    await existing_journal.update(update_query)
    return await Journal.get(journal_id)

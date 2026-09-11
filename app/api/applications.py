from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db, User
from app.models.application import JobApplication
from app.services.application_service import (
   create_application,
   delete_application,
   get_application,
   get_applications,
)
from app.api.dependencies import get_current_user

applications_router = APIRouter(
    prefix="/applications",
    tags = ["applications"]
)

DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]

@applications_router.get("")
async def get_all_applications(current_user: CurrentUser, db: DbSession):
   applications = await get_applications(db)
   return applications


@applications_router.get("/{application_id}")
async def get_app(current_user: CurrentUser, application_id : int, db: DbSession):
    application = await get_application(application_id, db)

    if application:
        return application
    raise HTTPException(status_code=404, detail="Application not found")


@applications_router.post("")
async def make_application(current_user: CurrentUser, application : JobApplication, db: DbSession):
    success = await create_application(application, db)

    if success:
        return success
    raise HTTPException(status_code=409, detail="Duplicate Request")


@applications_router.delete("/{application_id}")
async def delete(current_user: CurrentUser, application_id: int, db: DbSession):
    success = await delete_application(application_id, db)
    if success:
        return {"message": "Item deleted"}
    raise HTTPException(status_code=404, detail="Application not found")


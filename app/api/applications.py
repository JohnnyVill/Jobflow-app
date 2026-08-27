from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.application import JobApplication
from app.services.application_service import (
   create_application,
   delete_application,
   get_application,
   get_applications,
)

applications_router = APIRouter(
    prefix="/applications",
    tags = ["applications"]
)


@applications_router.get("")
async def get_all_applications(db: AsyncSession = Depends(get_db)):
   applications = await get_applications(db)
   return applications


@applications_router.get("/{application_id}")
async def get_app(application_id : int, db: AsyncSession = Depends(get_db)):
    application = await get_application(application_id, db)

    if application:
        return application
    raise HTTPException(status_code=404, detail="Application not found")


@applications_router.post("")
async def make_application(application : JobApplication, db: AsyncSession = Depends(get_db)):
    success = await create_application(application, db)

    if success:
        return success
    raise HTTPException(status_code=409, detail="Duplicate Request")


@applications_router.delete("/{application_id}")
async def delete(application_id: int, db: AsyncSession = Depends(get_db)):
    success = await delete_application(application_id, db)
    if success:
        return {"message": "Item deleted"}
    raise HTTPException(status_code=404, detail="Application not found")


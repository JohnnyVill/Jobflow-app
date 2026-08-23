from fastapi import APIRouter, HTTPException

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
def get_all_applications():
    return get_applications()

@applications_router.get("/{application_id}")
def get_app(application_id : int):
    application = get_application(application_id)
    if application:
        return application
    raise HTTPException(status_code=404, detail="Application not found")

@applications_router.post("")
def make_application(application : JobApplication):
    success = create_application(application)
    if success:
        return success
    raise HTTPException(status_code=409, detail="Duplicate Request")

@applications_router.delete("/{application_id}")
def delete(application_id: int):
    success = delete_application(application_id)
    if success:
        return {"message": "Item deleted"}
    raise HTTPException(status_code=404, detail="Application not found")


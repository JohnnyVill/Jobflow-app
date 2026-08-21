from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from enum import StrEnum

class ApplicationStatus(StrEnum):
    APPLIED = "applied"
    REJECTED = "rejected"
    INTERVIEW = "interview"
    OFFER = "offer"

#how incoming json request body should be interpreted
class JobApplication(BaseModel):
    id: int 
    company: str 
    position: str 
    status: ApplicationStatus

class ApplicationStorage:   
    applications: list[JobApplication] = []

app = FastAPI(
    title="Jobflow API",
    version="0.1.0",
)

@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Jobflow API is running, Image update"}

@app.post("/applications")
def create_application(application: JobApplication):
    #check if application already exist
    applicant_id = application.id
    for app in ApplicationStorage.applications:
        if applicant_id == app.id:
            raise HTTPException(
                status_code=409,
                detail="Application ID already"
            )
    
    ApplicationStorage.applications.append(application)
    return application

@app.get("/applications")
def get_applications():
    return ApplicationStorage.applications

@app.get("/applications/{application_id}")
def get_application(application_id: int):
    for application in ApplicationStorage.applications:
        if application_id == application.id:
            return application
    
    raise HTTPException(status_code=404, detail="Application not found")

@app.delete("/applications/{application_id}")
def delete_application(application_id: int):
    applicationStorage = ApplicationStorage.applications
    for index in  range(len(applicationStorage)):
        if application_id == applicationStorage[index].id:
            del applicationStorage[index]
            return {"message": "Item deleted"}
    raise HTTPException(status_code=404, detail="Application not found")
   

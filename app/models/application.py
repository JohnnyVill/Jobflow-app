from enum import StrEnum
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ApplicationStatus(StrEnum):
    APPLIED = "applied"
    REJECTED = "rejected"
    INTERVIEW = "interview"
    OFFER = "offer"

#how incoming json request body should be interpreted
class JobApplication(BaseModel):
    company: str 
    position: str 
    status: ApplicationStatus

class UserCreation(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id:int
    email:str
    created_at:datetime

    model_config = ConfigDict(for_attributes=True)
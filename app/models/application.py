from enum import StrEnum

from pydantic import BaseModel


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
from typing import ClassVar

from app.models.application import JobApplication


class ApplicationStorage:   
    applications: ClassVar[list[JobApplication]] = []


def create_application(application: JobApplication):
    #check if application already exist
    applicant_id = application.id
    for app in ApplicationStorage.applications:
        if applicant_id == app.id:
            return None
    ApplicationStorage.applications.append(application)
    return application


def get_applications():
    return ApplicationStorage.applications


def get_application(application_id: int):
    for application in ApplicationStorage.applications:
        if application_id == application.id:
            return application
    
    return None


def delete_application(application_id: int):
    application_storage = ApplicationStorage.applications
    for index in  range(len(application_storage)):
        if application_id == application_storage[index].id:
            del application_storage[index]
            return True
    return False
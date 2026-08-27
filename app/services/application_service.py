from typing import ClassVar
from collections.abc import AsyncGenerator

from fastapi import FastAPI, Depends


from app.models.application import JobApplication

from app.db.database import async_session_local, Application
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class ApplicationStorage:   
    applications: ClassVar[list[JobApplication]] = []

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_local() as session:
        yield session

async def create_application(application: JobApplication, db: AsyncSession = Depends(get_db)):
    #check if application already exist
    applicant_id = application.id 
    async with db.begin():
        new_application = Application(
            company=application.company,
            position=application.position,
            status=application.status
        )
        await db.refresh(new_application)
        print(f"Inserted User ID: {new_application.id}, {new_application.company}")


async def get_applications(db: AsyncSession = Depends(get_db)):
    applications = await db.execute(select(Application))
    return applications.scalars().all()

    


async def get_application(application_id: int, db: AsyncSession = Depends(get_db)):
    statement = select(Application).where(Application.id == application_id)
    application = await db.scalars(statement)
    return application.all()


def delete_application(application_id: int):
    application_storage = ApplicationStorage.applications
    for index in  range(len(application_storage)):
        if application_id == application_storage[index].id:
            del application_storage[index]
            return True
    return False
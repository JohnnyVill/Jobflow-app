from app.models.application import JobApplication
from app.db.database import Application

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError



async def create_application(application: JobApplication, db: AsyncSession):
    #check if application already exist
    try:
        async with db.begin():
            new_application = Application(
                company=application.company,
                position=application.position,
                status=application.status
            )
            db.add(new_application)
            print(f"Inserted User ID: {new_application.id}, {new_application.company}")
            return new_application
    except IntegrityError:
        return None

async def get_applications(db: AsyncSession):
    applications = await db.execute(select(Application))
    return applications.scalars().all()

    
async def get_application(application_id: int, db: AsyncSession):
    statement = select(Application).where(Application.id == application_id)
    application = await db.execute(statement)
    return application.scalar_one_or_none()


async def delete_application(application_id: int, db: AsyncSession):
    result = await db.execute(
        delete(Application)
        .where(Application.id == application_id)
        .returning(Application.id, Application.company, Application.position)
    )
    deleted_application = result.first()
    await db.commit()
    return deleted_application
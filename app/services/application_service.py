from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import Application
from app.models.application import JobApplication


async def create_application(application: JobApplication, db: AsyncSession):
    #check if application already exist
    try:
        
        new_application = Application(
            company=application.company,
            position=application.position,
            status=application.status
        )
        db.add(new_application)
        await db.commit()
        await db.refresh(new_application)
        return new_application
    except IntegrityError:
        await db.rollback()
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
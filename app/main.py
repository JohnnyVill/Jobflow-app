from fastapi import FastAPI
from app.api.applications import applications_router


app = FastAPI(
    title="Jobflow API",
    version="0.1.0",
)
@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Jobflow API is running, Image update"}

app.include_router(applications_router)

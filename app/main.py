from fastapi import FastAPI

app = FastAPI(
    title="Jobflow API",
    version="0.1.0",
)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Jobflow API is running"}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}
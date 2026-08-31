# JobFlow

JobFlow is an AI-powered career operating system designed to help job seekers
manage applications, tailor resumes, generate cover letters, prepare for
interviews, and automate repetitive parts of the job search.

The project is currently in early backend development. The current version
provides a REST API for managing job applications using in-memory storage.

## Current Features

- Create a job application
- Retrieve all job applications
- Retrieve a job application by ID
- Delete a job application
- Validate application status
- Prevent duplicate application IDs
- Handle missing applications with HTTP errors
- Automated API testing with pytest

## Tech Stack

- Python 3.13
- FastAPI
- Pydantic
- Pytest
- HTTPX2
- uv
- Docker
- PostgreSQL,
- SQLAlchemy
- Alembic

## Project Structure

```text
app/
├── api/
│   └── applications.py
├── models/
│   └── application.py
├── services/
│   └── application_service.py
└── main.py

tests/
└── ...
```

### Architecture

The application currently separates responsibilities into three layers:

- `api` - FastAPI routes and HTTP handling
- `models` - request/domain models and validation
- `services` - application logic and in-memory storage

## API Endpoints

| Method | Endpoint                         | Description               |
| ------ | -------------------------------- | ------------------------- |
| GET    | `/`                              | API health/root endpoint  |
| POST   | `/applications`                  | Create an application     |
| GET    | `/applications`                  | Retrieve all applications |
| GET    | `/applications/{application_id}` | Retrieve one application  |
| DELETE | `/applications/{application_id}` | Delete an application     |

## Requirements

- Python 3.13
- uv
- Docker Desktop

## Run Locally

Install the dependencies:

```bash
uv sync
```

Start the FastAPI development server:

```bash
uv run fastapi dev app/main.py
```

Then open the interactive API documentation at:

```text
http://localhost:8000/docs
```

## Run Tests

make sure docker container is running

```bash
docker compose exev api uv run -m pytest
```

## Project Status

JobFlow is currently under active development.

### Completed

- FastAPI project setup
- Application CRUD foundation
- Pydantic validation
- Service/router/model separation
- HTTP error handling
- Automated API tests
- PostgreSQL persistence
- SQLAlchemy ORM
- Database migrations with Alembic

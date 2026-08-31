# JobFlow

JobFlow is a backend application for managing job applications and is being developed as the foundation for a larger career-management platform.

The current version provides a REST API built with FastAPI and PostgreSQL. It supports persistent application storage, request validation, duplicate protection, database migrations, and isolated integration testing against a dedicated PostgreSQL test database.

## Current Features

- Create a job application
- Retrieve all job applications
- Retrieve a job application by ID
- Delete a job application
- Persist application data in PostgreSQL
- Validate application status with Pydantic
- Prevent duplicate applications using a database unique constraint
- Return appropriate HTTP errors for duplicate and missing applications
- Manage database schema changes with Alembic
- Run the API and PostgreSQL services with Docker Compose
- Run asynchronous API integration tests with pytest and HTTPX
- Use a dedicated PostgreSQL database for isolated testing
- Reset test data between tests without affecting development data

## Tech Stack

- Python 3.13+
- FastAPI
- Pydantic
- PostgreSQL 17
- SQLAlchemy 2
- asyncpg
- Alembic
- Pytest
- pytest-asyncio
- HTTPX2
- uv
- Docker
- Docker Compose
- Ruff

## Project Structure

```text
jobflow-app/
├── alembic/
│   └── versions/
├── app/
│   ├── api/
│   │   └── applications.py
│   ├── db/
│   │   └── database.py
│   ├── models/
│   │   └── application.py
│   ├── services/
│   │   └── application_service.py
│   ├── tests/
│   │   └── api_routes_test.py
│   └── main.py
├── alembic.ini
├── compose.yaml
├── Dockerfile
├── pyproject.toml
├── uv.lock
└── README.md
```

## Architecture

JobFlow currently separates responsibilities across several layers.

### API Layer

`app/api/`

Contains the FastAPI routes and HTTP-specific behavior such as:

- request handling
- dependency injection
- status codes
- HTTP exceptions

### Service Layer

`app/services/`

Contains application and database operations such as:

- creating applications
- querying applications
- deleting applications
- handling persistence logic

### Models

`app/models/`

Contains Pydantic models and application validation, including supported application statuses.

### Database Layer

`app/db/`

Contains:

- SQLAlchemy async engines
- sessionmakers
- FastAPI database dependency
- SQLAlchemy ORM models
- production and test database configuration

### Database Migrations

`alembic/`

Alembic manages schema changes so the PostgreSQL schema can evolve alongside the application.

## API Endpoints

| Method | Endpoint                         | Description                   |
| ------ | -------------------------------- | ----------------------------- |
| GET    | `/`                              | Root / health endpoint        |
| POST   | `/applications`                  | Create a job application      |
| GET    | `/applications`                  | Retrieve all applications     |
| GET    | `/applications/{application_id}` | Retrieve an application by ID |
| DELETE | `/applications/{application_id}` | Delete an application         |

## Application Statuses

Applications support the following statuses:

```text
applied
interview
offer
rejected
```

Invalid status values are rejected during request validation.

## Database Architecture

JobFlow currently uses two separate PostgreSQL databases.

```text
Development
FastAPI
   ↓
get_db
   ↓
async_session_local
   ↓
engine
   ↓
jobflow
```

The development database contains normal application data.

Testing uses a completely separate database:

```text
Testing
pytest / HTTPX
   ↓
FastAPI
   ↓
dependency override
   ↓
async_test_session_local
   ↓
test_engine
   ↓
test_jobflow
```

This prevents automated tests from modifying development data.

The test database can safely be truncated and reset between tests because it exists only for testing.

## Docker Services

The Docker Compose environment currently contains three primary services:

```text
api
db
test_db
```

### `api`

Runs the FastAPI application and contains the Python dependencies used by the project.

### `db`

Runs the PostgreSQL development database:

```text
jobflow
```

### `test_db`

Runs a separate PostgreSQL database:

```text
test_jobflow
```

used exclusively by pytest.

## Docker Networking

The development database is available to containers at:

```text
db:5432
```

The test database is available to containers at:

```text
test_db:5432
```

The test PostgreSQL container is also exposed to the host as:

```text
localhost:5433
```

Docker Compose port mappings use:

```text
HOST_PORT:CONTAINER_PORT
```

so:

```text
5433:5432
```

means port `5433` on the host forwards to PostgreSQL port `5432` inside the test database container.

## Requirements

Install:

- Docker Desktop
- Git

Python 3.13+ and `uv` are useful for local tooling, although the normal project workflow runs the application and tests inside Docker.

The Python project itself requires Python 3.13 or newer.

## Running the Project

### 1. Clone the repository

```bash
git clone https://github.com/JohnnyVill/Jobflow-app.git
cd Jobflow-app
```

### 2. Start the Docker environment

```bash
docker compose up -d
```

To rebuild the API image after dependency, Dockerfile, or copied-source changes:

```bash
docker compose up -d --build
```

### 3. Check container status

```bash
docker compose ps
```

### 4. Open the API documentation

Once the API is running:

```text
http://localhost:8000/docs
```

FastAPI provides interactive Swagger documentation at this endpoint.

## Database Migrations

JobFlow uses Alembic for schema migrations.

### Apply migrations to the development database

```bash
docker compose exec api alembic upgrade head
```

### Create a new migration

After changing SQLAlchemy models:

```bash
docker compose exec api alembic revision --autogenerate -m "migration description"
```

Review the generated migration before applying it.

Then run:

```bash
docker compose exec api alembic upgrade head
```

## Initializing the Test Database

Creating the PostgreSQL database does not automatically create the application's tables.

The test database therefore needs the same Alembic schema as the development database.

Apply the migrations to `test_jobflow` with:

```bash
docker compose exec \
  -e DATABASE_URL=postgresql+asyncpg://test_postgres:test_postgres@test_db:5432/test_jobflow \
  api alembic upgrade head
```

This temporarily points Alembic at the isolated test database for that command.

The development and test databases should have:

```text
same schema
different data
```

## Running Tests

Make sure the Docker services are running:

```bash
docker compose up -d
```

Then run:

```bash
docker compose exec api uv run python -m pytest -v
```

Current test status:

```text
8 passed
```

The current test suite covers:

- creating applications
- duplicate application handling
- retrieving all applications
- retrieving an application by ID
- deleting an application
- retrieving a missing application
- deleting a missing application
- invalid request validation

## Test Isolation

Tests override FastAPI's normal database dependency.

Normally:

```text
Depends(get_db)
   ↓
development database
```

During tests:

```text
Depends(get_db)
   ↓
FastAPI dependency override
   ↓
test database
```

This is important because creating a test SQLAlchemy session alone does not automatically make the FastAPI routes use it.

The dependency must also be overridden.

## Test Cleanup

Before each test, the `applications` table in the test database is reset using:

```sql
TRUNCATE TABLE applications
RESTART IDENTITY
CASCADE;
```

This provides each test with a predictable starting state.

### Why use a separate database instead of clearing the development database?

Clearing the development table would still mean tests were directly modifying application data.

As JobFlow gains additional tables and foreign-key relationships, destructive test operations could affect related development records.

Using `test_jobflow` provides a controlled environment where tests can:

- insert arbitrary data
- intentionally cause errors
- delete records
- reset primary-key sequences
- truncate tables
- test edge cases

without affecting development data.

## Useful Commands

Start containers:

```bash
docker compose up -d
```

Start and rebuild:

```bash
docker compose up -d --build
```

Check running containers:

```bash
docker compose ps
```

Run tests:

```bash
docker compose exec api uv run python -m pytest -v
```

Apply migrations:

```bash
docker compose exec api alembic upgrade head
```

View logs:

```bash
docker compose logs
```

Follow logs:

```bash
docker compose logs -f
```

Stop the environment:

```bash
docker compose down
```

## Current Project Status

JobFlow is under active backend development.

### Completed

- FastAPI project setup
- Router / service / model separation
- Application CRUD foundation
- PostgreSQL persistence
- Async SQLAlchemy integration
- PostgreSQL application model
- Application status validation
- Duplicate application protection
- HTTP error handling
- Alembic configuration
- Database migrations
- Dockerized API
- Dockerized PostgreSQL development database
- Dedicated PostgreSQL test database
- FastAPI dependency overrides for testing
- Asynchronous HTTP integration testing
- Per-test database cleanup
- 8 passing API integration tests

### Current Backend Foundation

The application now has a working path through:

```text
HTTP Request
   ↓
FastAPI
   ↓
Dependency Injection
   ↓
Service Layer
   ↓
SQLAlchemy
   ↓
PostgreSQL
```

The test suite exercises the same application stack while replacing the production database dependency with an isolated test database.

## Development Goal

JobFlow is being built toward a production-style backend rather than only a CRUD demonstration.

Future development will continue expanding the system with additional backend features, related database models, authentication, stronger testing infrastructure, and other capabilities as the project grows.

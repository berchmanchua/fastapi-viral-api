# FastAPI Template 🚀

A robust, production-ready FastAPI template designed for high performance and maintainability, using viral items as the example domain.

## Architectural Highlights

* **High-Throughput Asynchronous Core:** Powered by **`uvloop`** (a Cython drop-in replacement for the standard asyncio event loop) and **`httptools`** for C-based HTTP parsing.

* **Lightning-Fast JSON Serialization:** Uses **`orjson`** (written in Rust) globally for zero-copy serialization and deserialization, bypassing standard Python JSON bottlenecks.

* **Asynchronous PostgreSQL:** Utilizes **`asyncpg`** for non-blocking database operations and connection pooling.

* **In-Memory Read-Through Caching:** Integrated with **`valkey`** (an ultra-fast Redis fork) to serve read requests from memory with a configurable Time-To-Live (TTL).

* **Clean Architecture:** Strictly decoupled layers (`API Routes` $\rightarrow$ `Service Layer` $\rightarrow$ `Database/Cache`) for maximum maintainability and testability.

* **Version-Controlled Migrations:** Managed via **Alembic** with asynchronous database support.

## Project Structure

```
fastapi-template/
├── alembic/                  # Database migration scripts & env configuration
│   └── versions/
├── app/
│   ├── api/
│   │   ├── dependencies.py   # Dependency injection (Services, DB pools, Cache)
│   │   └── v1/
│   │       ├── endpoints/    # HTTP route handlers (Items, etc.)
│   │       └── router.py     # API router aggregation
│   ├── core/
│   │   ├── config.py         # Pydantic BaseSettings & environment validation
│   │   └── database.py       # Asyncpg & Valkey connection pool lifecycle
│   ├── schemas/
│   │   └── item.py           # Pydantic v2 validation models
│   └── services/
│       └── item_service.py   # Business logic, SQL queries, and caching layer
│   └── main.py               # FastAPI application entrypoint
├── alembic.ini               # Alembic configuration
├── Dockerfile                # Multi-stage production container build
├── docker-compose.yml        # Local development orchestration with hot-reload
├── requirements.txt          # Pinned dependency manifest
└── .env.example              # Environment variable template
```

## Quick Start (Docker Compose)

The fastest way to spin up the entire stack (FastAPI, PostgreSQL, and Valkey) with live code-reloading is using Docker Compose.

1. Clone or extract the project and navigate to the root directory.

2. Copy the environment template:

   ```bash
   cp .env.example .env
   ```

3. Build and launch the containers:

   ```bash
   docker compose up --build -d
   ```

4. View the interactive API documentation (Swagger UI):
   👉 [**http://localhost:8000/docs**](http://localhost:8000/docs)

## Environment Variables

Configuration is handled securely via `pydantic-settings`. The application fails fast at startup if required variables are missing.

| Variable | Description | Default (Local Dev) |
| :--- | :--- | :--- |
| `DATABASE_URL` | PostgreSQL DSN connection string | `postgresql://viraluser:viralpass@postgres:5432/viraldb` |
| `VALKEY_URL` | Valkey/Redis DSN connection string | `redis://valkey:6379/0` |
| `DB_POOL_MIN_SIZE` | Minimum Postgres pool connections | `5` |
| `DB_POOL_MAX_SIZE` | Maximum Postgres pool connections | `20` |
| `CACHE_TTL_SECONDS` | Cache expiration time for items | `3600` |

## API Endpoints Reference

### 1. Create an Item

Saves the record to PostgreSQL and immediately warms the Valkey cache.

* **URL:** `POST /api/v1/items/`
* **Payload:**
  ```json
  {
    "name": "Viral FastAPI Setup",
    "description": "Blazing fast asynchronous Python backend",
    "platform": "tiktok",
    "tags": ["python", "fastapi", "performance"]
  }
  ```

### 2. Get an Item (Read-Through Cache)

Checks Valkey in memory first. On a cache miss, queries PostgreSQL and caches the result.

* **URL:** `GET /api/v1/items/{item_id}`

### 3. Update an Item (Partial Patch)

Updates records in PostgreSQL using `COALESCE` and invalidates/refreshes the Valkey cache in a single roundtrip.

* **URL:** `PATCH /api/v1/items/{item_id}`
* **Payload:**
  ```json
  {
    "viral_score": 999.9,
    "tags": ["trending", "viral"]
  }
  ```

### 4. Soft Delete an Item

Sets `deleted_at` timestamp in PostgreSQL and evicts the key from Valkey immediately (`204 No Content`).

* **URL:** `DELETE /api/v1/items/{item_id}`

## Database Migrations (Alembic)

To create a new schema migration after making changes:

1. Generate a migration revision:
   ```bash
   docker compose exec api python -m alembic revision -m "description of changes"
   ```

2. Apply migrations to the database:
   ```bash
   docker compose exec api python -m alembic upgrade head
   ```

## Local Development (Without Docker)

If you prefer running the API natively on your host machine:

1. Install Python 3.12+ and dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Ensure local instances of PostgreSQL and Valkey are running.

3. Export your environment variables or create a `.env` file.

4. Run database migrations:
   ```bash
   python -m alembic upgrade head
   ```

5. Start the development server with Uvicorn:
   ```bash
   uvicorn app.main:app --reload --loop uvloop --http httptools
   ```
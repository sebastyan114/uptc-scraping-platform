from fastapi import FastAPI, HTTPException
from qdrant_client import AsyncQdrantClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.core.config import get_settings


settings = get_settings()

database_engine: AsyncEngine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
)


app = FastAPI(
    title=settings.app_name,
    description=(
        "API para scraping, detección de protecciones "
        "y análisis de vulnerabilidades web"
    ),
    version=settings.app_version,
)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "message": "UPTC Scraping Platform API funcionando",
        "version": settings.app_version,
        "environment": settings.app_env,
    }


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "backend",
        "environment": settings.app_env,
    }


@app.get("/health/postgres")
async def postgres_health_check() -> dict[str, str]:
    try:
        async with database_engine.connect() as connection:
            await connection.execute(text("SELECT 1"))

        return {
            "status": "ok",
            "service": "postgres",
        }

    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"PostgreSQL no disponible: {error}",
        )


@app.get("/health/qdrant")
async def qdrant_health_check() -> dict[str, str]:
    client = AsyncQdrantClient(url=settings.qdrant_url)

    try:
        await client.get_collections()

        return {
            "status": "ok",
            "service": "qdrant",
        }

    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"Qdrant no disponible: {error}",
        )

    finally:
        await client.close()
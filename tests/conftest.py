import logging
from collections.abc import AsyncGenerator, Callable
from pathlib import Path
from typing import Any
from urllib.parse import urlparse, urlunparse

import pytest
import sqlalchemy
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.operations import Operations
from alembic.runtime.migration import RevisionStep
from alembic.script import ScriptDirectory
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pydantic import PostgresDsn
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    create_async_engine,
)

from apat.api.main import app
from apat.database.database import ConnectionFactory, engine, metadata
from apat.database.database import conn_factory as real_conn_factory
from apat.settings import settings

LOGGER = logging.getLogger(__name__)
type AppURLResolver[**P] = Callable[[str, P.kwargs], str]


@pytest.fixture(scope="session")
def anyio_backend() -> tuple[str, Any]:
    return "asyncio", {"use_uvloop": True}


@pytest.fixture(scope="function")
async def test_app(
    conn_factory: ConnectionFactory,
) -> FastAPI:
    app.dependency_overrides[real_conn_factory] = lambda: conn_factory
    return app


@pytest.fixture(scope="function")
async def url_resolve(test_app: FastAPI) -> AppURLResolver:
    return lambda x, **path_params: test_app.url_path_for(x, **path_params)


@pytest.fixture(scope="function")
async def test_client(
    test_app: FastAPI,
) -> AsyncGenerator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as client:
        yield client


@pytest.fixture(scope="session")
async def real_db_engine() -> AsyncEngine:
    return engine


@pytest.fixture(scope="session")
async def test_db_url() -> PostgresDsn:
    url = urlparse(str(settings.database_dsn))
    return PostgresDsn(urlunparse(url._replace(path=f"{url.path}_test")))


@pytest.fixture(scope="session")
async def test_db_engine(test_db_url: PostgresDsn) -> AsyncEngine:
    return create_async_engine(str(test_db_url))


@pytest.fixture(autouse=True, scope="session")
async def setup_database(
    real_db_engine: AsyncEngine, test_db_url: PostgresDsn, test_db_engine: AsyncEngine
) -> AsyncGenerator[None, tuple[PostgresDsn, AsyncEngine]]:
    async with real_db_engine.connect() as temp_connection:
        await temp_connection.execution_options(isolation_level="AUTOCOMMIT")
        await create_test_database(temp_connection, test_db_url)
    await temp_connection.close()
    await real_db_engine.dispose()

    async with test_db_engine.connect() as temp_connection:
        await temp_connection.run_sync(migrate_test_db, test_db_url=test_db_url)
    await temp_connection.close()


@pytest.fixture(scope="function")
async def db_conn(test_db_engine: AsyncEngine) -> AsyncConnection:
    async with test_db_engine.connect() as connection:
        # await conn.execution_options(isolation_level="AUTOCOMMIT")
        await connection.begin()
        await connection.begin_nested()
        try:
            yield connection
        finally:
            await connection.rollback()
            await connection.close()


@pytest.fixture(scope="function")
async def conn_factory(
    db_conn: AsyncConnection,
) -> ConnectionFactory:
    """
    Creates a session maker that is bound to the test database.
    """

    def _session_factory():
        return db_conn

    _session_factory.is_fake = True
    return _session_factory


def migrate_test_db(
    connection: sqlalchemy.Connection, test_db_url: PostgresDsn
) -> None:
    config = Config(Path(__file__).parent.parent / "alembic.ini")
    config.set_main_option("sqlalchemy.url", str(test_db_url))

    script = ScriptDirectory.from_config(config)

    def upgrade(rev: Any, context: Any) -> list[RevisionStep]:
        return script._upgrade_revs("head", rev)  # type: ignore

    context = MigrationContext.configure(
        connection, opts={"target_metadata": metadata, "fn": upgrade}
    )

    with context.begin_transaction():
        with Operations.context(context):
            context.run_migrations()


async def create_test_database(
    connection: AsyncConnection, test_db_url: PostgresDsn
) -> None:
    if test_db_url.path is None:
        raise ValueError("test_db_url.path is empty")

    db_name = test_db_url.path.lstrip("/")

    await connection.execute(sqlalchemy.text(f'DROP DATABASE IF EXISTS "{db_name}"'))
    await connection.execute(sqlalchemy.text(f'CREATE DATABASE "{db_name}"'))

    LOGGER.info("Created test database.")

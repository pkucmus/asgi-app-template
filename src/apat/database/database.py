from collections.abc import AsyncGenerator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager

from sqlalchemy import (
    MetaData,
)
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from apat.settings import settings

type SessionFactory = Callable[[], AbstractAsyncContextManager[AsyncSession]]
type ConnectionFactory = Callable[[], AbstractAsyncContextManager[AsyncConnection]]
engine = create_async_engine(str(settings.database_dsn))
autocommit_engine = engine.execution_options(isolation_level="AUTOCOMMIT")
_sessionmaker = async_sessionmaker(autocommit=False, bind=engine)
metadata = MetaData()


@asynccontextmanager
async def db_session() -> AsyncGenerator[AsyncSession]:
    """
    This opens a new session which is susceptible to the connection exhaustion problem.
    If you were to open this as a FastAPI dependency you will open a DB transaction on
    first DB execute and give the connection back to the pool only after the endpoint
    handler finishes.

    Instead, use the `session_factory` dependency which will open a new session for each
    request and close it after the request is finished.
    """
    session = _sessionmaker()
    # session = await engine.connect()
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


def session_factory() -> SessionFactory:
    return db_session


@asynccontextmanager
async def db_conn(autocommit: bool = False) -> AsyncGenerator[AsyncConnection]:
    """
    ...
    """
    if autocommit:
        conn = await autocommit_engine.connect()
    else:
        conn = await engine.connect()
    try:
        yield conn
    except Exception:
        await conn.rollback()
        raise
    finally:
        await conn.close()


def conn_factory() -> ConnectionFactory:
    return db_conn

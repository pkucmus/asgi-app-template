from typing import Annotated

from fastapi import Depends

from apat.database.database import (
    ConnectionFactory,
    SessionFactory,
    conn_factory,
    session_factory,
)

DBSessionDep = Annotated[
    SessionFactory,
    Depends(session_factory),
]

DBConnDep = Annotated[
    ConnectionFactory,
    Depends(conn_factory),
]

from typing import Any

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_dsn: PostgresDsn


settings = Settings()


LOGGING: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "rich": {
            # "format": "%(message)s",
            "format": "[%(name)s] %(message)s",
            "datefmt": "[%X]",
        },
    },
    "handlers": {
        "default": {
            "class": "rich.logging.RichHandler",
            "formatter": "rich",
            "rich_tracebacks": True,
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["default"],
    },
    "loggers": {
        "uvicorn": {"level": "INFO", "handlers": ["default"], "propagate": False},
        "sqlalchemy": {"level": "INFO", "handlers": ["default"], "propagate": False},
        "apat": {"level": "DEBUG", "handlers": ["default"], "propagate": False},
    },
}

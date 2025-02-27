# ASGI Template

Looking for ways to quickly build maintainable Python apps.

Design principles:
1. ORM is disallowed - queries must be built manually
2. Strict typing
3. API, Business, Database layers must be separated

To run this:

```shell
docker compose up -d db
export DATABASE_DSN="postgresql+asyncpg://user:password@localhost:6666/db"
uv run python src/apat/api/main.py

uv run pytest tests
```

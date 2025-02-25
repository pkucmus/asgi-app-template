from fastapi import FastAPI

from apat.customers.endpoints import router as customers_router
from apat.settings import LOGGING

app = FastAPI()

app.include_router(customers_router, prefix="/customers")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "apat.api.main:app", host="0.0.0.0", port=8000, reload=True, log_config=LOGGING
    )

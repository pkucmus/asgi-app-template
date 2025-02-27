from typing import Any

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.pytest_plugin import register_fixture
from sqlalchemy.ext.asyncio import AsyncConnection

from apat.customers import models, schema
from apat.customers.crud import AddressCRUD
from tests.utils.factory import CustomModelFactory, DBFactory


@register_fixture
class AddressModelFactory(CustomModelFactory[models.Address]): ...


@register_fixture
class AddressSchemaFactory(ModelFactory[schema.AddressResponse]): ...


@register_fixture
class AddressCreateSchemaFactory(ModelFactory[schema.AddressCreate]): ...


@pytest.fixture
async def address_db_factory(
    db_conn: AsyncConnection, address_model_factory: ModelFactory[models.Address]
) -> DBFactory[models.Address]:
    async def inner(**kwargs: Any) -> models.Address:
        address = address_model_factory.build(**kwargs)
        result = await AddressCRUD.create(
            db_conn,
            street=address.street,
            city=address.city,
            state=address.state,
            zip_code=address.zip_code,
        )
        await db_conn.commit()
        return result

    return inner

import pytest
from sqlalchemy.ext.asyncio import AsyncConnection

from apat.customers.crud import AddressCRUD
from apat.customers.models import Address
from tests.utils.factory import DBFactory

pytestmark = pytest.mark.anyio


async def test_create_address(db_conn: AsyncConnection):
    assert await AddressCRUD.get_all(db_conn) == []

    address = await AddressCRUD.create(
        db_conn, street="123 Main St", city="Springfield", state="IL", zip_code="62701"
    )
    assert address.street == "123 Main St"
    assert address.city == "Springfield"
    assert address.state == "IL"
    assert address.zip_code == "62701"


async def test_get_all_addresses(
    db_conn: AsyncConnection, address_db_factory: DBFactory[Address]
):
    await address_db_factory()
    addresses = await AddressCRUD.get_all(db_conn)
    assert len(addresses) == 1

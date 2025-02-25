from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from apat.customers.crud import AddressCRUD, CustomerCRUD
from apat.customers.schema import (
    AddressCreate,
    AddressResponse,
    AddressWithCustomersResponse,
    CustomerCreate,
    CustomerResponse,
    CustomerWithAddressResponse,
)
from apat.database.deps import DBConnDep, DBSessionDep

router = APIRouter()
DBConnDep, DBSessionDep


@router.get("/customers/")
async def get_customers(
    get_db: DBConnDep,
):
    async with get_db() as conn:
        customers = await CustomerCRUD.get_all(conn)

    return [CustomerResponse.from_model(customer) for customer in customers]


@router.get("/customers/{bid}")
async def get_customer(
    bid: UUID,
    get_db: DBConnDep,
):
    async with get_db() as conn:
        customer = await CustomerCRUD.get_by_id_with_customer(conn, bid)

    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return CustomerWithAddressResponse.from_model(customer)


@router.post("/customers/")
async def create_customer(
    customer: CustomerCreate,
    get_db: DBConnDep,
):
    async with get_db() as conn:
        new_customer = await CustomerCRUD.create(conn, **customer.dict())
        await conn.commit()

    return CustomerResponse.from_model(new_customer)


@router.get("/addresses/")
async def get_addresses(
    get_db: DBConnDep,
):
    async with get_db() as conn:
        addresses = await AddressCRUD.get_all(conn)

    return [AddressResponse.from_model(address) for address in addresses]


@router.post("/addresses/")
async def create_address(
    address: AddressCreate,
    get_db: DBConnDep,
):
    async with get_db() as conn:
        new_address = await AddressCRUD.create(conn, **address.dict())
        await conn.commit()

    return AddressResponse.from_model(new_address)


@router.get("/addresses/{bid}")
async def get_address(
    bid: UUID,
    get_db: DBConnDep,
):
    async with get_db() as conn:
        address = await AddressCRUD.get_by_id_with_customers(conn, bid)

    if address is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return AddressWithCustomersResponse.from_model(address)

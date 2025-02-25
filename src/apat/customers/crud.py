from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession

from apat.customers.models import (
    Address,
    AddressWithCustomers,
    Customer,
    CustomerWithAddress,
)
from apat.customers.tables import AddressTable, CustomersTable

# type SessionOrConnection = AsyncConnection | AsyncSession
AsyncConnection
AsyncSession
# type SessionOrConnection = AsyncSession
type SessionOrConnection = AsyncConnection


class AddressCRUD:
    @classmethod
    async def create(
        cls,
        session_or_connection: SessionOrConnection,
        street: str,
        city: str,
        state: str,
        zip_code: str,
    ) -> Address:
        query = (
            insert(AddressTable)
            .values(
                street=street,
                city=city,
                state=state,
                zip_code=zip_code,
            )
            .returning(AddressTable)
        )
        result = await session_or_connection.execute(query)
        row = result.first()
        return Address(
            bid=row.id,
            street=row.street,
            city=row.city,
            state=row.state,
            zip_code=row.zip_code,
        )

    @classmethod
    async def get_all(
        cls,
        session_or_connection: SessionOrConnection,
    ) -> list[Address]:
        query = select(AddressTable)
        result = await session_or_connection.execute(query)
        rows = result.all()
        return [
            Address(
                bid=row.id,
                street=row.street,
                city=row.city,
                state=row.state,
                zip_code=row.zip_code,
            )
            for row in rows
        ]

    @classmethod
    async def get_by_id(
        cls,
        session_or_connection: SessionOrConnection,
        bid: UUID,
    ) -> Address | None:
        query = select(AddressTable).where(AddressTable.id == bid)
        result = await session_or_connection.execute(query)
        row = await result.scalars().all()
        if row is None:
            return None
        return Address(
            bid=row.id,
            street=row.street,
            city=row.city,
            state=row.state,
            zip_code=row.zip_code,
        )

    @classmethod
    async def get_by_id_with_customers(
        cls,
        session_or_connection: SessionOrConnection,
        bid: UUID,
    ) -> AddressWithCustomers | None:
        query = (
            select(
                AddressTable,
                CustomersTable,
                CustomersTable.id.label("customer_id"),
            )
            .where(AddressTable.id == bid)
            .outerjoin(CustomersTable, AddressTable.id == CustomersTable.address_id)
        )
        result = await session_or_connection.execute(query)

        rows = result.all()

        if not rows:
            return None

        first_row = rows[0]

        return AddressWithCustomers(
            bid=first_row.id,
            street=first_row.street,
            city=first_row.city,
            state=first_row.state,
            zip_code=first_row.zip_code,
            customers=[
                Customer(
                    bid=row.customer_id,
                    first_name=row.first_name,
                    last_name=row.last_name,
                    address_bid=row.address_id,
                )
                for row in rows
            ],
        )


class CustomerCRUD:
    @classmethod
    async def create(
        cls,
        session_or_connection: SessionOrConnection,
        first_name: str,
        last_name: str,
        address_bid: UUID | None = None,
    ) -> Customer:
        query = (
            insert(CustomersTable)
            .values(
                first_name=first_name,
                last_name=last_name,
                address_id=address_bid,
            )
            .returning(CustomersTable)
        )
        result = await session_or_connection.execute(query)
        row = result.first()
        return Customer(
            bid=row.id,
            first_name=row.first_name,
            last_name=row.last_name,
            address_bid=row.address_id,
        )

    @classmethod
    async def get_all(
        cls,
        session_or_connection: SessionOrConnection,
    ) -> list[Customer]:
        query = select(CustomersTable)
        result = await session_or_connection.execute(query)

        rows = result.all()

        return [
            Customer(
                bid=row.id,
                first_name=row.first_name,
                last_name=row.last_name,
                address_bid=row.address_id,
            )
            for row in rows
        ]

    @classmethod
    async def get_by_id(
        cls,
        session_or_connection: SessionOrConnection,
        bid: UUID,
    ) -> Customer | None:
        query = select(CustomersTable).where(CustomersTable.id == bid)
        result = await session_or_connection.execute(query)
        row = result.scalars().first()
        if row is None:
            return None
        return Customer(
            bid=row.id,
            first_name=row.first_name,
            last_name=row.last_name,
            address_bid=row.address_id,
        )

    @classmethod
    async def get_by_id_with_customer(
        cls,
        session_or_connection: SessionOrConnection,
        bid: UUID,
    ) -> CustomerWithAddress | None:
        query = (
            select(
                CustomersTable,
                # AddressTable.id.label("addressid"),
                AddressTable,
                # AddressTable.street,
                # AddressTable.city,
                # AddressTable.state,
                # AddressTable.zip_code,
            )
            .where(CustomersTable.id == bid)
            .outerjoin(AddressTable, CustomersTable.address_id == AddressTable.id)
        )
        result = await session_or_connection.execute(query)
        row = result.first()
        print(row)
        if row is None:
            return None
        return CustomerWithAddress(
            bid=row.id,
            first_name=row.first_name,
            last_name=row.last_name,
            address=Address(
                bid=row.address_id,
                street=row.street,
                city=row.city,
                state=row.state,
                zip_code=row.zip_code,
            )
            if row.address_id is not None
            else None,
        )

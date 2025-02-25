from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from apat.database.tables import BaseTable


class AddressTable(BaseTable):
    __tablename__ = "addresses"

    street: Mapped[str]
    city: Mapped[str]
    state: Mapped[str]
    zip_code: Mapped[str]


class CustomersTable(BaseTable):
    __tablename__ = "customers"

    first_name: Mapped[str]
    last_name: Mapped[str]
    address_id: Mapped[UUID | None] = mapped_column(ForeignKey("addresses.id"))

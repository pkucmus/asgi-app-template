from dataclasses import dataclass, field
from uuid import UUID


@dataclass(frozen=True, kw_only=True)
class Address:
    bid: UUID
    street: str
    city: str
    state: str
    zip_code: str


@dataclass(frozen=True, kw_only=True)
class AddressWithCustomers(Address):
    customers: list["Customer"] = field(default_factory=list)


@dataclass(frozen=True, kw_only=True)
class Customer:
    bid: UUID
    first_name: str
    last_name: str
    address_bid: UUID | None = None


@dataclass(frozen=True, kw_only=True)
class CustomerWithAddress(Customer):
    address: Address | None = None

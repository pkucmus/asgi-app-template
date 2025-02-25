from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel

if TYPE_CHECKING:
    from apat.customers.models import (
        Address,
        AddressWithCustomers,
        Customer,
        CustomerWithAddress,
    )


class CustomerCreate(BaseModel):
    first_name: str
    last_name: str
    address_bid: UUID | None = None


class CustomerUpdate(BaseModel):
    first_name: str
    last_name: str
    address_bid: UUID


class CustomerResponse(BaseModel):
    bid: UUID
    first_name: str
    last_name: str
    address_bid: UUID | None = None

    @classmethod
    def from_model(cls, customer: "Customer"):
        return cls(
            bid=customer.bid,
            first_name=customer.first_name,
            last_name=customer.last_name,
            address_bid=customer.address_bid,
        )


class AddressCreate(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str


class AddressResponse(BaseModel):
    bid: UUID
    street: str
    city: str
    state: str
    zip_code: str

    @classmethod
    def from_model(cls, address: "Address"):
        return cls(
            bid=address.bid,
            street=address.street,
            city=address.city,
            state=address.state,
            zip_code=address.zip_code,
        )


class CustomerWithAddressResponse(CustomerResponse):
    address: AddressResponse | None = None

    @classmethod
    def from_model(cls, customer: "CustomerWithAddress"):
        return cls(
            bid=customer.bid,
            first_name=customer.first_name,
            last_name=customer.last_name,
            address_bid=customer.address_bid,
            address=AddressResponse.from_model(customer.address)
            if customer.address
            else None,
        )


class AddressWithCustomersResponse(AddressResponse):
    customers: list[CustomerResponse] = []

    @classmethod
    def from_model(cls, address: "AddressWithCustomers"):
        return cls(
            bid=address.bid,
            street=address.street,
            city=address.city,
            state=address.state,
            zip_code=address.zip_code,
            customers=[
                CustomerResponse.from_model(customer) for customer in address.customers
            ],
        )

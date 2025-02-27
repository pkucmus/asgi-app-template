from collections.abc import Callable, Coroutine
from typing import Any, Generic, TypeVar

from polyfactory.factories.dataclass_factory import DataclassFactory

T = TypeVar("T")
type DBFactory[T] = Callable[..., Coroutine[Any, Any, T]]


class CustomModelFactory(Generic[T], DataclassFactory[T]):
    __is_base_factory__ = True

    @classmethod
    def get_provider_map(
        cls,
    ) -> dict[type, Callable[[], Any]]:
        providers_map = super().get_provider_map()

        return {
            # UserBID: lambda: UserBID(uuid4()),
            **providers_map,
        }

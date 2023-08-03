from abc import ABC, ABCMeta, abstractmethod

from service.dal.schemas.db import OrderEntry


class _SingletonMeta(ABCMeta):
    _instances: dict = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(_SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DalHandler(ABC, metaclass=_SingletonMeta):

    @abstractmethod
    def create_order_in_db(self, customer_name: str, order_item_count: int) -> OrderEntry:
        ...  # pragma: no cover

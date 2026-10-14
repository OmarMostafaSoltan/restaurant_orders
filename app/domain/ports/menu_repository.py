from abc import ABC, abstractmethod

from app.domain.entities.menu import MenuItem


class MenuRepository(ABC):
    @abstractmethod
    def get_menu(self, restaurant_id: str) -> list[MenuItem]:
        ...

    @abstractmethod
    def get_item(self, restaurant_id: str, menu_item_id: str) -> MenuItem | None:
        ...
from abc import ABC, abstractmethod
from typing import Any

from marktplaats import Listing


class Notifier(ABC):
    @abstractmethod
    def __init__(self, config: dict[str, Any]): ...

    @abstractmethod
    def notify_started(self) -> None: ...

    @abstractmethod
    def notify_listing(self, listing: Listing, search_is: list[int]) -> None: ...

    @abstractmethod
    def notify_exception(self, context: str) -> None: ...

    @abstractmethod
    def notify_error(self, message: str) -> None: ...

    @abstractmethod
    def notify_warning(self, message: str) -> None: ...

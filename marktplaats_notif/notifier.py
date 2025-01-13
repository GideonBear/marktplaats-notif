from abc import ABC, abstractmethod

from marktplaats import Listing


class Notifier(ABC):
    @abstractmethod
    def __init__(self, config): ...

    @abstractmethod
    def notify_started(self) -> None: ...

    @abstractmethod
    def notify_listing(self, listing: Listing, search_is: list[int]) -> None: ...

    @abstractmethod
    def notify_error(self, error: Exception, context: str) -> None: ...

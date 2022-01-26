from typing import Protocol

from ...services.auth.interface import AuthenticationService
from ...services.datastore.interface import DatastoreService
from ...services.media.interface import MediaService
from ...services.message_bus.interface import MessageBusService
from ...services.thread_manager.thread_manager_service import ThreadManagerService
from ...services.vote.interface import VoteService


class Services(Protocol):  # pragma: no cover
    """
    Interface for service container used for dependency injection.
    """

    def authentication(self) -> AuthenticationService:
        pass

    def datastore(self) -> DatastoreService:
        pass

    def media(self) -> MediaService:
        pass

    def vote(self) -> VoteService:
        pass

    def message_bus(self) -> MessageBusService:
        pass

    def thread_manager(self) -> ThreadManagerService:
        pass

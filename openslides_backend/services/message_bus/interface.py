from typing import Any, Dict, Optional, Protocol


class MessageBusService(Protocol):
    """
    Message bus to implement messaging between multiple backend instances.
    """

    def wait_for_request(self) -> str:
        """
        Blocking method which executes an xread and waits for an incoming status request. Returns the thread id of the
        received request.
        """
        ...

    def request(self, thread_uuid: str) -> Optional[Dict[str, Any]]:
        """
        Request an update for the given thread from all backends.
        """
        ...

    def publish(self, thread_uuid: str, info: Dict[str, Any]) -> None:
        """
        Publish an update for the given thread to all backends.
        """
        ...

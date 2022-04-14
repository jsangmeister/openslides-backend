from concurrent.futures import Future, ThreadPoolExecutor
from enum import Enum
from multiprocessing import Process
from threading import Thread
from typing import Any, Callable, Dict, NoReturn, Optional, TypedDict
from uuid import uuid4

from ..message_bus.interface import MessageBusService


class ShutdownInfo(TypedDict):
    shutdown: bool


class ThreadProgressState(int, Enum):
    NOT_FOUND = 0
    RUNNING = 1
    FINISHED = 2


class ThreadManagerService:

    threads: Dict[str, Future]
    executor: ThreadPoolExecutor

    def __init__(self, message_bus: MessageBusService) -> None:
        self.message_bus = message_bus
        self.listener_thread: Optional[Process] = None
        self.shutdown_info: ShutdownInfo = {"shutdown": False}
        self.threads = {}
        self.executor = ThreadPoolExecutor()

    def print(self, msg: str) -> None:
        print(f"{hex(id(self))}: {msg}")

    def start_listener(self) -> None:
        self.listener_thread = Thread(
            target=self._start_listener, args=[self.shutdown_info], daemon=True
        )
        self.listener_thread.start()

    def _start_listener(self, shutdown_info: ShutdownInfo) -> NoReturn:
        self.print("started")
        while True:
            self.print(f"{self.threads} ({hex(id(self.threads))})")
            uuid = self.message_bus.wait_for_request()
            if shutdown_info.shutdown:
                self.print("stopping listener")
                return
            self.print(uuid)
            self.print(f"{self.threads} ({hex(id(self.threads))})")
            if data := self._get_thread_status(uuid):
                self.print(f"thread found! data: {data}")
                self.message_bus.publish(uuid, data)

    def get_thread_status(self, uuid: str) -> Dict[str, Any]:
        # check if result is in this worker
        self.print(f"Check status of {uuid}")
        data = self._get_thread_status(uuid)
        self.print(f"Local data: {data}")
        if data is None:
            # ask other workers via message bus
            data = self.message_bus.request(uuid)
        self.print(f"External data: {data}")
        if data is not None:
            return data
        else:
            return {"status": ThreadProgressState.NOT_FOUND}

    def _get_thread_status(self, uuid: str) -> Any:
        if thread := self.threads.get(uuid):
            if thread.done():
                data: Dict[str, Any] = {"status": ThreadProgressState.FINISHED}
                if exception := thread.exception():
                    data["exception"] = str(exception)
                else:
                    data["result"] = thread.result()
                # remove thread after publishing result
                del self.threads[uuid]
            else:
                data = {"status": ThreadProgressState.RUNNING}
            return data
        return None

    def start_threaded_function(self, threaded_function: Callable[[], Any]) -> str:
        uuid = uuid4().hex
        future = self.executor.submit(threaded_function)
        self.threads[uuid] = future
        # start listener as soon as we have data to answer for
        if not self.listener_thread:
            self.start_listener()
        return uuid

    def reset(self) -> None:
        self.threads.clear()
        self.shutdown_info["shutdown"] = True
        self.shutdown_info = {"shutdown": False}

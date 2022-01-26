import json
from time import time
from typing import Any, Dict, Optional

from redis import Redis

from ...shared.interfaces.logging import LoggingModule
from .interface import MessageBusService

THREAD_UPDATE_REQUEST_TOPIC = "backend_thread_update_requests"
THREAD_UPDATE_RESPONSE_TOPIC = "backend_thread_update_responses"
THREAD_UPDATE_TIMEOUT = 1000  # ms


class RedisAdapter(MessageBusService):
    def __init__(self, message_bus_url: str, logging: LoggingModule) -> None:
        self.logger = logging.getLogger(__name__)
        self.message_bus_url = message_bus_url
        self.redis = Redis.from_url(message_bus_url)
        self.last_request_id = "$"
        self.last_response_id: Optional[int] = None

    def wait_for_request(self) -> str:
        print("blocking request, last id: " + str(self.last_request_id))
        response = self.redis.xread(
            {THREAD_UPDATE_REQUEST_TOPIC: self.last_request_id}, count=1, block=0
        )
        update = response[0][1][0]
        self.last_request_id = update[0]
        uuid = next(iter(update[1])).decode()
        print(f"request for uuid {uuid}")
        return uuid

    def request(self, thread_uuid: str) -> Optional[Dict[str, Any]]:
        if self.last_response_id is None:
            length = self.redis.xlen(THREAD_UPDATE_RESPONSE_TOPIC)
            if length == 0:
                self.last_response_id = 0
            else:
                response = self.redis.xinfo_stream(THREAD_UPDATE_RESPONSE_TOPIC)
                self.last_response_id = response["last-generated-id"]
        self.redis.xadd(THREAD_UPDATE_REQUEST_TOPIC, {thread_uuid: ""})
        print(f"requesting update for {thread_uuid}")

        start = time()
        while (elapsed_ms := time() - start) < THREAD_UPDATE_TIMEOUT:
            remaining_ms = int(THREAD_UPDATE_TIMEOUT - elapsed_ms)
            response = self.redis.xread(
                {THREAD_UPDATE_RESPONSE_TOPIC: self.last_response_id},
                block=remaining_ms,
            )
            if not response:
                break

            updates = response[0][1]
            for id, fields in updates:
                self.last_response_id = id
                if value := fields.get(thread_uuid.encode()):
                    return json.loads(value)
        return None

    def publish(self, thread_uuid: str, info: Dict[str, Any]) -> None:
        self.redis.xadd(THREAD_UPDATE_RESPONSE_TOPIC, {thread_uuid: json.dumps(info)})

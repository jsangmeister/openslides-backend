from threading import Lock
from time import sleep
from typing import Any, Dict, Optional, Tuple, cast
from concurrent.futures import Future

from openslides_backend.action.action import Action
from openslides_backend.action.util.register import register_action
from openslides_backend.action.util.typing import ActionData, ActionResults
from openslides_backend.http.views.action_view import ActionView
from openslides_backend.services.thread_manager.thread_manager_service import (
    ThreadProgressState,
    ThreadManagerService,
)
from openslides_backend.services.message_bus.redis_adapter import RedisAdapter, THREAD_UPDATE_REQUEST_TOPIC, THREAD_UPDATE_RESPONSE_TOPIC
from openslides_backend.shared.interfaces.write_request import WriteRequest
from tests.system.base import ADMIN_PASSWORD, ADMIN_USERNAME, Response
from tests.system.util import create_action_test_application, get_route_path
from tests.util import Client

from .base import BasePresenterTestCase

ACTION_URL = get_route_path(ActionView.action_route)


action_start_lock = Lock()
action_end_lock = Lock()


@register_action("dummy.idle", threaded=True)
class DummyIdleAction(Action):
    def perform(
        self, action_data: ActionData, user_id: int, internal: bool = False
    ) -> Tuple[Optional[WriteRequest], Optional[ActionResults]]:
        print("action waiting")
        action_end_lock.acquire()
        with action_start_lock:
            print("lock acquired, returning")
            return (None, None)


def done_callback(future: Future) -> None:
    action_end_lock.release()
    print("end lock released")


class TestGetThreadStatus(BasePresenterTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.actions_app = create_action_test_application()
        self.app_thread_manager = self.actions_app.services.thread_manager()
        self.actions_client = Client(self.actions_app, ADMIN_USERNAME, ADMIN_PASSWORD)
        for lock in (action_start_lock, action_end_lock):
            if lock.locked():
                lock.release()

    def action_request(self, action: str, data: Dict[str, Any]) -> Response:
        payload = [
            {
                "action": action,
                "data": [data],
            }
        ]
        return self.actions_client.post(ACTION_URL, json=payload)

    def test_same_worker(self) -> None:
        # acquire the start lock: the dummy action will wait until this lock is free
        action_start_lock.acquire()
        # call dummy action and save the thread uuid
        response = self.action_request("dummy.idle", {})
        self.assert_status_code(response, 200)
        uuid = response.json["results"][0][0]["uuid"]
        # add callback to release the end lock after the action is done and the result is available
        future = self.app_thread_manager.threads[uuid]
        future.add_done_callback(done_callback)
        # currently, the action thread is still waiting for the start lock and the end lock is already locked by the
        # action, so the current status should be RUNNING
        status_code, data = self.request("get_thread_status", {"uuid": uuid})
        self.assertEqual(status_code, 200)
        self.assertEqual(data, {"status": ThreadProgressState.RUNNING})
        # release the start lock so the action can finish its "work"
        action_start_lock.release()
        # wait until done callback has been called (=> the result is available)
        action_end_lock.acquire()
        # the action is done and the result is now available, so fetch it
        status_code, data = self.request("get_thread_status", {"uuid": uuid})
        self.assertEqual(status_code, 200)
        self.assertEqual(data, {"status": ThreadProgressState.FINISHED, "result": None})
        # assert that nothing was written to redis
        self.assertEqual(self.message_bus.redis.xlen(THREAD_UPDATE_REQUEST_TOPIC), 0)
        self.assertEqual(self.message_bus.redis.xlen(THREAD_UPDATE_RESPONSE_TOPIC), 0)

    def test_emulate_other_worker(self) -> None:
        """
        Emulate another worker (which is hard to do for real in tests) by creating a second ThreadManagerService and
        manipulating the class variables.
        """
        # acquire the start lock: the dummy action will wait until this lock is free
        action_start_lock.acquire()
        print("call to action")
        # call dummy action and save the thread uuid
        response = self.action_request("dummy.idle", {})
        self.assert_status_code(response, 200)
        uuid = response.json["results"][0][0]["uuid"]
        # add callback to release the end lock after the action is done and the result is available
        future = self.app_thread_manager.threads[uuid]
        future.add_done_callback(done_callback)
        # currently, the action thread is sitll waiting for the start lock and the end lock is already locked by the
        # action, so the current status should be RUNNING
        status_code, data = self.request("get_thread_status", {"uuid": uuid})
        self.assertEqual(status_code, 200)
        self.assertEqual(data, {"status": ThreadProgressState.RUNNING})
        print("first check done")

        # create a second "dummy" thread manager to test the message bus communication
        dummy_thread_manager = ThreadManagerService(self.services.message_bus())
        dummy_thread_manager.threads = self.app_thread_manager.threads.copy()
        self.app_thread_manager.reset()
        dummy_thread_manager.start_listener()

        # release the start lock so the action can finish its "work"
        action_start_lock.release()
        # wait until done callback has been called (=> the result is available)
        action_end_lock.acquire()
        # the action is done and the result is now available, so fetch it
        status_code, data = self.request("get_thread_status", {"uuid": uuid})
        self.assertEqual(status_code, 200)
        self.assertEqual(data, {"status": ThreadProgressState.FINISHED, "result": None})

        # assert redis was used
        self.assertEqual(self.message_bus.redis.xlen(THREAD_UPDATE_REQUEST_TOPIC), 1)
        self.assertEqual(self.message_bus.redis.xlen(THREAD_UPDATE_RESPONSE_TOPIC), 1)

        # clean up dummy thread manager
        dummy_thread_manager.reset()

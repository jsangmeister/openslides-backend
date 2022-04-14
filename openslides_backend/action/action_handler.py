from copy import deepcopy
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    cast,
)

import fastjsonschema

from ..services.datastore.interface import DatastoreService
from ..shared.exceptions import (
    ActionException,
    DatastoreLockedException,
    View400Exception,
)
from ..shared.handlers.base_handler import BaseHandler
from ..shared.interfaces.env import Env
from ..shared.interfaces.logging import LoggingModule
from ..shared.interfaces.services import Services
from ..shared.interfaces.write_request import WriteRequest
from ..shared.schema import schema_version
from . import actions  # noqa
from .action import Action
from .relations.relation_manager import RelationManager
from .util.action_type import ActionType
from .util.actions_map import actions_map
from .util.typing import (
    ActionData,
    ActionError,
    ActionResults,
    ActionsResponse,
    ActionsResponseResults,
    OnSuccessCallable,
    Payload,
    PayloadElement,
)

T = TypeVar("T")

action_data_schema = {
    "$schema": schema_version,
    "title": "Action data",
    "type": "array",
    "items": {"type": "object"},
}

payload_schema = fastjsonschema.compile(
    {
        "$schema": schema_version,
        "title": "Schema for action API",
        "description": "An array of actions",
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "action": {
                    "description": "Name of the action to be performed on the server",
                    "type": "string",
                    "minLength": 1,
                },
                "data": action_data_schema,
            },
            "required": ["action", "data"],
            "additionalProperties": False,
        },
    }
)

MAX_RETRY = 3


class ActionHandler(BaseHandler):
    """
    Action handler. It is the concrete implementation of Action interface.
    """

    on_success: List[OnSuccessCallable]

    def __init__(self, env: Env, services: Services, logging: LoggingModule) -> None:
        super().__init__(env, services, logging)
        self.on_success = []

    @classmethod
    def get_health_info(cls) -> Iterable[Tuple[str, Dict[str, Any]]]:
        """
        Returns name and development status of all actions.
        """
        for name in sorted(actions_map):
            action = actions_map[name]
            schema: Dict[str, Any] = deepcopy(action_data_schema)
            schema["items"] = action.schema
            if action.is_singular:
                schema["maxItems"] = 1
            info = dict(
                schema=schema,
            )
            yield name, info

    def handle_request(
        self,
        payload: Payload,
        user_id: int,
        atomic: bool = True,
        internal: bool = False,
    ) -> ActionsResponse:
        """
        Takes payload and user id and handles this request by validating and
        parsing all actions. In the end it sends everything to the event store.
        """
        self.user_id = user_id
        self.internal = internal

        try:
            payload_schema(payload)
        except fastjsonschema.JsonSchemaException as exception:
            raise ActionException(exception.message)

        # check if only a single action is called
        if len(payload) == 1:
            ActionClass = self.get_action_class(payload[0]["action"])
            # if threaded, start separately in a thread
            if ActionClass.threaded:
                action = self.get_action_instance(
                    ActionClass, None, self.datastore.clone()
                )
                action_data = deepcopy(payload[0]["data"])

                def threaded_function() -> Optional[ActionResults]:
                    write_request, results, on_success = self.try_perform_action(
                        action, action_data
                    )
                    if write_request:
                        action.datastore.write(write_request)
                    if on_success:
                        on_success()
                    return results

                uuid = self.services.thread_manager().start_threaded_function(
                    threaded_function
                )
                self.logger.debug(f"Thread started: {uuid}")
                return ActionsResponse(
                    success=True,
                    message="Thread started successfully",
                    results=[[{"uuid": uuid}]],
                )

        results: ActionsResponseResults = []
        if atomic:
            results = self.execute_write_requests(self.parse_actions, payload)
        else:

            def transform_to_list(
                tuple: Tuple[Optional[WriteRequest], Optional[ActionResults]]
            ) -> Tuple[List[WriteRequest], Optional[ActionResults]]:
                return ([tuple[0]] if tuple[0] is not None else [], tuple[1])

            for element in payload:
                try:
                    result = self.execute_write_requests(
                        lambda e: transform_to_list(self.perform_action(e)), element
                    )
                    results.append(result)
                except ActionException as exception:
                    error = cast(ActionError, exception.get_json())
                    results.append(error)
                self.datastore.reset()

        # execute cleanup methods
        for on_success in self.on_success:
            on_success()

        # Return action result
        self.logger.debug("Request was successful. Send response now.")
        return ActionsResponse(
            success=True, message="Actions handled successfully", results=results
        )

    def execute_write_requests(
        self,
        get_write_requests: Callable[..., Tuple[List[WriteRequest], T]],
        *args: Any,
        max_retries: int = MAX_RETRY,
    ) -> T:
        retries = 0
        while True:
            try:
                write_requests, data = get_write_requests(*args)
                if write_requests:
                    self.datastore.write(write_requests)
                return data
            except DatastoreLockedException as exception:
                retries += 1
                if retries >= max_retries:
                    raise ActionException(exception.message)
                else:
                    self.datastore.reset()

    def parse_actions(
        self, payload: Payload
    ) -> Tuple[List[WriteRequest], ActionsResponseResults]:
        """
        Parses actions request send by client. Raises ActionException or
        PermissionDenied if something went wrong.
        """
        write_requests: List[WriteRequest] = []
        action_response_results: ActionsResponseResults = []
        relation_manager = RelationManager(self.datastore)
        action_name_list = []
        for i, element in enumerate(payload):
            action_name = element["action"]
            if (
                actions_map.get(action_name)
                and actions_map.get(action_name).is_singular  # type: ignore
            ):
                if action_name in action_name_list:
                    exception = ActionException(
                        f"Action {action_name} may not appear twice in one request."
                    )
                    exception.action_error_index = i
                    raise exception
                else:
                    action_name_list.append(action_name)
            try:
                write_request, results = self.perform_action(element, relation_manager)
            except ActionException as exception:
                exception.action_error_index = i
                raise exception

            if write_request:
                write_requests.append(write_request)
            action_response_results.append(results)

        self.logger.debug("Write request is ready.")
        return (
            write_requests,
            action_response_results,
        )

    def perform_action(
        self,
        action_payload_element: PayloadElement,
        relation_manager: Optional[RelationManager] = None,
    ) -> Tuple[Optional[WriteRequest], Optional[ActionResults]]:
        ActionClass = self.get_action_class(action_payload_element["action"])
        action = self.get_action_instance(ActionClass, relation_manager)
        action_data = deepcopy(action_payload_element["data"])

        self.logger.debug(f"Perform action {ActionClass.name}.")
        write_request, results, on_success = self.try_perform_action(
            action, action_data
        )
        if on_success:
            self.on_success.append(on_success)
        return (write_request, results)

    def try_perform_action(
        self, action: Action, action_data: ActionData
    ) -> Tuple[
        Optional[WriteRequest], Optional[ActionResults], Optional[OnSuccessCallable]
    ]:
        try:
            write_request, results = action.perform(
                action_data, self.user_id, internal=self.internal
            )
            if write_request:
                action.validate_required_fields(write_request)

                # add locked_fields to request
                write_request.locked_fields = action.datastore.locked_fields
                # reset locked fields, but not addtional relation models - these might be needed
                # by another action
                action.datastore.locked_fields = {}

            # get on_success routine
            on_success = action.get_on_success(action_data)

            return (write_request, results, on_success)
        except ActionException as exception:
            self.logger.debug(
                f"Error occured on index {action.index}: {exception.message}"
            )
            # -1: error which cannot be directly associated with a single action data
            if action.index > -1:
                exception.action_data_error_index = action.index
            raise exception

    def get_action_class(
        self,
        action_name: str,
    ) -> Type[Action]:
        ActionClass = actions_map.get(action_name)
        if ActionClass is None or (
            ActionClass.action_type == ActionType.BACKEND_INTERNAL
            and not self.env.is_dev_mode()
        ):
            raise View400Exception(f"Action {action_name} does not exist.")
        return ActionClass

    def get_action_instance(
        self,
        ActionClass: Type[Action],
        relation_manager: Optional[RelationManager] = None,
        datastore: Optional[DatastoreService] = None,
    ) -> Action:
        if not relation_manager:
            if not datastore:
                datastore = self.datastore
            relation_manager = RelationManager(datastore)
        action = ActionClass(
            self.services, self.datastore, relation_manager, self.logging
        )
        return action

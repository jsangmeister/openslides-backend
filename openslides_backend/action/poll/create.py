from typing import Any, Dict, Type

from ...models.models import MotionWorkflow
from ..action import register_action
from ..base import Action, DataSet
from ..action_interface import ActionPayload
from ..generics import CreateAction
from ..default_schema import DefaultSchema
from ..motion_state.create_update_delete import MotionStateActionSet


BASE_POLL_CREATE_REQUIRED_PROPERTIES = ["title"]
BASE_POLL_CREATE_PROPERTIES = BASE_POLL_CREATE_REQUIRED_PROPERTIES + ["pollmethod", "type", "onehundred_percent_base", "majority_method", "entitled_group_ids", "votes", "publish_immediately"]


class BasePollCreateAction(CreateAction):
    """
    Base action to create a poll.
    """
    def prepare_dataset(self, payload: ActionPayload) -> DataSet:
        pass

    def create_options(self, poll_id: int) -> DataSet:
        raise NotImplementedError()

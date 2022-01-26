from typing import Any

import fastjsonschema

from ..shared.schema import schema_version
from .base import BasePresenter
from .presenter import register_presenter

get_thread_status_schema = fastjsonschema.compile(
    {
        "$schema": schema_version,
        "type": "object",
        "title": "get_thread_status data",
        "description": "Schema to validate the get_thread_status presenter data.",
        "properties": {"uuid": {"type": "string", "minLength": 1}},
        "required": ["uuid"],
        "additionalProperties": False,
    }
)


@register_presenter("get_thread_status")
class GetThreadStatus(BasePresenter):

    schema = get_thread_status_schema

    def get_result(self) -> Any:
        thread_manager = self.services.thread_manager()
        result = thread_manager.get_thread_status(self.data["uuid"])
        return result

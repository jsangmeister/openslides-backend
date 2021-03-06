from tests.system.action.base import BaseActionTestCase


class ProjectorMessageUpdate(BaseActionTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.set_models(
            {
                "meeting/1": {"projector_message_ids": [2]},
                "projector_message/2": {"meeting_id": 1, "message": "test1"},
            }
        )

    def test_update(self) -> None:
        response = self.request(
            "projector_message.update",
            {"id": 2, "message": "geredegerede"},
        )
        self.assert_status_code(response, 200)
        projector_message = self.get_model("projector_message/2")
        assert projector_message.get("message") == "geredegerede"

    def test_update_wrong_id(self) -> None:
        response = self.request(
            "projector_message.update",
            {"id": 3, "message": "geredegerede"},
        )
        self.assert_status_code(response, 400)
        projector_message = self.get_model("projector_message/2")
        assert projector_message.get("message") == "test1"

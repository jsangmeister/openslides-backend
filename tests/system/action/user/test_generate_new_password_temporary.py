from tests.system.action.base import BaseActionTestCase


class UserGenerateNewPasswordTemporaryActionTest(BaseActionTestCase):
    def test_update_correct(self) -> None:
        self.set_models(
            {
                "meeting/2": {"name": "name_meeting_2"},
                "user/1": {"password": "old_pw", "meeting_id": 2},
            }
        )
        response = self.request("user.generate_new_password_temporary", {"id": 1})
        self.assert_status_code(response, 200)
        model = self.get_model("user/1")
        assert model.get("password") is not None
        assert self.auth.is_equals(
            model.get("default_password", ""), model.get("password", "")
        )

    def test_update_not_temporary(self) -> None:
        self.update_model("user/1", {"password": "old_pw"})
        response = self.request("user.generate_new_password_temporary", {"id": 1})
        self.assert_status_code(response, 400)
        assert "User 1 is not temporary" in response.json["message"]

from tests.system.action.base import BaseActionTestCase


class UserUpdateTemporaryActionTest(BaseActionTestCase):
    def test_update_correct(self) -> None:
        self.create_model(
            "user/111",
            {"username": "username_srtgb123", "meeting_id": 222},
        )
        response = self.request(
            "user.update_temporary", {"id": 111, "username": "username_Xcdfgee"}
        )
        self.assert_status_code(response, 200)
        model = self.get_model("user/111")
        assert model.get("username") == "username_Xcdfgee"

    def test_update_all_fields(self) -> None:
        self.set_models(
            {
                "meeting/222": {"name": "name_meeting222"},
                "user/111": {"username": "username_srtgb123", "meeting_id": 222},
                "group/7": {"name": "name_group7", "user_ids": [], "meeting_id": 222},
                "user/7": {},
            }
        )
        response = self.request(
            "user.update_temporary",
            {
                "id": 111,
                "username": "test_Xcdfgee",
                "title": "title",
                "first_name": "first_name",
                "last_name": "last_name",
                "is_active": True,
                "is_physical_person": False,
                "gender": "gender",
                "email": "email",
                "is_present_in_meeting_ids": [222],
                "default_password": "password",
                "group_ids": [7],
                "vote_delegations_from_ids": [7],
                "comment": "comment<iframe></iframe>",
                "number": "number",
                "structure_level": "level",
                "about_me": "<p>about</p><iframe></iframe>",
                "vote_weight": "1.000000",
            },
        )
        self.assert_status_code(response, 200)
        model = self.get_model("user/111")
        assert model.get("username") == "test_Xcdfgee"
        assert model.get("meeting_id") == 222
        assert model.get("title") == "title"
        assert model.get("first_name") == "first_name"
        assert model.get("last_name") == "last_name"
        assert model.get("is_active") is True
        assert model.get("is_physical_person") is False
        assert model.get("gender") == "gender"
        assert model.get("email") == "email"
        assert model.get("is_present_in_meeting_ids") == [222]
        assert model.get("default_password") == "password"
        assert model.get("group_$222_ids") == [7]
        assert model.get("group_$_ids") == ["222"]
        assert model.get("group_ids") is None
        assert model.get("vote_delegations_$222_from_ids") == [7]
        assert model.get("vote_delegations_$_from_ids") == ["222"]
        assert model.get("vote_delegations_from_ids") is None
        assert model.get("comment_$222") == "comment&lt;iframe&gt;&lt;/iframe&gt;"
        assert model.get("comment_$") == ["222"]
        assert model.get("number_$222") == "number"
        assert model.get("number_$") == ["222"]
        assert model.get("structure_level_$222") == "level"
        assert model.get("structure_level_$") == ["222"]
        assert model.get("about_me_$222") == "<p>about</p>&lt;iframe&gt;&lt;/iframe&gt;"
        assert model.get("about_me_$") == ["222"]
        assert model.get("vote_weight_$222") == "1.000000"
        assert model.get("vote_weight_$") == ["222"]
        # check meeting.user_ids
        meeting = self.get_model("meeting/222")
        assert meeting.get("user_ids") == [111]

    def test_update_vote_weight(self) -> None:
        self.set_models(
            {
                "user/111": {"username": "username_srtgb123", "meeting_id": 222},
                "meeting/222": {},
            }
        )
        response = self.request(
            "user.update_temporary", {"id": 111, "vote_weight": "1.500000"}
        )
        self.assert_status_code(response, 200)
        model = self.get_model("user/111")
        assert model.get("vote_weight_$222") == "1.500000"

    def test_update_vote_weight_two_digits(self) -> None:
        self.set_models(
            {
                "user/111": {"username": "username_srtgb123", "meeting_id": 222},
                "meeting/222": {},
            }
        )
        response = self.request(
            "user.update_temporary", {"id": 111, "vote_weight": "10.500000"}
        )
        self.assert_status_code(response, 200)
        model = self.get_model("user/111")
        assert model.get("vote_weight_$222") == "10.500000"

    def test_update_vote_weight_invalid_number(self) -> None:
        self.set_models(
            {
                "user/111": {"username": "username_srtgb123", "meeting_id": 222},
                "meeting/222": {},
            }
        )
        response = self.request(
            "user.update_temporary", {"id": 111, "vote_weight": 1.5}
        )
        self.assert_status_code(response, 400)
        model = self.get_model("user/111")
        assert model.get("vote_weight_$222") is None

    def test_update_vote_weight_invalid_string(self) -> None:
        self.set_models(
            {
                "user/111": {"username": "username_srtgb123", "meeting_id": 222},
                "meeting/222": {},
            }
        )
        response = self.request(
            "user.update_temporary", {"id": 111, "vote_weight": "a.aaaaaa"}
        )
        self.assert_status_code(response, 400)
        model = self.get_model("user/111")
        assert model.get("vote_weight_$222") is None

    def test_update_wrong_id(self) -> None:
        self.create_model(
            "user/111",
            {"username": "username_srtgb123", "meeting_id": 222},
        )
        response = self.request(
            "user.update_temporary", {"id": 112, "username": "username_Xcdfgee"}
        )
        self.assert_status_code(response, 400)
        model = self.get_model("user/111")
        assert model.get("username") == "username_srtgb123"

    def test_update_invalid_present_meeting(self) -> None:
        self.set_models(
            {
                "meeting/1": {},
                "meeting/2": {},
                "user/111": {"username": "username_srtgb123", "meeting_id": 1},
            }
        )
        response = self.request(
            "user.update_temporary", {"id": 111, "is_present_in_meeting_ids": [2]}
        )
        self.assert_status_code(response, 400)
        self.assertIn(
            "A temporary user can only be present in its respective meeting.",
            response.json["message"],
        )
        self.assert_model_exists("user/111", {"is_present_in_meeting_ids": None})

    def test_update_invalid_group(self) -> None:
        self.set_models(
            {
                "meeting/1": {},
                "group/2": {"meeting_id": 2},
                "user/111": {"username": "username_srtgb123", "meeting_id": 1},
            }
        )
        response = self.request("user.update_temporary", {"id": 111, "group_ids": [2]})
        self.assert_status_code(response, 400)
        self.assertIn(
            "requires the following fields to be equal",
            response.json["message"],
        )
        model = self.get_model("user/111")
        assert model.get("group_$222_ids") is None
        assert model.get("group_$_ids") is None
        assert model.get("group_ids") is None

    def test_update_invalid_vote_delegation(self) -> None:
        self.set_models({"meeting/222": {}, "user/111": {"meeting_id": 222}})
        response = self.request(
            "user.update_temporary",
            {
                "id": 111,
                "vote_delegations_from_ids": [7],
            },
        )
        self.assert_status_code(response, 400)
        self.assertIn(
            "The following users were not found",
            response.json["message"],
        )
        model = self.get_model("user/111")
        assert model.get("vote_delegations_$222_from_ids") is None
        assert model.get("vote_delegations_$_from_ids") is None
        assert model.get("vote_delegations_from_ids") is None

from tests.system.action.base import BaseActionTestCase


class MotionCategorySystemTest(BaseActionTestCase):
    def test_update_correct_all_fields(self) -> None:
        self.set_models(
            {
                "meeting/222": {"name": "name_xQyvfmsS"},
                "motion/89": {"meeting_id": 222},
                "motion_category/111": {
                    "name": "name_srtgb123",
                    "prefix": "prefix_JmDHFgvH",
                    "meeting_id": 222,
                },
            }
        )
        response = self.request(
            "motion_category.update",
            {
                "id": 111,
                "name": "name_Xcdfgee",
                "prefix": "prefix_sthyAKrW",
                "motion_ids": [89],
            },
        )
        self.assert_status_code(response, 200)

        self.assert_model_exists("motion_category/111")
        model = self.get_model("motion_category/111")
        assert model.get("name") == "name_Xcdfgee"
        assert model.get("prefix") == "prefix_sthyAKrW"
        assert model.get("motion_ids") == [89]

    def test_update_delete_prefix(self) -> None:
        self.set_models(
            {
                "meeting/222": {},
                "motion_category/111": {
                    "name": "name_srtgb123",
                    "prefix": "prefix_JmDHFgvH",
                    "meeting_id": 222,
                },
            }
        )
        response = self.request(
            "motion_category.update",
            {
                "id": 111,
                "prefix": None,
            },
        )
        self.assert_status_code(response, 200)
        model = self.get_model("motion_category/111")
        assert "prefix" not in model

    def test_update_wrong_id(self) -> None:
        self.set_models(
            {
                "meeting/222": {"name": "name_xQyvfmsS"},
                "motion_category/111": {
                    "name": "name_srtgb123",
                    "prefix": "prefix_JmDHFgvH",
                    "meeting_id": 222,
                },
            }
        )
        response = self.request(
            "motion_category.update", {"id": 112, "name": "name_Xcdfgee"}
        )
        self.assert_status_code(response, 400)
        model = self.get_model("motion_category/111")
        assert model.get("name") == "name_srtgb123"

from openslides_backend.models.models import Poll
from tests.system.action.base import BaseActionTestCase


class VotePollBaseTestClass(BaseActionTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.create_model(
            "assignment/1",
            {
                "title": "test_assignment_tcLT59bmXrXif424Qw7K",
                "open_posts": 1,
            },
        )
        self.create_poll()
        self.create_model("meeting/113", {"name": "my meeting"})
        self.create_model("group/1", {"user_ids": [1]})
        self.create_model("option/1", {"meeting_id": 113, "poll_id": 1})
        self.create_model("option/2", {"meeting_id": 113, "poll_id": 1})
        self.update_model(
            "user/1",
            {
                "is_present_in_meeting_ids": [113],
                "group_$113_ids": [1],
                "group_$_ids": ["113"],
            },
        )

    def create_poll(self) -> None:
        # has to be implemented by subclasses
        raise NotImplementedError()


class VotePollAnalogYNA(VotePollBaseTestClass):
    def create_poll(self) -> None:
        self.create_model(
            "poll/1",
            {
                "content_object_id": "assignment/1",
                "title": "test_title_04k0y4TwPLpJKaSvIGm1",
                "pollmethod": "YNA",
                "type": Poll.TYPE_ANALOG,
                "state": Poll.STATE_CREATED,
                "meeting_id": 113,
                "option_ids": [1, 2],
                "entitled_group_ids": [1],
                "votesinvalid": "0.000000",
                "votesvalid": "0.000000",
                "votescast": "0.000000",
            },
        )

    def test_start_poll(self) -> None:
        response = self.request("poll.start", {"id": 1})
        self.assert_status_code(response, 200)
        poll = self.get_model("poll/1")
        self.assertEqual(poll.get("state"), Poll.STATE_STARTED)
        self.assertEqual(poll.get("votesvalid"), "0.000000")
        self.assertEqual(poll.get("votesinvalid"), "0.000000")
        self.assertEqual(poll.get("votescast"), "0.000000")
        self.assert_model_not_exists("vote/1")

    def test_start_wrong_state(self) -> None:
        self.update_model("poll/1", {"state": "published"})
        response = self.request("poll.start", {"id": 1})
        self.assert_status_code(response, 400)
        poll = self.get_model("poll/1")
        assert poll.get("state") == "published"
        assert (
            "Cannot start poll 1, because it is not in state created."
            in response.data.decode()
        )


class VotePollNamedYNA(VotePollBaseTestClass):
    def create_poll(self) -> None:
        self.create_model(
            "poll/1",
            {
                "content_object_id": "assignment/1",
                "title": "test_title_OkHAIvOSIcpFnCxbaL6v",
                "pollmethod": "YNA",
                "type": Poll.TYPE_NAMED,
                "state": Poll.STATE_CREATED,
                "meeting_id": 113,
                "option_ids": [1, 2],
                "entitled_group_ids": [1],
                "votesinvalid": "0.000000",
                "votesvalid": "0.000000",
                "votescast": "0.000000",
            },
        )

    def test_start_poll(self) -> None:
        response = self.request("poll.start", {"id": 1})
        self.assert_status_code(response, 200)
        poll = self.get_model("poll/1")
        self.assertEqual(poll.get("state"), Poll.STATE_STARTED)
        self.assertEqual(poll.get("votesvalid"), "0.000000")
        self.assertEqual(poll.get("votesinvalid"), "0.000000")
        self.assertEqual(poll.get("votescast"), "0.000000")
        self.assert_model_not_exists("vote/1")


class VotePollNamedY(VotePollBaseTestClass):
    def create_poll(self) -> None:
        self.create_model(
            "poll/1",
            {
                "content_object_id": "assignment/1",
                "title": "test_title_Zrvh146QAdq7t6iSDwZk",
                "pollmethod": "Y",
                "type": Poll.TYPE_NAMED,
                "state": Poll.STATE_CREATED,
                "meeting_id": 113,
                "option_ids": [1, 2],
                "entitled_group_ids": [1],
                "votesinvalid": "0.000000",
                "votesvalid": "0.000000",
                "votescast": "0.000000",
            },
        )

    def test_start_poll(self) -> None:
        response = self.request("poll.start", {"id": 1})
        self.assert_status_code(response, 200)
        poll = self.get_model("poll/1")
        self.assertEqual(poll.get("state"), Poll.STATE_STARTED)
        self.assertEqual(poll.get("votesvalid"), "0.000000")
        self.assertEqual(poll.get("votesinvalid"), "0.000000")
        self.assertEqual(poll.get("votescast"), "0.000000")
        self.assert_model_not_exists("vote/1")


class VotePollNamedN(VotePollBaseTestClass):
    def create_poll(self) -> None:
        self.create_model(
            "poll/1",
            {
                "content_object_id": "assignment/1",
                "title": "test_title_4oi49ckKFk39SDIfj30s",
                "pollmethod": "N",
                "type": Poll.TYPE_NAMED,
                "state": Poll.STATE_CREATED,
                "meeting_id": 113,
                "option_ids": [1, 2],
                "entitled_group_ids": [1],
                "votesinvalid": "0.000000",
                "votesvalid": "0.000000",
                "votescast": "0.000000",
            },
        )

    def test_start_poll(self) -> None:
        response = self.request("poll.start", {"id": 1})
        self.assert_status_code(response, 200)
        poll = self.get_model("poll/1")
        self.assertEqual(poll.get("state"), Poll.STATE_STARTED)
        self.assertEqual(poll.get("votesvalid"), "0.000000")
        self.assertEqual(poll.get("votesinvalid"), "0.000000")
        self.assertEqual(poll.get("votescast"), "0.000000")
        self.assert_model_not_exists("vote/1")


class VotePollPseudoanonymousYNA(VotePollBaseTestClass):
    def create_poll(self) -> None:
        self.create_model(
            "poll/1",
            {
                "content_object_id": "assignment/1",
                "title": "test_title_OkHAIvOSIcpFnCxbaL6v",
                "pollmethod": "YNA",
                "type": Poll.TYPE_PSEUDOANONYMOUS,
                "state": Poll.STATE_CREATED,
                "meeting_id": 113,
                "option_ids": [1, 2],
                "entitled_group_ids": [1],
                "votesinvalid": "0.000000",
                "votesvalid": "0.000000",
                "votescast": "0.000000",
            },
        )

    def test_start_poll(self) -> None:
        response = self.request("poll.start", {"id": 1})
        self.assert_status_code(response, 200)
        poll = self.get_model("poll/1")
        self.assertEqual(poll.get("state"), Poll.STATE_STARTED)
        self.assertEqual(poll.get("votesvalid"), "0.000000")
        self.assertEqual(poll.get("votesinvalid"), "0.000000")
        self.assertEqual(poll.get("votescast"), "0.000000")
        self.assert_model_not_exists("vote/1")


class VotePollPseudoanonymousY(VotePollBaseTestClass):
    def create_poll(self) -> None:
        self.create_model(
            "poll/1",
            {
                "content_object_id": "assignment/1",
                "title": "test_title_Zrvh146QAdq7t6iSDwZk",
                "pollmethod": "Y",
                "type": Poll.TYPE_PSEUDOANONYMOUS,
                "state": Poll.STATE_CREATED,
                "meeting_id": 113,
                "option_ids": [1, 2],
                "entitled_group_ids": [1],
                "votesinvalid": "0.000000",
                "votesvalid": "0.000000",
                "votescast": "0.000000",
            },
        )

    def test_start_poll(self) -> None:
        response = self.request("poll.start", {"id": 1})
        self.assert_status_code(response, 200)
        poll = self.get_model("poll/1")
        self.assertEqual(poll.get("state"), Poll.STATE_STARTED)
        self.assertEqual(poll.get("votesvalid"), "0.000000")
        self.assertEqual(poll.get("votesinvalid"), "0.000000")
        self.assertEqual(poll.get("votescast"), "0.000000")
        self.assert_model_not_exists("vote/1")


class VotePollPseudoAnonymousN(VotePollBaseTestClass):
    def create_poll(self) -> None:
        self.create_model(
            "poll/1",
            {
                "content_object_id": "assignment/1",
                "title": "test_title_wWPOVJgL9afm83eamf3e",
                "pollmethod": "N",
                "type": Poll.TYPE_PSEUDOANONYMOUS,
                "state": Poll.STATE_CREATED,
                "meeting_id": 113,
                "option_ids": [1, 2],
                "entitled_group_ids": [1],
                "votesinvalid": "0.000000",
                "votesvalid": "0.000000",
                "votescast": "0.000000",
            },
        )

    def test_start_poll(self) -> None:
        response = self.request("poll.start", {"id": 1})
        self.assert_status_code(response, 200)
        poll = self.get_model("poll/1")
        self.assertEqual(poll.get("state"), Poll.STATE_STARTED)
        self.assertEqual(poll.get("votesvalid"), "0.000000")
        self.assertEqual(poll.get("votesinvalid"), "0.000000")
        self.assertEqual(poll.get("votescast"), "0.000000")
        self.assert_model_not_exists("vote/1")

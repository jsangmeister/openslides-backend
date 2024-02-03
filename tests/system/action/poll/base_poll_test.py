import os
from tests.system.action.base import BaseActionTestCase


class BasePollTestCase(BaseActionTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.vote_service.clear_all()
        self.remove_files_from_vote_decrypt_service()

    def remove_files_from_vote_decrypt_service(self) -> None:
        path = "tests/system/action/poll/vote_decrypt_clear_data"
        if os.path.exists(path):
            files = os.listdir(path)
            for file in files:
                os.remove(os.path.join(path, file))


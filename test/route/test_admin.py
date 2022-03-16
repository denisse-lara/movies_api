from flask import json

from api.route.admin import url_prefix
from test.base_test import BaseTest
from api.model.user_profile import UserProfile


class TestAdmin(BaseTest):
    def setUp(self) -> None:
        super().setUp()

    def test_get_all_users_returns_user_list(self):
        self.create_user("user1", "1234", "User 1", False)
        self.create_user("user2", "1234", "User 2", False)
        self.create_user("user3", "1234", "User 3", False)

        res = self.client.get(url_prefix+"/users")
        self.assertEqual(200, res.status_code, url_prefix+"/users endpoint should exist")

        users = json.loads(json.dumps(res.json))
        self.assertEqual(len(users), 3, "")

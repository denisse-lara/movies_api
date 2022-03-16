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

        res = self.client.get(url_prefix + "/users")
        self.assertEqual(
            200, res.status_code, url_prefix + "/users endpoint should exist"
        )

        users = json.loads(json.dumps(res.json))
        self.assertEqual(len(users), 3, "")

    def test_promote_existing_user_to_admin_returns_ok(self):
        self.create_user("not_admin", "1234", "Not Admin", False)
        res = self.client.put(url_prefix + "/users/%s/promote" % self.user_public_id)
        self.assertEqual(
            200, res.status_code, url_prefix + "/users/<public_id>/promote should exist"
        )

        admin_value = res.json["user"]["admin"]
        self.assertEqual(True, admin_value, "User should be promoted to admin")

    def test_promote_non_existing_user_to_admin_returns_not_found(self):
        res = self.client.put(url_prefix + "/users/%s/promote" % "not_good_id")
        self.assertEqual(
            404, res.status_code, "Trying to promote non existing user returns 404"
        )
        self.assertEqual("User not found", res.json["message"])

    def test_demote_existing_user_from_admin_returns_ok(self):
        self.create_user("not_admin", "1234", "Not Admin", True)
        res = self.client.put(url_prefix + "/users/%s/demote" % self.user_public_id)
        self.assertEqual(
            200, res.status_code, url_prefix + "/users/<public_id>/demote should exist"
        )

        admin_value = res.json["user"]["admin"]
        self.assertEqual(False, admin_value, "User should be demoted to normal")

    def test_demote_non_existing_user_from_admin_returns_not_found(self):
        res = self.client.put(url_prefix + "/users/%s/demote" % "not_good_id")
        self.assertEqual(
            404, res.status_code, "Trying to demote non existing user returns 404"
        )
        self.assertEqual("User not found", res.json["message"])

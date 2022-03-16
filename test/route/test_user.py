from api.route.user import url_prefix
from api.route.auth import url_prefix as auth_prefix
from test.base_test import BaseTest
from test.route.test_auth import get_basic_auth, get_bearer


class TestUser(BaseTest):
    def setUp(self) -> None:
        super().setUp()
        self.create_user("mirabel_madrigal", "casita", "Mirabel Madrigal", admin=False)
        self._set_login_info()

    def test_get_user_profile_with_logged_user_returns_profile_info(self):
        res = self.client.get(
            url_prefix + "/%s" % self.user_public_id,
            headers={"Authorization": self.authorization},
        )
        self.assertEqual(200, res.status_code, url_prefix + "/<public_id> returns 200")
        info = res.get_json()
        self.assertEqual(
            info["display_name"],
            self.display_name,
            "When user is authorized should return info",
        )
        self.assertNotIn("admin", info, "Normal user should not see user_profile.admin")
        self.assertNotIn(
            "banned", info, "Normal user should not see user_profile.banned"
        )

    def test_get_user_profile_with_admin_returns_profile_info(self):
        original_user_display_name = self.display_name
        original_user_public_id = self.user_public_id
        self.create_user("admin", "admin", admin=True)
        self._set_login_info()
        res = self.client.get(
            url_prefix + "/%s" % original_user_public_id,
            headers={"Authorization": self.authorization},
        )
        self.assertEqual(200, res.status_code, url_prefix + "/<public_id> returns 200")
        info = res.get_json()
        self.assertEqual(
            info["display_name"],
            original_user_display_name,
            "Admin checking another person's profile should return info",
        )
        self.assertIn("admin", info, "Admin should see user_profile.admin")
        self.assertIn("banned", info, "Admin should see user_profile.banned")

    def test_get_user_profile_with_admin_with_incorrect_public_id_returns_not_found(
        self,
    ):
        res = self.client.get(
            url_prefix + "/%s" % "not_public_id",
            headers={"Authorization": self.authorization},
        )
        self.assertEqual(
            404,
            res.status_code,
            "Retrieving user profile with incorrect id should return 404",
        )

    def _set_login_info(self):
        login_auth = get_basic_auth("%s:%s" % (self.username, self.password))
        res = self.client.get(
            auth_prefix + "/login", headers={"Authorization": login_auth}
        )
        self.authorization = get_bearer(res.json["token"])

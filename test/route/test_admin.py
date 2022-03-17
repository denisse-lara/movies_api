import unittest

from flask import json

from api.model.movie import Movie
from api.route.admin import url_prefix
from test.base_test import BaseTest
from api.model.user_profile import UserProfile
from test.route.test_auth import get_basic_auth, url_prefix as auth_prefix


class TestAdmin(BaseTest):
    def setUp(self) -> None:
        super().setUp()

        with self.app.app_context():
            user = UserProfile.query.filter_by(username="admin").first()

            if not user:
                self.create_user("admin", "admin", "Admin", True)

            authorization = get_basic_auth("admin:admin")
            res = self.client.get(
                auth_prefix + "/login",
                headers={"Authorization": authorization},
            )
            self.admin_token = res.json["token"]

    # @unittest.skip
    def test_get_all_users_returns_user_list(self):
        self.create_user("user1", "1234", "User 1", False)
        self.create_user("user2", "1234", "User 2", False)
        self.create_user("user3", "1234", "User 3", False)

        res = self.client.get(
            url_prefix + "/users",
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )
        self.assertEqual(
            200, res.status_code, url_prefix + "/users endpoint should exist"
        )

        users = json.loads(json.dumps(res.json))
        # counts the admin user
        self.assertEqual(len(users), 4, "")

    # @unittest.skip
    def test_promote_existing_user_to_admin_returns_ok(self):
        self.create_user("not_admin", "1234", "Not Admin", admin=False)
        res = self.client.put(
            url_prefix + "/users/%s/promote" % self.user_public_id,
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )
        self.assertEqual(
            200, res.status_code, url_prefix + "/users/<public_id>/promote should exist"
        )

        self.assertIn("user", res.json, "Response should return the user data")
        admin_value = res.json["user"]["admin"]
        self.assertEqual(True, admin_value, "User should be promoted to admin")

    # @unittest.skip
    def test_promote_non_existing_user_to_admin_returns_not_found(self):
        res = self.client.put(
            url_prefix + "/users/%s/promote" % "not_good_id",
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )
        self.assertEqual(
            404, res.status_code, "Trying to promote non existing user returns 404"
        )
        self.assertEqual("User not found", res.json["message"])

    # @unittest.skip
    def test_demote_existing_user_from_admin_returns_ok(self):
        self.create_user("not_admin", "1234", "Not Admin", admin=True)
        res = self.client.put(
            url_prefix + "/users/%s/demote" % self.user_public_id,
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )
        self.assertEqual(
            200, res.status_code, url_prefix + "/users/<public_id>/demote should exist"
        )

        self.assertIn("user", res.json, "Response should return the user data")
        admin_value = res.json["user"]["admin"]
        self.assertEqual(False, admin_value, "User should be demoted to normal")

    # @unittest.skip
    def test_demote_non_existing_user_from_admin_returns_not_found(self):
        res = self.client.put(
            url_prefix + "/users/%s/demote" % "not_good_id",
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )
        self.assertEqual(
            404, res.status_code, "Trying to demote non existing user returns 404"
        )
        self.assertEqual("User not found", res.json["message"])

    # @unittest.skip
    def test_ban_existing_user_returns_ok(self):
        self.create_user("not_admin", "1234", "Not Admin", banned=False)
        res = self.client.put(
            url_prefix + "/users/%s/ban" % self.user_public_id,
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )
        self.assertEqual(
            200, res.status_code, url_prefix + "/users/<public_id>/ban should exist"
        )

        self.assertIn("user", res.json, "Response should return the user data")
        banned_value = res.json["user"]["banned"]
        self.assertEqual(True, banned_value, "User should be banned")

    # @unittest.skip
    def test_ban_non_existing_user_returns_not_found(self):
        res = self.client.put(
            url_prefix + "/users/%s/ban" % "not_good_id",
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )
        self.assertEqual(
            404, res.status_code, "Trying to ban non existing user returns 404"
        )
        self.assertEqual("User not found", res.json["message"])

    # @unittest.skip
    def test_unban_existing_user_returns_ok(self):
        self.create_user("banned", "1234", "Banned", banned=True)
        res = self.client.put(
            url_prefix + "/users/%s/unban" % self.user_public_id,
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )
        self.assertEqual(
            200, res.status_code, url_prefix + "/users/<public_id>/unban should exist"
        )

        self.assertIn("user", res.json, "Response should return the user data")
        banned_value = res.json["user"]["banned"]
        self.assertEqual(False, banned_value, "User should be unbanned")

    # @unittest.skip
    def test_unban_non_existing_user_returns_not_found(self):
        res = self.client.put(
            url_prefix + "/users/%s/unban" % "not_good_id",
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )
        self.assertEqual(
            404, res.status_code, "Trying to unban non existing user returns 404"
        )
        self.assertEqual("User not found", res.json["message"])

    # @unittest.skip
    def test_delete_existing_user_returns_ok(self):
        self.create_user("created", "1234", "created")
        res = self.client.delete(
            url_prefix + "/users/%s" % self.user_public_id,
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )
        self.assertEqual(
            200, res.status_code, url_prefix + "/users/<public_id>/unban should exist"
        )
        self.assertIn("deleted", res.json["message"], "User should be deleted")

    # @unittest.skip
    def test_delete_non_existing_user_returns_not_found(self):
        res = self.client.delete(
            url_prefix + "/users/%s" % "not_good_id",
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )
        self.assertEqual(
            404, res.status_code, "Trying to delete non existing user returns 404"
        )
        self.assertEqual("User not found", res.json["message"])

    # @unittest.skip
    def test_admin_add_a_movie_returns_ok(self):
        movie = {"title": "The Lord of the Rings", "release_year": 2001}

        res = self.client.post(
            url_prefix + "/movies",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            json=movie,
        )
        self.assertEqual(201, res.status_code, "Admin adding a movie returns 201")
        movie_json = res.get_json()
        self.assertEqual(movie["title"], movie_json["title"])

    # @unittest.skip
    def test_admin_add_movie_without_required_param_returns_error(self):
        movie = {"release_year": 2001}

        res = self.client.post(
            url_prefix + "/movies",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            json=movie,
        )
        self.assertEqual(422, res.status_code)
        response = res.get_json()
        self.assertEqual("Missing required fields", response["message"])
        self.assertIn("title", response["description"])

    # @unittest.skip
    def test_non_admin_add_movie_returns_forbidden(self):
        self.create_user("created", "1234", "created")
        authorization = get_basic_auth("created:1234")
        res = self.client.get(
            auth_prefix + "/login",
            headers={"Authorization": authorization},
        )
        token = res.json["token"]
        movie = {"title": "The Lord of the Rings", "release_year": 2001}
        res = self.client.post(
            url_prefix + "/movies",
            headers={"Authorization": f"Bearer {token}"},
            json=movie,
        )
        self.assertEqual(403, res.status_code, "Non admin adding a movie returns 403")

    # @unittest.skip
    def test_admin_update_existing_movie_returns_ok(self):
        self.movie_id = ""
        with self.app.app_context():
            movie = Movie(title="Movie Title", release_year=2011)
            self.db.session.add(movie)
            self.db.session.commit()
            self.movie_id = movie.public_id

        new_values = {"title": "New Title", "release_year": 2010}
        res = self.client.put(
            url_prefix + "/movies/%s" % self.movie_id,
            headers={"Authorization": f"Bearer {self.admin_token}"},
            json=new_values,
        )
        movie_json = res.get_json()
        self.assertEqual(200, res.status_code, "Admin modifying movie returns 200")
        self.assertEqual("New Title", movie_json["title"])
        self.assertEqual(2010, movie_json["release_year"])

    # @unittest.skip
    def test_admin_update_non_existing_movie_returns_not_found(self):
        movie_id = ""
        new_values = {}
        res = self.client.put(
            url_prefix + "/movies/%s" % movie_id,
            headers={"Authorization": f"Bearer {self.admin_token}"},
            json=new_values,
        )
        self.assertEqual(
            404, res.status_code, "Admin modifying non existing movie returns 404"
        )

    # @unittest.skip
    def test_performing_operations_without_authorization_token_returns_unauthorized(
        self,
    ):
        self.create_user("created", "1234", "created")
        res = self.client.get(
            url_prefix + "/users",
        )
        self.assertEqual(401, res.status_code, "Missing token should return 401")
        res = self.client.put(
            url_prefix + "/users/%s/promote" % self.user_public_id,
        )
        self.assertEqual(401, res.status_code, "Missing token should return 401")
        res = self.client.put(
            url_prefix + "/users/%s/demote" % self.user_public_id,
        )

    # @unittest.skip
    def test_performing_admin_operations_without_admin_user_returns_forbidden(self):
        self.create_user("created", "1234", "created")

        authorization = get_basic_auth("created:1234")
        res = self.client.get(
            auth_prefix + "/login",
            headers={"Authorization": authorization},
        )
        token = res.json["token"]

        res = self.client.get(
            url_prefix + "/users",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(403, res.status_code, "Normal user should not access admin")
        res = self.client.put(
            url_prefix + "/users/%s/promote" % self.user_public_id,
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(403, res.status_code, "Normal user should not access admin")

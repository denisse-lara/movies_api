from api.model.movie import Movie
from api.model.user_profile import UserProfile
from api.route.user import url_prefix
from test.base_test import BaseTest


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
        self.assertEqual(
            200, res.status_code, url_prefix + "/<public_id> should return 200"
        )
        info = res.get_json()
        self.assertEqual(
            info["name"],
            self.name,
            "When user is authorized should return info",
        )
        self.assertNotIn("admin", info, "Normal user should not see user_profile.admin")
        self.assertNotIn(
            "banned", info, "Normal user should not see user_profile.banned"
        )

    def test_get_user_profile_with_admin_returns_profile_info(self):
        original_user_name = self.name
        original_user_public_id = self.user_public_id
        self.create_user("admin", "admin", admin=True)
        self._set_login_info()
        res = self.client.get(
            url_prefix + "/%s" % original_user_public_id,
            headers={"Authorization": self.authorization},
        )
        self.assertEqual(
            200, res.status_code, url_prefix + "/<public_id> should return 200"
        )
        info = res.get_json()
        self.assertEqual(
            info["name"],
            original_user_name,
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

    def test_get_user_profile_with_incorrect_user_returns_not_found(self):
        original_user_name = self.name
        original_user_public_id = self.user_public_id
        self.create_user("another", "another")
        self._set_login_info()
        res = self.client.get(
            url_prefix + "/%s" % original_user_public_id,
            headers={"Authorization": self.authorization},
        )
        self.assertEqual(
            403,
            res.status_code,
            "When another user tries to access profile information should return 403",
        )

    def test_put_name_with_logged_user_returns_ok(self):
        res = self.client.put(
            url_prefix + "/%s" % self.user_public_id,
            headers={"Authorization": self.authorization},
            json={"name": "Maria"},
        )
        self.assertEqual(
            200, res.status_code, url_prefix + "/<public_id> should return 200"
        )
        info = res.get_json()
        self.assertEqual(
            info["name"],
            "Maria",
            "When user is authorized should change name",
        )

    def test_put_name_with_admin_returns_ok(self):
        original_user_public_id = self.user_public_id
        self.create_user("admin", "admin", admin=True)
        self._set_login_info()
        res = self.client.put(
            url_prefix + "/%s" % original_user_public_id,
            headers={"Authorization": self.authorization},
            json={"name": "Maria"},
        )
        self.assertEqual(
            200, res.status_code, url_prefix + "/<public_id> should return 200"
        )
        info = res.get_json()
        self.assertEqual(
            info["name"],
            "Maria",
            "Admin can change another user's name",
        )

    def test_put_name_without_correct_user_returns_forbidden(
        self,
    ):
        original_name = self.name
        original_user_public_id = self.user_public_id
        self.create_user("another", "another")
        self._set_login_info()
        res = self.client.get(
            url_prefix + "/%s" % original_user_public_id,
            headers={"Authorization": self.authorization},
            json={"name": "Maria"},
        )
        self.assertEqual(
            403,
            res.status_code,
            "Another user trying to change name should return 403",
        )

        with self.app.app_context():
            user = UserProfile.query.filter_by(
                public_id=original_user_public_id
            ).first()
            self.assertEqual(
                user.name,
                original_name,
                "Non authorized operation should not change the data",
            )
            self.assertNotEqual(
                user.name,
                "Maria",
                "Non authorized operation should not change the data",
            )

    def test_user_retrieve_liked_movies_returns_ok(self):
        with self.app.app_context():
            self.db.session.add(Movie(title="Movie Title", release_year=2010))
            self.db.session.add(Movie(title="Movie Title", release_year=2010))
            self.db.session.add(Movie(title="Movie Title", release_year=2010))
            user = UserProfile.query.filter_by(username=self.username).first()

            movies = Movie.query.all()
            for movie in movies:
                user.liked_movies.append(movie)
            self.db.session.commit()

        res = self.client.get(
            url_prefix + "/%s/movies" % self.user_public_id,
            headers={"Authorization": self.authorization},
        )
        self.assertEqual(
            200, res.status_code, url_prefix + "/<public_id>/movies should return 200"
        )

        movies = res.get_json()
        self.assertEqual(3, len(movies))

    def test_admin_retrieve_user_liked_movies_returns_ok(self):
        with self.app.app_context():
            movie = Movie(title="Movie Title", release_year=2010)
            self.db.session.add(movie)
            user = UserProfile.query.filter_by(username=self.username).first()
            user.liked_movies.append(movie)
            self.db.session.commit()

        original_user_public_id = self.user_public_id
        self.create_user("admin", "admin", admin=True)
        self._set_login_info()
        res = self.client.get(
            url_prefix + "/%s/movies" % original_user_public_id,
            headers={"Authorization": self.authorization},
        )
        self.assertEqual(
            200, res.status_code, url_prefix + "/<public_id>/movies should return 200"
        )

        movies = res.get_json()
        self.assertEqual(1, len(movies))

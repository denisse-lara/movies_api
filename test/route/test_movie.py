from api.model.movie import Movie
from api.route.movie import url_prefix
from test.base_test import BaseTest


class TestMovie(BaseTest):
    def setUp(self) -> None:
        super().setUp()

        self.create_user("User", "1234")
        self._set_login_info()

        movie = Movie(title="The Lord of the Rings", release_year=2001)
        with self.app.app_context():
            self.movie_title = movie.title
            self.db.session.add(movie)
            self.db.session.commit()
            self.movie_id = movie.public_id

    def test_user_get_all_movies_returns_ok(self):
        res = self.client.get(url_prefix, headers={"Authorization": self.authorization})
        self.assertEqual(
            200, res.status_code, "User fetching all movies should return 200"
        )
        movies = res.get_json()
        self.assertEqual(1, len(movies))
        self.assertEqual(self.movie_title, movies[0]["title"])

    def test_unauthenticated_user_get_all_movies_returns_unauthorized(self):
        res = self.client.get(
            url_prefix,
        )
        self.assertEqual(
            401,
            res.status_code,
            "Unauthenticated user fetching all movies should return 401",
        )

    def test_user_fetch_one_movie_returns_ok(self):
        res = self.client.get(
            url_prefix + "/%s" % self.movie_id,
            headers={"Authorization": self.authorization},
        )
        self.assertEqual(
            200, res.status_code, "User fetching one movie should return 200"
        )
        movie = res.get_json()
        self.assertEqual(self.movie_title, movie["title"])

    def test_unauthenticated_user_fetch_one_movie_returns_unauthorized(self):
        res = self.client.get(
            url_prefix + "/%s" % self.movie_id,
        )
        self.assertEqual(
            401,
            res.status_code,
            "Unauthenticated user fetching one movie should return 401",
        )

    def test_user_fetch_not_existing_movie_returns_not_found(self):
        res = self.client.get(
            url_prefix + "/%s" % "not_valid",
            headers={"Authorization": self.authorization},
        )
        self.assertEqual(
            404,
            res.status_code,
            "Fetching a movie that doesn't exist should return 404",
        )

    def test_user_like_a_movie_returns_ok(self):
        res = self.client.put(
            url_prefix + "/%s/like" % self.movie_id,
            headers={"Authorization": self.authorization},
        )
        self.assertEqual(
            200, res.status_code, "User liking one movie should return 200"
        )
        movie = res.get_json()
        self.assertEqual(1, movie["likes"], "Movie likes should increase by 1")

    def test_user_can_only_like_a_movie_once(self):
        self.client.put(
            url_prefix + "/%s/like" % self.movie_id,
            headers={"Authorization": self.authorization},
        )
        res = self.client.put(
            url_prefix + "/%s/like" % self.movie_id,
            headers={"Authorization": self.authorization},
        )
        movie = res.get_json()
        self.assertEqual(1, movie["likes"], "User should only be able to like a movie once")

    def test_unauthenticated_user_like_a_movie_returns_unauthorized(self):
        res = self.client.put(
            url_prefix + "/%s/like" % self.movie_id,
        )
        self.assertEqual(
            401,
            res.status_code,
            "Unauthenticated user liking one movie should return 401",
        )

    def test_user_like_not_existing_movie_returns_not_found(self):
        res = self.client.put(
            url_prefix + "/%s/like" % "not_valid",
            headers={"Authorization": self.authorization},
        )
        self.assertEqual(
            404,
            res.status_code,
            "Liking a movie that doesn't exist should return 404",
        )


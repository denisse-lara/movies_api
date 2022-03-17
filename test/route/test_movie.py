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
        res = self.client.get(
            url_prefix,
            headers={"Authorization": self.authorization}
        )
        self.assertEqual(200, res.status_code, "User fetching all movies should return 200")
        movies = res.get_json()
        self.assertEqual(1, len(movies))
        self.assertEqual(self.movie_title, movies[0]["title"])

    def test_unauthenticated_user_get_all_movies_returns_unauthorized(self):
        res = self.client.get(
            url_prefix,
        )
        self.assertEqual(401, res.status_code, "Unauthenticated user fetching all movies should return 401")

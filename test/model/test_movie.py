import unittest
import uuid

from api.model.movie import Movie
from api.model.user_profile import UserProfile
from api.schema.movie import MovieSchema
from api.schema.user_profile import UserProfileSchema
from test.base_test import BaseTest


class TestMovieUnit(unittest.TestCase):
    def setUp(self) -> None:
        self.movie = Movie(
            title="The Lord of the Rings",
            release_year=2001,
            poster_img_url="https://image.tmdb.org/t/p/w500/6oom5QYQ2yQTMJIbnvbkBL9cHo6.jpg",
        )

    def test_str(self):
        """
        Movie.__str__ returns appropriate string.
        """
        str_movie = str(self.movie)
        self.assertIn("title", str_movie, "String doesn't include the title")
        self.assertIn(
            "The Lord of the Rings", str_movie, "String doesn't include the title"
        )
        self.assertIn("id", str_movie, "String doesn't include the id")

    def test_repr(self):
        """
        Movie.__repr__ returns appropriate representation
        """
        repr_user = repr(self.movie)
        self.assertEqual(
            f"Movie(title='{self.movie.title}', release_year={self.movie.release_year}, "
            f"poster_img_url='{self.movie.poster_img_url}')",
            repr_user,
        )


class TestMovieInt(BaseTest):
    def setUp(self) -> None:
        super().setUp()
        user1 = UserProfile(username="user", password="1234", display_name="user")
        user2 = UserProfile(username="user1", password="1234", display_name="user")
        user3 = UserProfile(username="user2", password="1234", display_name="user")
        movie = Movie(title="The Lord of the Rings", release_year=2001)

        with self.app.app_context():
            self.db.session.add(user1)
            self.db.session.add(user2)
            self.db.session.add(user3)
            self.db.session.add(movie)
            self.db.session.commit()

    def test_autogenerated_public_id(self):
        """
        Movie.public_id is autogenerated before insert
        """
        movie = Movie(title="The Lord of the Rings", release_year=2001)

        with self.app.app_context():
            self.db.session.add(movie)
            self.db.session.commit()

            created_movie = Movie.query.first()
            self.assertIsNot(
                None, created_movie.public_id, "Movie.public_id cannot be None"
            )
            try:
                uuid.UUID(created_movie.public_id, version=4)
            except ValueError:
                self.fail("Movie.public_id must be a valid uuid4 string")

    def test_a_user_can_like_a_movie(self):
        with self.app.app_context():
            user = UserProfile.query.first()
            movie = Movie.query.first()
            user.liked_movies.append(movie)
            self.db.session.commit()
            self.assertEqual(1, len(user.liked_movies))

    def test_movie_counts_likes(self):
        with self.app.app_context():
            movie = Movie.query.first()
            users = UserProfile.query.all()
            for user in users:
                user.liked_movies.append(movie)
            self.db.session.commit()
            self.assertEqual(3, len(movie.likes))

    def test_movie_schema_calculates_likes(self):
        with self.app.app_context():
            movie = Movie.query.first()
            users = UserProfile.query.all()
            for user in users:
                user.liked_movies.append(movie)
            self.db.session.commit()

            movie_schema = MovieSchema()
            result = movie_schema.dump(movie)
            self.assertEqual(3, result["likes"])

    def test_user_schema_shows_liked_movies(self):
        with self.app.app_context():
            self.db.session.add(Movie(title="The Lord of the Rings", release_year=2001))
            self.db.session.add(Movie(title="The Lord of the Rings", release_year=2001))
            self.db.session.commit()

            movies = Movie.query.all()
            user = UserProfile.query.first()
            for movie in movies:
                user.liked_movies.append(movie)
            self.db.session.commit()

            user_schema = UserProfileSchema()

            user_schema.context = user.liked_movies
            result = user_schema.dump(user)
            self.assertEqual(3, len(user.liked_movies))
            self.assertEqual(3, len(result["liked_movies"]))
            self.assertEqual(2001, result["liked_movies"][0]["release_year"])

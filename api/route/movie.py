import os
from functools import wraps

from flask import Blueprint, jsonify, json

from api.model.movie import Movie
from api.route.auth import authorized_user
from api.schema.movie import MovieSchema
from app import db

url_prefix = os.path.join(os.getenv("API_URL_PREFIX"), "movies")
movie_blueprint = Blueprint("movies", __name__, url_prefix=url_prefix)


def find_movie(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        movie_id = kwargs.get("public_id", "")
        movie = Movie.query.filter_by(public_id=movie_id).first()

        if not movie:
            return jsonify({"message": "Movie not found", "status_code": 404}), 404

        return f(movie, *args, **kwargs)

    return decorated


@movie_blueprint.route("", methods=["GET"])
@authorized_user
def get_all_movies(user):
    movies = Movie.query.all()
    movie_schema = MovieSchema(many=True)
    movies = movie_schema.dumps(movies)
    return jsonify(json.loads(movies)), 200


@movie_blueprint.route("/<public_id>", methods=["GET"])
@find_movie
@authorized_user
def get_movie(user, movie, public_id):
    movie_schema = MovieSchema()
    return jsonify(json.loads(movie_schema.dumps(movie))), 200


@movie_blueprint.route("/<public_id>/like", methods=["PUT"])
@find_movie
@authorized_user
def like_movie(user, movie, public_id):
    movie_schema = MovieSchema(exclude=["release_year", "poster_img_url"])
    user.liked_movies.append(movie)
    db.session.commit()
    return (
        jsonify(
            {
                "message": f"Movie '{movie.title}' liked",
                "movie": json.loads(movie_schema.dumps(movie)),
            }
        ),
        200,
    )


@movie_blueprint.route("/<public_id>/unlike", methods=["DELETE"])
@find_movie
@authorized_user
def unlike_movie(user, movie, public_id):
    movie_schema = MovieSchema(exclude=["release_year", "poster_img_url"])

    if user.liked_movies.count(movie) > 0:
        user.liked_movies.remove(movie)

    db.session.commit()
    return (
        jsonify(
            {
                "message": f"Movie '{movie.title}' unliked",
                "movie": json.loads(movie_schema.dumps(movie)),
            }
        ),
        200,
    )

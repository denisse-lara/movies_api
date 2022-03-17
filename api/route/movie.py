import os

from flask import Blueprint, jsonify, json

from api.model.movie import Movie
from api.route.auth import authorized_user
from api.schema.movie import MovieSchema

url_prefix = os.path.join(os.getenv("API_URL_PREFIX"), "movies")
movie_blueprint = Blueprint("movies", __name__, url_prefix=url_prefix)


@movie_blueprint.route("", methods=["GET"])
@authorized_user
def get_all_movies(user):
    movies = Movie.query.all()
    movie_schema = MovieSchema(many=True)
    movies = movie_schema.dumps(movies)
    return jsonify(json.loads(movies)), 200

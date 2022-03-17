import base64
import os
from functools import wraps

from flask import Blueprint, jsonify, json, request, make_response
from sqlalchemy import desc, asc

from api.model.movie import Movie
from api.route.auth import authorized_user
from api.route.paginate import paginate
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


def movie_query_filter(query, args):
    if "release_year" in args and type(json.loads(args.get("release_year"))) is int:
        query = query.filter_by(release_year=json.loads(args.get("release_year")))

    if "title" in args:
        query = query.filter(Movie.title.ilike(f"%{args.get('title').strip()}%"))

    return query


def movie_query_sort_by(query, args):
    if "sort" in args:
        sorting = args.get("sort").split(",")
        for by in sorting:
            order = desc if "-" in by else asc
            if "title" in by:
                query = query.order_by(order(Movie.title))
            elif "release_year" in by:
                query = query.order_by(order(Movie.release_year))

    return query


@movie_blueprint.route("", methods=["GET"])
@authorized_user
def get_all_movies(user):
    movie_schema = MovieSchema(many=True)
    query = Movie.query
    query = movie_query_filter(query, request.args)
    query = movie_query_sort_by(query, request.args)

    if "page" in request.args:
        page = request.args.get("page", 1, type=int)
        results = make_response(paginate(query, movie_schema, page, "movies"))
        results = make_response(results)
    else:
        movies = query.all()
        results = make_response((jsonify(json.loads(movie_schema.dumps(movies))), 200))

    return results


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
    return make_response(
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
    return make_response(
        jsonify(
            {
                "message": f"Movie '{movie.title}' unliked",
                "movie": json.loads(movie_schema.dumps(movie)),
            }
        ),
        200,
    )

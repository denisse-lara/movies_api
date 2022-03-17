import os
from functools import wraps

from flask import Blueprint, jsonify, json, request, make_response
from sqlalchemy import desc, asc

from api.model.movie import Movie
from api.model.user_profile import UserProfile
from api.route.auth import authorized_admin, clear_user_jwt
from api.route.movie import find_movie
from api.route.paginate import paginate
from api.schema.movie import MovieSchema
from api.schema.user_profile import UserProfileSchema
from app import db

url_prefix = os.path.join(os.getenv("API_URL_PREFIX"), "admin")
admin_blueprint = Blueprint("admin", __name__, url_prefix=url_prefix)


def find_user(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        public_id = kwargs.get("public_id", "")
        user = UserProfile.query.filter_by(public_id=public_id).first()

        if not user:
            return jsonify({"message": "User not found", "status_code": 404}), 404

        return f(user, *args, **kwargs)

    return decorated


def user_query_filter(query, args):
    if "admin" in args and type(json.loads(args.get("admin"))) is bool:
        query = query.filter_by(admin=json.loads(args.get("admin")))

    if "banned" in args and type(json.loads(args.get("banned"))) is bool:
        query = query.filter_by(banned=json.loads(args.get("banned")))

    return query


def user_query_sort_by(query, args):
    if "sort" in args:
        sorting = args.get("sort").split(",")
        for by in sorting:
            order = desc if "-" in by else asc
            if "username" in by:
                query = query.order_by(order(UserProfile.username))
            elif "name" in by:
                query = query.order_by(order(UserProfile.name))
            elif "banned" in by:
                query = query.order_by(order(UserProfile.banned))
            elif "admin" in by:
                query = query.order_by(order(UserProfile.admin))

    return query


@admin_blueprint.route("/users", methods=["GET"])
@authorized_admin
def get_all_users():
    users_schema = UserProfileSchema(many=True)
    query = UserProfile.query

    # filter by admin or banned
    query = user_query_filter(query, request.args)
    query = user_query_sort_by(query, request.args)

    if "page" in request.args:
        page = request.args.get("page", 1, type=int)
        results = make_response(paginate(query, users_schema, page, "users"))
    else:
        users = query.all()
        results = make_response((jsonify(json.loads(users_schema.dumps(users))), 200))

    return results


@admin_blueprint.route("/users/<public_id>/promote", methods=["PUT"])
@find_user
@authorized_admin
def promote_to_admin(user, public_id):
    if not user.admin:
        user.admin = True
        db.session.commit()

    user_schema = UserProfileSchema()
    return (
        jsonify(
            {
                "message": "User '%s' promoted to admin" % user.username,
                "user": json.loads(user_schema.dumps(user)),
            }
        ),
        200,
    )


@admin_blueprint.route("/users/<public_id>/demote", methods=["PUT"])
@find_user
@authorized_admin
def demote_to_normal(user, public_id):
    if user.admin:
        user.admin = False
        db.session.commit()

    user_schema = UserProfileSchema()
    return (
        jsonify(
            {
                "message": "User '%s' demoted to normal" % user.username,
                "user": json.loads(user_schema.dumps(user)),
            }
        ),
        200,
    )


@admin_blueprint.route("/users/<public_id>/ban", methods=["PUT"])
@find_user
@authorized_admin
def ban_user(user, public_id):
    if not user.banned:
        user.banned = True
        db.session.commit()
        clear_user_jwt(user.id)

    user_schema = UserProfileSchema()
    return (
        jsonify(
            {
                "message": "User '%s' banned" % user.username,
                "user": json.loads(user_schema.dumps(user)),
            }
        ),
        200,
    )


@admin_blueprint.route("/users/<public_id>/unban", methods=["PUT"])
@find_user
@authorized_admin
def unban_user(user, public_id):
    if user.banned:
        user.banned = False
        db.session.commit()

    user_schema = UserProfileSchema()
    return (
        jsonify(
            {
                "message": "User '%s' unbanned" % user.username,
                "user": json.loads(user_schema.dumps(user)),
            }
        ),
        200,
    )


@admin_blueprint.route("/users/<public_id>", methods=["DELETE"])
@find_user
@authorized_admin
def delete_user(user, public_id):
    username = user.username
    clear_user_jwt(user.id)
    db.session.delete(user)
    db.session.commit()

    return (
        jsonify({"message": "User '%s' deleted" % username}),
        200,
    )


@admin_blueprint.route("/movies", methods=["POST"])
@authorized_admin
def add_movie():
    movie_data = request.get_json()

    missing_fields = []

    if "title" not in movie_data:
        missing_fields.append("title")

    if "release_year" not in movie_data:
        missing_fields.append("release_year")

    if missing_fields:
        return (
            jsonify(
                {
                    "message": "Missing required fields",
                    "description": "Tried creating a movie without the field(s) %s"
                    % missing_fields,
                    "status_code": 422,
                }
            ),
            422,
        )

    movie = Movie(
        title=movie_data["title"],
        release_year=movie_data["release_year"],
        poster_img_url=movie_data.get("poster_img_url", ""),
    )
    db.session.add(movie)
    db.session.commit()

    movie_schema = MovieSchema()
    return jsonify(json.loads(movie_schema.dumps(movie))), 201


@admin_blueprint.route("/movies/<public_id>", methods=["PUT", "DELETE"])
@find_movie
@authorized_admin
def update_movie(movie, public_id):
    response = ""
    if request.method == "PUT":
        movie_data = request.get_json()

        if (
            "title" in movie_data
            and movie_data["title"] is not None
            and movie_data["title"] != ""
        ):
            movie.title = movie_data["title"]

        if (
            "release_year" in movie_data
            and movie_data["release_year"] is not None
            and movie_data["release_year"] != ""
        ):
            movie.release_year = movie_data["release_year"]

        if (
            "poster_img_url" in movie_data
            and movie_data["poster_img_url"] is not None
            and movie_data["poster_img_url"] != ""
        ):
            movie.poster_img_url = movie_data["poster_img_url"]

        db.session.commit()

        movie_schema = MovieSchema()
        response = json.loads(movie_schema.dumps(movie))

    if request.method == "DELETE":
        response = {"message": "Movie '%s' deleted" % movie.title, "status_code": 200}
        db.session.delete(movie)
        db.session.commit()

    return jsonify(response), 200

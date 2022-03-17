import os
from functools import wraps

from flask import Blueprint, make_response, jsonify, json, request

from api.model.user_profile import UserProfile
from api.route.auth import authorized_user
from api.schema.movie import MovieSchema
from api.schema.user_profile import UserProfileSchema
from app import db

url_prefix = os.path.join(os.getenv("API_URL_PREFIX"), "users")
user_blueprint = Blueprint("users", __name__, url_prefix=url_prefix)

forbidden_response = (
    {
        "message": "Forbidden access for the current user",
        "description": "Users can only retrieve or edit their own information.",
        "status_code": 403,
    },
    403,
)


def profile_exists(f):
    """
    Checks if the user with the provided public id exists
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        public_id = kwargs.get("public_id", "")
        queried_user = UserProfile.query.filter_by(public_id=public_id).first()

        if not queried_user:
            return (
                jsonify({"message": "User information not found", "status_code": 404}),
                404,
            )

        return f(*args, **kwargs)

    return decorated


@user_blueprint.route("/<public_id>", methods=["GET", "PUT"])
@profile_exists
@authorized_user
def get_user_profile(current_user, public_id):
    user_info = UserProfile.query.filter_by(public_id=public_id).first()

    # forbid anyone that is not the user or an admin from accessing the information
    if current_user.public_id != public_id and not current_user.admin:
        return make_response(forbidden_response)

    # show extra information to admin user
    if not current_user.admin:
        user_schema = UserProfileSchema(exclude=["admin", "banned", "liked_movies"])
    else:
        user_schema = UserProfileSchema(exclude=["liked_movies"])

    if request.method == "PUT":
        data = request.get_json()
        user_info.name = data.get("name", user_info.name)
        db.session.commit()

    return jsonify(json.loads(user_schema.dumps(user_info))), 200


@user_blueprint.route("/<public_id>/movies", methods=["GET"])
@profile_exists
@authorized_user
def get_user_liked_movies(current_user, public_id):
    user_info = UserProfile.query.filter_by(public_id=public_id).first()

    # forbid anyone that is not the user or an admin from accessing the information
    if current_user.public_id != public_id and not current_user.admin:
        return make_response(forbidden_response)

    movie_schema = MovieSchema(many=True)
    movies = movie_schema.dumps(user_info.liked_movies)

    return jsonify(json.loads(movies)), 200

import os

from flask import Blueprint, make_response, jsonify, json

from api.model.user_profile import UserProfile
from api.route.auth import authorized_user
from api.schema.user_profile import UserProfileSchema

url_prefix = os.path.join(os.getenv("API_URL_PREFIX"), "users")
user_blueprint = Blueprint("users", __name__, url_prefix=url_prefix)


@user_blueprint.route("/<public_id>", methods=["GET"])
@authorized_user
def get_user_profile(current_user, public_id):
    user_info = UserProfile.query.filter_by(public_id=public_id).first()

    if not user_info:
        return make_response(
            ({"message": "User information not found", "status_code": 404}, 404)
        )

    if current_user.public_id != public_id and not current_user.admin:
        return make_response(
            (
                {
                    "message": "Forbidden access for the current user",
                    "description": "Users can only retrieve their own information.",
                    "status_code": 403,
                },
                403,
            )
        )

    if not current_user.admin:
        user_schema = UserProfileSchema(exclude=["admin", "banned"])
    else:
        user_schema = UserProfileSchema()

    return jsonify(json.loads(user_schema.dumps(user_info))), 200

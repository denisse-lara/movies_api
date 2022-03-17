import os

from flask import Blueprint, make_response, jsonify, json, request

from api.model.user_profile import UserProfile
from api.route.auth import authorized_user
from api.schema.user_profile import UserProfileSchema
from app import db

url_prefix = os.path.join(os.getenv("API_URL_PREFIX"), "users")
user_blueprint = Blueprint("users", __name__, url_prefix=url_prefix)


@user_blueprint.route("/<public_id>", methods=["GET", "PUT"])
@authorized_user
def get_user_profile(current_user, public_id):
    # check if the user exists
    user_info = UserProfile.query.filter_by(public_id=public_id).first()
    if not user_info:
        return make_response(
            ({"message": "User information not found", "status_code": 404}, 404)
        )

    # forbid anyone that is not the user or an admin from accessing the information
    forbidden_response = make_response(
        (
            {
                "message": "Forbidden access for the current user",
                "description": "Users can only retrieve or edit their own information.",
                "status_code": 403,
            },
            403,
        )
    )
    if current_user.public_id != public_id and not current_user.admin:
        return forbidden_response

    # show extra information to admin user
    if not current_user.admin:
        user_schema = UserProfileSchema(exclude=["admin", "banned"])
    else:
        user_schema = UserProfileSchema()

    if request.method == "PUT":
        data = request.get_json()
        user_info.display_name = data.get("display_name", user_info.display_name)
        db.session.commit()

    return jsonify(json.loads(user_schema.dumps(user_info))), 200

from flask import Blueprint, jsonify, json

from api.model.user_profile import UserProfile
from api.schema.user_profile import UserProfileSchema

admin_blueprint = Blueprint("admin", __name__, url_prefix="/admin")

# TODO: validate that it is admin user


@admin_blueprint.route("/users", methods=["GET"])
def get_all_users():
    users = UserProfile.query.all()
    users_schema = UserProfileSchema(many=True)
    users_list = users_schema.dumps(users)
    return jsonify(json.loads(users_list)), 200


# TODO: promote to admin

# TODO: demote to normal

# TODO: ban user

# TODO: delete user

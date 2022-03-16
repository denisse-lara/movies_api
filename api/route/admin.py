import os

from flask import Blueprint, jsonify, json

from api.model.user_profile import UserProfile
from api.schema.user_profile import UserProfileSchema
from app import db

url_prefix = os.path.join(os.getenv("API_URL_PREFIX"), "admin")
admin_blueprint = Blueprint("admin", __name__, url_prefix=url_prefix)

# TODO: validate that it is admin user


@admin_blueprint.route("/users", methods=["GET"])
def get_all_users():
    users = UserProfile.query.all()
    users_schema = UserProfileSchema(many=True)
    users_list = users_schema.dumps(users)
    return jsonify(json.loads(users_list)), 200


@admin_blueprint.route("/users/<public_id>/promote", methods=["PUT"])
def promote_to_admin(public_id):
    user = UserProfile.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    if not user.admin:
        user.admin = True
        db.session.commit()

    user_schema = UserProfileSchema()
    return jsonify(json.loads(user_schema.dumps(user))), 200


@admin_blueprint.route("/users/<public_id>/demote", methods=["PUT"])
def demote_to_normal(public_id):
    user = UserProfile.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    if user.admin:
        user.admin = False
        db.session.commit()

    user_schema = UserProfileSchema()
    return jsonify(json.loads(user_schema.dumps(user))), 200

# TODO: ban user

# TODO: delete user

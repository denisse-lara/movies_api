import os
from functools import wraps

from flask import Blueprint, jsonify, json

from api.model.user_profile import UserProfile
from api.route.auth import authorized_admin, clear_user_jwt
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


@admin_blueprint.route("/users", methods=["GET"])
@authorized_admin
def get_all_users():
    users = UserProfile.query.all()
    users_schema = UserProfileSchema(many=True)
    users_list = users_schema.dumps(users)
    return jsonify(json.loads(users_list)), 200


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

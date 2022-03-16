import datetime
import json
import os

import jwt
import sqlalchemy.exc
from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash

import config
from api.model.user_profile import UserProfile
from api.model.auth import JWTWhitelist
from api.schema.user_profile import UserProfileSchema
from app import db

url_prefix = os.path.join(os.getenv("API_URL_PREFIX"), "auth")
auth_blueprint = Blueprint("auth", __name__, url_prefix=url_prefix)


@auth_blueprint.route("/login", methods=["GET"])
def login():
    auth = request.authorization

    error_response = {
        "status_code": 401,
        "message": "Invalid user credentials",
        "description": "Basic realm='Provide valid credentials'",
    }

    if not auth or not auth.username or not auth.password:
        error_response["message"] = "Invalid authorization request"
        return jsonify(error_response), 401

    user_profile = UserProfile.query.filter_by(username=auth.username).first()

    if not user_profile:
        return jsonify(error_response), 401

    if check_password_hash(user_profile.password, auth.password):
        jwt_whited = JWTWhitelist.query.filter_by(user_id=user_profile.id).first()

        if not jwt_whited:
            jwt_whited = generate_user_token(user_profile)
            return jsonify({"token": jwt_whited.token})

        # if existing token is still valid, return it
        # otherwise, recreate it
        try:
            jwt.decode(bytes(jwt_whited.token, "utf-8"), config.SECRET_KEY, algorithms=config.JWT_ALGORITHMS)
        except jwt.ExpiredSignatureError:
            db.session.delete(jwt_whited)
            db.session.commit()
            jwt_whited = generate_user_token(user_profile)
        finally:
            return jsonify({"token": jwt_whited.token})

    return jsonify(error_response), 401


@auth_blueprint.route("/register", methods=["POST"])
def register():
    user_data = request.get_json()

    if not user_data.get("username") or not user_data.get("password"):
        return {
            "message": "Missing user data",
            "status_code": 422,
        }, 422

    try:
        new_user_profile = UserProfile(
            username=user_data["username"],
            password=user_data["password"],
            display_name=user_data.get("display_name", None),
        )
        db.session.add(new_user_profile)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        return {
            "message": "User with username already exists",
            "status_code": 500,
        }, 500

    user_schema = UserProfileSchema(exclude=["admin", "banned"])

    return {
        "message": "User created",
        "user": json.loads(user_schema.dumps(new_user_profile)),
    }, 201


@auth_blueprint.route("/logout", methods=["GET"])
def logout():
    if "Authorization" not in request.headers:
        return {
            "status_code": 401,
            "message": "Missing authorization bearer token",
        }, 401

    bearer = request.headers["Authorization"]
    if len(bearer.split(" ")) < 2:
        return {
            "status_code": 401,
            "message": "Missing authorization bearer token",
        }, 401

    token = bearer.split(" ")[1]
    whited = JWTWhitelist.query.filter_by(token=token).first()
    if not whited:
        return {"message": "No user logged"}, 200

    if whited:
        db.session.delete(whited)
        db.session.commit()

    return {"message": "User logged out"}, 200


def generate_user_token(user_profile: UserProfile):
    token = jwt.encode(
        {
            "public_id": user_profile.public_id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        },
        config.SECRET_KEY,
        algorithm=config.JWT_ALGORITHMS,
    )
    jwt_whited = JWTWhitelist(user_id=user_profile.id, token=token)
    db.session.add(jwt_whited)
    db.session.commit()

    return jwt_whited

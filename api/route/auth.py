import datetime

import jwt
from flask import Blueprint, request, make_response, jsonify
from werkzeug.security import check_password_hash

import config
from api.model.user_profile import UserProfile

auth_blueprint = Blueprint("auth", __name__, url_prefix="/auth")


@auth_blueprint.route("/login")
def login():
    auth = request.authorization

    error_response = {
        "status_code": 401,
        "message": "Invalid user credentials",
        "description": "Basic realm='Provide valid credentials'"
    }

    if not auth or not auth.username or not auth.password:
        error_response["message"] = "Invalid authorization request"
        return jsonify(error_response), 401

    user_profile = UserProfile.query.filter_by(username=auth.username).first()

    if not user_profile:
        return jsonify(error_response), 401

    if check_password_hash(user_profile.password, auth.password):
        token = jwt.encode(
            {
                "public_id": user_profile.public_id,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
            },
            config.SECRET_KEY,
            algorithm=config.JWT_ALGORITHMS,
        )
        return jsonify({"token": token})

    return jsonify(error_response), 401

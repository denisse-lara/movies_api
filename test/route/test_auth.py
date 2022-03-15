import base64
import jwt

import config

from urllib.parse import unquote
from flask import json

from test.base_test import BaseTest
from api.model.user_profile import UserProfile


class TestAuth(BaseTest):
    def setUp(self) -> None:
        super().setUp()
        self.username = "admin"
        self.password = "12345"
        self.display_name = "Admin"
        with self.app.app_context():
            user = UserProfile(
                username=self.username,
                password=self.password,
                display_name=self.display_name,
                admin=True,
            )
            self.db.session.add(user)
            self.db.session.commit()
            self.user_public_id = user.public_id

    def test_register_user_with_complete_data(self):
        payload = {
            "username": "normal_user",
            "password": "safe-password123",
            "display_name": "Normal User",
        }
        res = self.client.post("/auth/register", json=payload)
        self.assertEqual(201, res.status_code, "Valid registration returns 201")
        self.assertIn(
            "user", res.json, "Registration response returns new user information"
        )

        new_user = json.loads(json.dumps(res.json["user"]))
        self.assertTrue(
            new_user["public_id"], "Response must include the user public_id"
        )
        self.assertEqual(new_user["username"], payload["username"])
        self.assertEqual(new_user["display_name"], payload["display_name"])

    def test_register_user_with_incomplete_data(self):
        # no password
        payload = {"username": "normal_user"}
        res = self.client.post("/auth/register", json=payload)
        self.assertEqual(422, res.status_code, "Invalid registration should return 422")
        self.assertEqual("Missing user data", res.json["message"])

        # no username
        payload = {"password": "12345"}
        res = self.client.post("/auth/register", json=payload)
        self.assertEqual(422, res.status_code, "Invalid registration should return 422")
        self.assertEqual("Missing user data", res.json["message"])

    def test_login_with_no_auth_credentials_returns_not_authorized(self):
        res = self.client.get("/auth/login")
        self.assertEqual(
            401,
            res.status_code,
            msg="Authenticating without credentials should raise 401 error",
        )

    def test_login_auth_with_credentials_returns_jwt(self):
        authorization = get_encoded_authorization(
            "%s:%s" % (self.username, self.password)
        )
        res = self.client.get("/auth/login", headers={"Authorization": authorization})
        self.assertNotEqual(
            None, res.json, "Authenticating with valid credentials should return a json"
        )
        self.assertIn("token", res.json, "Authenticating should return a JWT token")

        try:
            jwt.decode(
                jwt=res.json["token"],
                key=config.SECRET_KEY,
                algorithms=config.JWT_ALGORITHMS,
            )
        except jwt.exceptions.DecodeError as de:
            self.fail(
                f"DecodeError: {de}. " "Authentication token should be a valid JWT"
            )

    def test_login_multiple_times_returns_same_token_if_not_expired(self):
        authorization = get_encoded_authorization(
            "%s:%s" % (self.username, self.password)
        )
        res = self.client.get("/auth/login", headers={"Authorization": authorization})
        token1 = res.json["token"]
        res = self.client.get("/auth/login", headers={"Authorization": authorization})
        token2 = res.json["token"]
        self.assertEqual(token1, token2)

    def test_login_with_correct_credentials_returns_correct_public_id(self):
        authorization = get_encoded_authorization(
            "%s:%s" % (self.username, self.password)
        )
        res = self.client.get("/auth/login", headers={"Authorization": authorization})

        decoded_token = jwt.decode(
            jwt=res.json["token"],
            key=config.SECRET_KEY,
            algorithms=config.JWT_ALGORITHMS,
        )
        self.assertEqual(
            decoded_token["public_id"],
            self.user_public_id,
            "JWT should contain the public id of the authenticated user",
        )

    def test_login_with_incorrect_credentials_returns_not_authorized(self):
        authorization = get_encoded_authorization("%s:52687" % self.username)
        res = self.client.get("/auth/login", headers={"Authorization": authorization})
        self.assertEqual(
            401, res.status_code, "Authentication with wrong password should return 401"
        )
        self.assertEqual("Invalid user credentials", res.json["message"])

        authorization = get_encoded_authorization("nimda:%s" % self.password)
        res = self.client.get("/auth/login", headers={"Authorization": authorization})
        self.assertEqual(
            401, res.status_code, "Authentication with wrong username should return 401"
        )
        self.assertEqual("Invalid user credentials", res.json["message"])

    def test_logout_logged_user(self):
        res = self.client.get("/auth/logout")
        self.assertEqual(401, res.status_code, "User must be logged in before logging out")

        res = self.client.get("/auth/logout", headers={"Authorization": "Bearer"})
        self.assertEqual(401, res.status_code, "Authorization header must have bearer token")

        authorization = get_encoded_authorization(
            "%s:%s" % (self.username, self.password)
        )
        res = self.client.get("/auth/login", headers={"Authorization": authorization})
        token = res.json["token"]

        authorization = get_encoded_bearer(token)
        res = self.client.get("/auth/logout", headers={"Authorization": authorization})
        self.assertEqual(200, res.status_code)


def get_encoded_authorization(credentials):
    return f"Basic %s" % base64.b64encode(bytes(credentials, "utf-8")).decode("utf-8")


def get_encoded_bearer(token):
    return f"Bearer %s" % base64.b64encode(bytes(token, "utf-8")).decode("utf-8")

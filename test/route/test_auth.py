import base64
import jwt
import config

from urllib.parse import unquote

from test.base_test import BaseTest
from api.model.user_profile import UserProfile


class TestLoginAuth(BaseTest):
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

    def test_login_with_no_auth_credentials_returns_not_authorized(self):
        res = self.client.get("/auth/login")
        self.assertEqual(
            401,
            res.status_code,
            msg="Authenticating without credentials should raise 401 error",
        )

    def test_login_auth_with_credentials_returns_jwt(self):
        authorization = get_encoded_authorization("%s:%s" % (self.username, self.password))
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
                f"DecodeError: {de}. "
                "Authentication token should be a valid JWT"
            )

    def test_login_with_correct_credentials_returns_correct_public_id(self):
        authorization = get_encoded_authorization("%s:%s" % (self.username, self.password))
        res = self.client.get("/auth/login", headers={"Authorization": authorization})

        decoded_token = jwt.decode(
            jwt=res.json["token"],
            key=config.SECRET_KEY,
            algorithms=config.JWT_ALGORITHMS,
        )
        self.assertEqual(
            decoded_token["public_id"],
            self.user_public_id,
            "JWT should contain the public id of the authenticated user"
        )

    def test_login_with_incorrect_credentials_returns_not_authorized(self):
        authorization = get_encoded_authorization("%s:52687" % self.username)
        res = self.client.get(
            "/auth/login",
            headers={"Authorization": authorization}
        )
        self.assertEqual(401, res.status_code, "Authentication with wrong password should return 401")
        self.assertEqual("Invalid user credentials", res.json["message"])

        authorization = get_encoded_authorization("nimda:%s" % self.password)
        res = self.client.get("/auth/login", headers={"Authorization": authorization})
        self.assertEqual(401, res.status_code, "Authentication with wrong username should return 401")
        self.assertEqual("Invalid user credentials", res.json["message"])


def get_encoded_authorization(credentials):
    return f"Basic %s" % base64.b64encode(
            bytes(credentials, "utf-8")
        ).decode("utf-8")

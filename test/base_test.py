import base64
import unittest

from app import create_app, db

from api.model.user_profile import UserProfile
from api.route.auth import url_prefix as auth_prefix


def setup_env():
    new_app = create_app()
    new_app.config.update(
        {
            "TESTING": True,
            "DEBUG": True,
            "APP_ENV": "testing",
            "WTF_CSRF_ENABLED": False,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///instance/test.db",
        }
    )

    new_db = db
    with new_app.app_context():
        new_db.create_all()

    return new_app, new_db


class BaseTest(unittest.TestCase):
    def setUp(self) -> None:
        self.app, self.db = setup_env()
        self.client = self.app.test_client()

    def tearDown(self) -> None:
        with self.app.app_context():
            self.db.session.remove()
            self.db.drop_all()

    def create_user(self, username, password, name=None, admin=False, banned=False):
        with self.app.app_context():
            user = UserProfile(
                username=username,
                password=password,
                name=name,
                admin=admin,
                banned=banned,
            )
            self.username = username
            self.password = password
            self.name = name

            self.db.session.add(user)
            self.db.session.commit()

            self.user_public_id = user.public_id

    def _set_login_info(self):
        login_auth = get_basic_auth("%s:%s" % (self.username, self.password))
        res = self.client.get(
            auth_prefix + "/login", headers={"Authorization": login_auth}
        )
        self.authorization = get_bearer(res.json["token"])


def get_basic_auth(credentials):
    return f"Basic %s" % base64.b64encode(bytes(credentials, "utf-8")).decode("utf-8")


def get_bearer(token):
    return f"Bearer %s" % token

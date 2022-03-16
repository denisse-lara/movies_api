import unittest

from app import create_app, db

from api.model.user_profile import UserProfile


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

    def create_user(
        self, username, password, display_name=None, admin=False, banned=False
    ):
        with self.app.app_context():
            user = UserProfile(
                username=username,
                password=password,
                display_name=display_name,
                admin=admin,
                banned=banned,
            )
            self.username = username
            self.password = password
            self.display_name = display_name

            self.db.session.add(user)
            self.db.session.commit()

            self.user_public_id = user.public_id

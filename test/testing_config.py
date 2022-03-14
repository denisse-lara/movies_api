import app


def setup_env():
    new_app = app.create_app()
    new_app.config.update(
        {
            "TESTING": True,
            "DEBUG": True,
            "APP_ENV": "testing",
            "WTF_CSRF_ENABLED": False,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///instance/test.db",
        }
    )

    new_db = app.db
    with new_app.app_context():
        new_db.create_all()

    return new_app, new_db

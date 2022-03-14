from flask import Flask
from flasgger import Swagger
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import config

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)

    app.config["SWAGGER"] = {"title": "Movie Ratings API"}
    swagger = Swagger(app)

    # Initialize config
    app.config.from_pyfile("config.py")
    app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = config.SQLALCHEMY_TRACK_MODIFICATIONS

    db.init_app(app)
    migrate.init_app(app, db)

    from api.model import user_profile

    return app


if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        db.create_all()

    app.run(host=config.HOST, port=config.PORT)

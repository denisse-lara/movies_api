from flask import Flask
from flasgger import Swagger
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow

import config

db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()


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
    ma.init_app(app)

    from api.model import user_profile, auth, movie

    from api.route import auth, admin, user, movie

    app.register_blueprint(auth.auth_blueprint)
    app.register_blueprint(admin.admin_blueprint)
    app.register_blueprint(user.user_blueprint)
    app.register_blueprint(movie.movie_blueprint)

    return app


if __name__ == "__main__":
    app = create_app()

    app.run(host=config.APP_HOST, port=config.APP_PORT)

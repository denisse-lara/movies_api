import os

from flask import Flask
from flasgger import Swagger


def create_app():
    app = Flask(__name__)

    app.config["SWAGGER"] = {"title": "Movie Ratings API"}
    swagger = Swagger(app)

    # Initialize config
    app.config.from_pyfile("config.py")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host=os.getenv("HOST"), port=os.getenv("PORT"))

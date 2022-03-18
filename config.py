"""[General Configuration Params] """

from os import path

from dotenv import load_dotenv
from environs import Env

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))

env = Env()

SECRET_KEY = env.str("SECRET_KEY")

SQLALCHEMY_DATABASE_URI = env.str("SQLALCHEMY_DATABASE_URI")
SQLALCHEMY_TRACK_MODIFICATIONS = env.bool("SQLALCHEMY_TRACK_MODIFICATIONS")

APP_HOST = "localhost"
APP_PORT = "5001"

JWT_ALGORITHMS = "HS256"

ROWS_PER_PAGE = 25

API_URL_PREFIX = "/api/v1"

DATABASE_NAME = env.str("DATABASE_NAME")
DB_USER = env.str("DB_USER")
DB_PASSWORD = env.str("DB_PASSWORD")
DB_HOST = env.str("DB_HOST")
DB_PORT = env.str("DB_PORT")

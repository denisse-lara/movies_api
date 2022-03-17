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

HOST = env.str("HOST")
PORT = env.int("PORT")

JWT_ALGORITHMS = "HS256"

ROWS_PER_PAGE = 25

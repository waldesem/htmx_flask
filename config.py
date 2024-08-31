import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = "SUPERSECRETKEY"
    BASE_PATH = os.path.join(basedir, "..", "PersonalDB")
    DEFAULT_PASSWORD = "8" * 8
    DATABASE_URI = os.path.join("sqlite:///", "..", "database.db")

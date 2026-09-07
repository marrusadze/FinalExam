import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Config:
    """Base configuration, shared by all environments."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-insecure-key-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(basedir, "eventhub.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")

    # Shared secret for the JSON API's write endpoints (sent as the X-API-Key header).
    API_KEY = os.environ.get("API_KEY", "")

    UPLOAD_FOLDER = os.path.join(basedir, "app", "static", "uploads", "profile_pics")
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2 MB max upload size
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

    WTF_CSRF_ENABLED = True

    EVENTS_PER_PAGE = 9


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SECRET_KEY = "test-secret-key"
    API_KEY = "test-api-key"


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}

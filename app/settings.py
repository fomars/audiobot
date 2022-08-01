import os

from pydantic import BaseSettings

DEBUG = bool(os.getenv("DEBUG"))
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "app/output")
INPUT_DIR = os.getenv("INPUT_DIR", "app/input")

# telegram
API_TOKEN = os.getenv("API_TOKEN")
TELEGRAM_API_URL = os.getenv("API_URL", "https://api.telegram.org/bot")
LOCAL_API = bool(os.getenv("API_URL"))
API_WORKDIR = os.getenv("API_WORKDIR", "/var/lib/telegram-bot-api")

# s3
CLOUDCUBE_URL = os.getenv("CLOUDCUBE_URL")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

# ffmpeg
DEFAULT_LOUDNESS = int(os.getenv("TARGET_LOUDNESS", "-14"))
MAX_LOUDNESS = int(os.getenv("MAX_LOUDNESS", "-6"))
MIN_LOUDNESS = int(os.getenv("MIN_LOUDNESS", "-28"))
ACCEPTED_MIME_TYPES = r"^audio/[a-zA-Z0-9-_]+|application/ogg$"

# celery
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
BROKER_DB = 0
BACKEND_DB = 1
STORAGE_DB = 2


class DBSettings(BaseSettings):
    db_user: str
    db_password: str
    db_host: str = "db"
    db_port: str = "5432"
    db_name: str = "audiobot"

    @property
    def connection_str(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"  # noqa: E501


db_settings = DBSettings()

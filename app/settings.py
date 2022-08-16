import os

from pydantic import BaseSettings

DEBUG = bool(os.getenv("DEBUG"))
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "app/output")
INPUT_DIR = os.getenv("INPUT_DIR", "app/input")
APP_THREADS = int(os.getenv("APP_THREADS", "8"))

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
AUDIO_MIME_TYPES = r"^audio/[a-zA-Z0-9-_]+|application/ogg$"
VIDEO_MIME_TYPES = r"^video/[a-zA-Z0-9-_]+$"

# celery
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
BROKER_DB = 0
BACKEND_DB = 1
STORAGE_DB = 2


class DBSettings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_host: str = "db"
    postgres_port: str = "5432"
    postgres_db: str = "audiobot"

    @property
    def connection_str(self) -> str:
        return f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"  # noqa: E501


db_settings = DBSettings()

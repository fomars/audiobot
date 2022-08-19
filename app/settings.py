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

# celery
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
BROKER_DB = 0
BACKEND_DB = 1
STORAGE_DB = 2


class AppSettings(BaseSettings):
    app_threads: int = 8
    audio_send_timeout: int = 60
    video_send_timeout: int = 300
    read_timeout: int = 300
    audio_size_limit: int = 350
    video_size_limit: int = 1000
    max_loudness: int = -7
    min_loudness: int = -24
    default_loudness: int = -14
    min_low_cut: int = 50
    max_low_cut: int = 150
    default_low_cut: int = 65
    audio_mime_types: str = r"^audio/[a-zA-Z0-9-_]+|application/ogg$"
    video_mime_types: str = r"^video/[a-zA-Z0-9-_]+$"
    lufs_rtfm_link: str = "https://en.wikipedia.org/wiki/Audio_normalization#Loudness_normalization"
    cutoff_rtfm_link: str = "https://en.wikipedia.org/wiki/Audio_filter"


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
app_settings = AppSettings()

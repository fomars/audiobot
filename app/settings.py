import os

DEBUG = bool(os.getenv('DEBUG'))
OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'app/output')
INPUT_DIR = os.getenv('INPUT_DIR', 'app/input')

# telegram
API_TOKEN = os.getenv('API_TOKEN')
TELEGRAM_API_URL = os.getenv('API_URL', 'https://api.telegram.org/bot')
LOCAL_API = bool(os.getenv('API_URL'))
API_WORKDIR = os.getenv('API_WORKDIR', '/var/lib/telegram-bot-api')

# s3
CLOUDCUBE_URL = os.environ['CLOUDCUBE_URL']
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

# ffmpeg
TARGET_LOUDNESS = int(os.getenv('TARGET_LOUDNESS', '-13'))

# celery
BROKER_URL = os.environ['REDIS_URL']
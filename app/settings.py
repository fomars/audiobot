import os

DEBUG = bool(os.getenv('DEBUG'))
OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'app/output')

# telegram
TOKEN = os.getenv('API_TOKEN')

# s3
CLOUDCUBE_URL = os.environ['CLOUDCUBE_URL']
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

# ffmpeg
TARGET_LOUDNESS = int(os.getenv('TARGET_LOUDNESS', '-13'))

# celery
BROKER_URL = os.environ['REDIS_URL']
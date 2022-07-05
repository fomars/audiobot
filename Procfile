bot: python main.py
celery_worker: celery -A tasks worker --loglevel=DEBUG
web: telegram-bot-api --http-port $PORT --dir=/var/lib/telegram-bot-api --temp-dir=/tmp/telegram-bot-api --username=telegram-bot-api --groupname=telegram-bot-api --local
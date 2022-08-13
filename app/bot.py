import logging

from telebot.storage import StateRedisStorage
from telebot import TeleBot, apihelper, logger
from app.middleware import AccountingMiddleware
from app import settings

if settings.DEBUG:
    logger.setLevel(logging.DEBUG)

state_storage = StateRedisStorage(
    host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.STORAGE_DB
)

apihelper.API_URL = settings.TELEGRAM_API_URL + "{0}/{1}"
bot = TeleBot(
    settings.API_TOKEN,
    state_storage=state_storage,
    num_threads=settings.APP_THREADS,
    use_class_middlewares=True
)
bot.setup_middleware(AccountingMiddleware())

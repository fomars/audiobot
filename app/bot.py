from telebot.storage import StateRedisStorage
from telebot import TeleBot, apihelper
from telebot.types import MenuButtonCommands, BotCommandScopeDefault

from app.commands import main_commands, bot_command_help
from app.middleware import PrepareUserData
from app import settings

state_storage = StateRedisStorage(
    host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.STORAGE_DB
)

apihelper.API_URL = settings.TELEGRAM_API_URL + "{0}/{1}"
apihelper.READ_TIMEOUT = settings.app_settings.read_timeout


bot = TeleBot(
    settings.API_TOKEN,
    state_storage=state_storage,
    num_threads=settings.app_settings.app_threads,
    use_class_middlewares=True,
)
bot.setup_middleware(PrepareUserData())

bot.set_my_commands(
    main_commands + [bot_command_help],
    BotCommandScopeDefault(),
)

bot.set_chat_menu_button(menu_button=MenuButtonCommands(type="commands"))

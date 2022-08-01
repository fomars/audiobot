from telebot.asyncio_handler_backends import BaseMiddleware

from app.models.user import UserDAL


class AccountingMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        self.update_types = ["message"]

    async def pre_process(self, message, data):
        await UserDAL.upsert_user(
            message.from_user.id,
            message.from_user.first_name,
            message.from_user.is_bot,
            message.from_user.username,
        )

    async def post_process(self, message, data, exception):
        pass

from telebot.handler_backends import BaseMiddleware
from app.models.user import UserDAL


class AccountingMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        self.update_types = ["message"]

    def pre_process(self, message, data):
        UserDAL.upsert_user(
            message.from_user.id,
            message.from_user.first_name,
            message.from_user.is_bot,
            message.from_user.username,
        )

    def post_process(self, message, data, exception):
        pass

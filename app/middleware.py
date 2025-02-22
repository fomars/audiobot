import re

from telebot.handler_backends import BaseMiddleware
from telebot.types import Audio

from app.settings import app_settings
from app.models.user import UserDAL


class PrepareUserData(BaseMiddleware):
    def __init__(self):
        super().__init__()
        self.update_types = ["message"]

    def pre_process(self, message, data):
        user = UserDAL.upsert_user(
            message.from_user.id,
            message.from_user.first_name,
            message.from_user.is_bot,
            message.from_user.username,
        )
        message.user_id = user.id
        message.user = user
        if message.document and re.fullmatch(
            app_settings.audio_mime_types, message.document.mime_type
        ):
            message.audio = Audio(
                message.document.file_id,
                message.document.file_unique_id,
                0,
                file_name=message.document.file_name,
                mime_type=message.document.mime_type,
                file_size=message.document.file_size,
            )
            message.content_type = "audio"

    def post_process(self, message, data, exception):
        pass

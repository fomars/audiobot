import os
import tempfile
from abc import ABC, abstractmethod
from urllib.request import urlretrieve

from app import settings


async def send_file(fpath, bot, message):
    if settings.LOCAL_API:
        file_uri = f'file:///{settings.API_WORKDIR}/output/{os.path.relpath(fpath, settings.OUTPUT_DIR)}'
        await bot.send_audio(
            message.chat.id,
            reply_to_message_id=message.id,
            audio=file_uri
        )
    else:
        with open(fpath, 'rb') as fileobj:
            await bot.send_audio(
                message.chat.id,
                reply_to_message_id=message.id,
                audio=(os.path.basename(fpath), fileobj)
            )


class BotFile(ABC):
    file_name: str

    @property
    @abstractmethod
    def path(self):
        ...

    @abstractmethod
    def remove(self):
        ...


class UserUploaded(BotFile):
    api_workdir = settings.API_WORKDIR
    bot_input_dir = settings.INPUT_DIR

    def __init__(self, file_info, file_name):
        self.file_name = file_name
        self.tg_file_path = file_info.file_path
        self._file_path = None

    @property
    def path(self):
        if self._file_path is None:
            if settings.LOCAL_API:
                self._file_path = self.tg_file_path.replace(self.api_workdir, self.bot_input_dir, 1)
            else:
                self._file_path = self.__download_user_file()
        return self._file_path

    def remove(self):
        if self._file_path is not None:
            os.remove(self._file_path)
            self._file_path = None

    def __download_user_file(self):
        file_url = f"{TELEGRAM_API_URL}/file/bot{API_TOKEN}/{self.tg_file_path}"
        fpath = os.path.join(tempfile.gettempdir(), self.file_name)
        urlretrieve(file_url, fpath)
        return fpath
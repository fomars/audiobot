import os
import tempfile
from abc import ABC, abstractmethod
from urllib.request import urlretrieve

from app.settings import LOCAL_API, API_TOKEN, TELEGRAM_API_URL,DEBUG


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
    api_base_dir = '/var/lib/telegram-bot-api'
    bot_base_dir = '/app/input'

    def __init__(self, file_info, file_name):
        self.file_name = file_name
        self.tg_file_path = file_info.file_path
        self._file_path = None

    @property
    def path(self):
        if self._file_path is None:
            if LOCAL_API:
                if DEBUG:
                    self._file_path = os.path.join('../mount', self.tg_file_path.strip('/'))
                else:
                    self._file_path = self.tg_file_path.replace(self.api_base_dir, self.bot_base_dir, 1)
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
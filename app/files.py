import os

from app import settings
from app.bot import bot


def send_file(fpath, chat_id, msg_id, filename, duration):
    if settings.LOCAL_API:
        file_uri = (
            f"file:///{settings.API_WORKDIR}/output/{os.path.relpath(fpath, settings.OUTPUT_DIR)}"
        )
        bot.send_audio(
            chat_id,
            reply_to_message_id=msg_id,
            audio=file_uri,
            title=filename,
            duration=duration,
        )
    else:
        with open(fpath, "rb") as fileobj:
            bot.send_audio(
                chat_id,
                reply_to_message_id=msg_id,
                audio=(os.path.basename(fpath), fileobj),
            )

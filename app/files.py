import os

from app import settings
from app.bot import bot


def send_audio(fpath, chat_id, msg_id, filename, duration):
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
                title=filename,
                duration=duration,
            )


def send_video(fpath, chat_id, msg_id, filename, duration, width, height):
    if settings.LOCAL_API:
        file_uri = (
            f"file:///{settings.API_WORKDIR}/output/{os.path.relpath(fpath, settings.OUTPUT_DIR)}"
        )
        bot.send_video(
            chat_id,
            reply_to_message_id=msg_id,
            video=file_uri,
            duration=duration,
            width=width,
            height=height,
        )
    else:
        with open(fpath, "rb") as fileobj:
            bot.send_video(
                chat_id,
                reply_to_message_id=msg_id,
                video=(os.path.basename(fpath), fileobj),
                duration=duration,
                width=width,
                height=height,
            )

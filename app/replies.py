import os

from app import settings
from app.bot import bot


def send_message(chat_id: int, text: str, reply_to_message_id: int = None):
    bot.send_message(
        chat_id,
        text,
        reply_to_message_id=reply_to_message_id,
    )


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
            allow_sending_without_reply=True,
            timeout=settings.app_settings.audio_send_timeout,
        )
    else:
        with open(fpath, "rb") as fileobj:
            bot.send_audio(
                chat_id,
                reply_to_message_id=msg_id,
                audio=(os.path.basename(fpath), fileobj),
                title=filename,
                duration=duration,
                allow_sending_without_reply=True,
                timeout=settings.app_settings.audio_send_timeout,
            )


def send_video(fpath, chat_id, msg_id, duration, width, height):
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
            allow_sending_without_reply=True,
            timeout=settings.app_settings.video_send_timeout,
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
                allow_sending_without_reply=True,
                timeout=settings.app_settings.video_send_timeout,
            )


def send_document(fpath, chat_id, msg_id, filename):
    file_uri = (
        f"file:///{settings.API_WORKDIR}/output/{os.path.relpath(fpath, settings.OUTPUT_DIR)}"
    )
    bot.send_document(
        chat_id,
        file_uri,
        reply_to_message_id=msg_id,
        timeout=settings.app_settings.video_send_timeout,
        allow_sending_without_reply=True,
        visible_file_name=filename,
    )

import os
import os.path
import time

import youtube_dl
from youtube_dl import DownloadError
import logging

from app import settings
from app.bot import bot
from app.tasks import make_it_loud, make_video_loud, process_streaming_audio

logger = logging.getLogger()


@bot.message_handler(func=lambda message: message.from_user.is_bot)
def filter_bots(message):
    pass


@bot.message_handler(commands=["help", "start"])
def send_welcome(message):
    bot.reply_to(
        message,
        f"""\
Hi there, I am here to make your audio loud!
I can make your vlog / podcast / mixtape evenly loud throughout its duration.
I make the overall loudness to match -14 dB LUFS by default, \
but you can set the target loudness between [{settings.MIN_LOUDNESS}, {settings.MAX_LOUDNESS}], \
just send me the number!
Or simply send me your audio file and see how it works!
""",
    )


@bot.message_handler(content_types=["audio"])
def handle_audio(message):
    audio = message.audio

    if audio.file_size / 1024 / 1024 > 350:
        return bot.reply_to(message, "File size limit exceeded (350M)")
    else:
        bot.reply_to(message, "Downloading file")
        file_info = bot.get_file(audio.file_id)
        logger.info(f"file from {message.from_user}\ninfo: {file_info}")
        target_loudness = (
            bot.get_state(message.from_user.id, message.chat.id) or settings.DEFAULT_LOUDNESS
        )
        bot.reply_to(
            message,
            f"Audio is being processed, target loudness: {target_loudness} LUFS",
        )
        try:
            duration = audio.duration
        except AttributeError:
            duration = None
        make_it_loud.delay(
            file_info.file_path,
            target_loudness,
            duration,
            message.chat.id,
            message.id,
            audio.file_name,
        )


@bot.message_handler(content_types=["video"])
def handle_video(message):
    video = message.video
    if video.file_size / 1024 / 1024 > 1200:
        return bot.reply_to(message, "File size limit exceeded (1200M)")
    else:
        bot.reply_to(message, "Downloading file")
        file_info = bot.get_file(video.file_id)
        logger.info(f"file from {message.from_user}\ninfo: {file_info}")
        target_loudness = (
            bot.get_state(message.from_user.id, message.chat.id) or settings.DEFAULT_LOUDNESS
        )
        bot.reply_to(
            message,
            f"Video is being processed, target loudness: {target_loudness} LUFS\nCaution: Preview"
            " size might be distorted/cropped. Expand fullscreen or download for proper view.",
        )
        try:
            duration = video.duration
        except AttributeError:
            duration = None
        make_video_loud.delay(
            file_info.file_path,
            target_loudness,
            duration,
            message.chat.id,
            message.id,
            video.file_name,
            video.width,
            video.height,
        )


@bot.message_handler(func=lambda message: message.entities)
def process_link(message):
    if len(message.entities) > 1:
        bot.reply_to(message, "Send only one URL")
    else:
        entity = message.entities[0]
        if entity.type != "url":
            bot.reply_to(message, "Send a valid URL")
        else:
            url = message.text[entity.offset : entity.offset + entity.length]  # noqa: E203
            try:
                with youtube_dl.YoutubeDL() as ydl:
                    info = ydl.extract_info(url, download=False)
                    title = info.get("title", "untitled")
                bot.reply_to(
                    message,
                    f"Audio is being processed\nDuration: {info.get('duration')}",
                )

                result = process_streaming_audio.delay(url, title)
                delay = 0.1
                while not result.ready():
                    time.sleep(delay)
                    delay = min(delay * 1.2, 2)
                output_fpath = result.get()
                with open(output_fpath, "rb") as fileobj:
                    bot.send_audio(
                        message.chat.id,
                        reply_to_message_id=message.id,
                        audio=(os.path.basename(output_fpath), fileobj),
                    )
            except DownloadError:
                bot.reply_to(message, "Media not found")


@bot.message_handler(func=lambda message: True)
def set_loudness(message):
    try:
        loudness = int(message.text)
        assert settings.MIN_LOUDNESS <= loudness <= settings.MAX_LOUDNESS
    except (ValueError, AssertionError):
        bot.reply_to(
            message,
            f"Enter loudness between [{settings.MIN_LOUDNESS}, {settings.MAX_LOUDNESS}]"
            " LUFS, or just send an audio to render at default"
            f" {settings.DEFAULT_LOUDNESS} LUFS",
        )
    else:
        bot.set_state(message.from_user.id, str(loudness), message.chat.id)
        bot.reply_to(message, f"Target loudness is set to {loudness} LUFS")


@bot.message_handler(
    content_types=[
        "animation",
        "document",
        "photo",
        "sticker",
        "video_note",
        "voice",
        "contact",
        "dice",
        "poll",
        "venue",
        "location",
    ]
)
def undefined(message):
    bot.reply_to(message, "Send media file.")

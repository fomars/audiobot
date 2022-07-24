import asyncio
import os.path

import youtube_dl
from telebot.asyncio_storage import StateRedisStorage
from youtube_dl import DownloadError
from telebot.async_telebot import AsyncTeleBot
from telebot import asyncio_helper
import telebot
import logging

from app import settings
from app.files import UserUploaded, send_file
from app.tasks import make_it_loud, process_streaming_audio


logger = telebot.logger
if settings.DEBUG:
    logger.setLevel(logging.DEBUG)

state_storage = StateRedisStorage(
    host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.STORAGE_DB
)

asyncio_helper.API_URL = settings.TELEGRAM_API_URL + "{0}/{1}"
bot = AsyncTeleBot(settings.API_TOKEN, state_storage=state_storage)


@bot.message_handler(func=lambda message: message.from_user.is_bot)
async def filter_bots(message):
    pass


@bot.message_handler(commands=["help", "start"])
async def send_welcome(message):
    await bot.reply_to(
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
async def process_audio(message):
    if message.audio.file_size / 1024 / 1024 > 350:
        await bot.reply_to(message, "File size limit exceeded")
    else:
        await bot.reply_to(message, "Downloading file")
        file_info = await bot.get_file(message.audio.file_id)
        file = UserUploaded(file_info, message.audio.file_name)
        target_loudness = await bot.get_state(message.from_user.id, message.chat.id) or settings.DEFAULT_LOUDNESS
        await bot.reply_to(
            message,
            f"Audio is being processed, target loudness: {target_loudness} LUFS",
        )

        result = make_it_loud.delay(file.path, target_loudness)
        delay = 0.1
        while not result.ready():
            await asyncio.sleep(delay)
            delay = min(delay * 1.2, 3)
        output_fpath = result.get()
        file.remove()

        await send_file(output_fpath, bot, message)


@bot.message_handler(func=lambda message: message.entities)
async def process_link(message):
    if len(message.entities) > 1:
        await bot.reply_to(message, "Send only one URL")
    else:
        entity = message.entities[0]
        if entity.type != "url":
            await bot.reply_to(message, "Send a valid URL")
        else:
            url = message.text[entity.offset: entity.offset + entity.length]
            try:
                with youtube_dl.YoutubeDL() as ydl:
                    info = ydl.extract_info(url, download=False)
                    title = info.get("title", "untitled")
                await bot.reply_to(
                    message,
                    f"Audio is being processed\nDuration: {info.get('duration')}",
                )

                result = process_streaming_audio.delay(url, title)
                delay = 0.1
                while not result.ready():
                    await asyncio.sleep(delay)
                    delay = min(delay * 1.2, 2)
                output_fpath = result.get()
                with open(output_fpath, "rb") as fileobj:
                    await bot.send_audio(
                        message.chat.id,
                        reply_to_message_id=message.id,
                        audio=(os.path.basename(output_fpath), fileobj),
                    )
            except DownloadError:
                await bot.reply_to(message, "Media not found")


@bot.message_handler(func=lambda message: True)
async def set_loudness(message):
    try:
        loudness = int(message.text)
        assert settings.MIN_LOUDNESS <= loudness <= settings.MAX_LOUDNESS
    except (ValueError, AssertionError):
        await bot.reply_to(
            message,
            f"Enter loudness between [{settings.MIN_LOUDNESS}, {settings.MAX_LOUDNESS}]"
            " LUFS, or just send an audio to render at default"
            f" {settings.DEFAULT_LOUDNESS} LUFS",
        )
    else:
        await bot.set_state(message.from_user.id, str(loudness), message.chat.id)
        await bot.reply_to(message, f"Target loudness is set to {loudness} LUFS")

import asyncio
import os.path
import youtube_dl
from youtube_dl import DownloadError
from telebot.async_telebot import AsyncTeleBot
import telebot
import logging

from app import settings
from app.tasks import make_it_loud, process_streaming_audio


logger = telebot.logger
if settings.DEBUG:
    logger.setLevel(logging.DEBUG)

bot = AsyncTeleBot(settings.TOKEN)


@bot.message_handler(commands=['help', 'start'])
async def send_welcome(message):
    await bot.reply_to(message, """\
Hi there, I am here to make your audio loud! 
I can make your vlog / podcast / mixtape evenly loud throughout its duration.
I make the overall loudness to match -14 dB LUFS according to the ITU 1770 standard.
Just send me your audio file to see how it works!
""")


@bot.message_handler(content_types=['audio'])
async def process_audio(message):
    if message.audio.file_size/1024/1024 > 20:
        await bot.reply_to(message, "File size limit exceeded")
    else:
        file_info = await bot.get_file(message.audio.file_id)
        file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"
        filename = message.audio.file_name
        await bot.reply_to(message, "Audio is being processed")

        result = make_it_loud.delay(file_url, filename)
        delay = 0.1
        while not result.ready():
            await asyncio.sleep(delay)
            delay = min(delay * 1.2, 2)
        output_fpath = result.get()

        with open(output_fpath, 'rb') as fileobj:
            await bot.send_audio(
                message.chat.id,
                reply_to_message_id=message.id,
                audio=(os.path.basename(output_fpath), fileobj)
            )
        os.remove(output_fpath)


@bot.message_handler(func=lambda message: message.entities)
async def process_link(message):
    if len(message.entities) > 1:
        await bot.reply_to(message, 'Send only one URL')
    else:
        entity = message.entities[0]
        if entity.type != 'url':
            await bot.reply_to(message, 'Send a valid URL')
        else:
            url = message.text[entity.offset:entity.offset+entity.length]
            try:
                with youtube_dl.YoutubeDL() as ydl:
                    info = ydl.extract_info(url, download=False)
                    title = info.get('title', 'untitled')
                await bot.reply_to(message, f"Audio is being processed\nDuration: {info.get('duration')}")

                result = process_streaming_audio.delay(url, title)
                delay = 0.1
                while not result.ready():
                    await asyncio.sleep(delay)
                    delay = min(delay * 1.2, 2)
                output_fpath = result.get()
                with open(output_fpath, 'rb') as fileobj:
                    await bot.send_audio(
                        message.chat.id,
                        reply_to_message_id=message.id,
                        audio=(os.path.basename(output_fpath), fileobj)
                    )
            except DownloadError:
                await bot.reply_to(message, 'Media not found')


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
async def echo_message(message):
    await bot.reply_to(message, message.text)

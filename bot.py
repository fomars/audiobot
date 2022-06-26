import asyncio
import os.path

import settings
from telebot.async_telebot import AsyncTeleBot
import telebot
import logging

from s3 import download
from tasks import make_it_loud

logger = telebot.logger
if settings.DEBUG:
    logger.setLevel(logging.DEBUG)

bot = AsyncTeleBot(settings.TOKEN)


@bot.message_handler(commands=['help', 'start'])
async def send_welcome(message):
    await bot.reply_to(message, """\
Hi there, I am EchoBot.
I am here to echo your kind words back to you. Just say anything nice and I'll say the exact same thing to you!\
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
            delay = min(delay * 1.2, 1)
        processed_s3_key = result.get()
        output_fpath = download(processed_s3_key)

        with open(output_fpath, 'rb') as fileobj:
            await bot.send_audio(
                message.chat.id,
                reply_to_message_id=message.id,
                audio=(os.path.basename(output_fpath), fileobj)
            )
        os.remove(output_fpath)
        # f"""Received audio file
        # name: {message.audio.file_name}
        # size: {message.audio.file_size/1024/1024} MB
        # mime_type: {message.audio.mime_type}
        # file_id: {message.audio.file_id}
        # file_unique_id: {message.audio.file_unique_id}"""


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
async def echo_message(message):
    await bot.reply_to(message, message.text)

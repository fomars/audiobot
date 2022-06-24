import settings
from telebot.async_telebot import AsyncTeleBot
import telebot
import logging

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


@bot.message_handler(content_types=['audio', 'voice'])
async def process_audio(message):
    await bot.reply_to(message, f"""Received audio file
    name: {message.audio.file_name}
    size: {message.audio.file_size/1024/1024} MB
    mime_type: {message.audio.mime_type}""")


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
async def echo_message(message):
    await bot.reply_to(message, message.text)

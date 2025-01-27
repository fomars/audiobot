import re
import logging

from telebot import formatting
from telebot.types import (
    ReplyKeyboardMarkup,
    BotCommandScopeChat,
    MenuButtonCommands,
    ReplyKeyboardRemove,
)
from telebot.util import extract_arguments

from app.commands import (
    MainCommands,
    UtilityCommands,
    main_commands,
    bot_command_start,
    bot_command_low_cut,
    bot_command_loudness,
)
from app.settings import app_settings
from app.bot import bot
from app.tasks import process_audio, process_video

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def reset_menu(chat_id, commands=None, start=True):
    commands = commands + [bot_command_start] * start if commands else [bot_command_start]
    bot.set_my_commands(
        commands,
        BotCommandScopeChat(chat_id),
    )
    bot.set_chat_menu_button(menu_button=MenuButtonCommands(type="commands"))


@bot.message_handler(func=lambda message: message.from_user.is_bot)
def filter_bots(message):
    pass


@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reset_data(message.from_user.id)
    bot.delete_state(message.from_user.id)
    reset_menu(message.chat.id, commands=main_commands, start=False)
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=1)
    choices = [f"/{command.value}" for command in MainCommands]
    markup.add(*choices)
    bot.reply_to(
        message,
        "Hi there, I am here to make your audio/video loud!\n"
        "I can make your vlog / podcast / mixtape evenly loud throughout its duration.\n"
        "1. Choose an action from menu.\n"
        "2. Set the parameters if necessary.\n"
        "3. Send your media file.\n"
        "4. Kindly wait. Processing audio file usually takes 1/5 of its duration; "
        "video processing takes about 100% of video duration.\n"
        "! Limitations:\n"
        f"Audio file size: {app_settings.audio_size_limit}MB\n"
        f"Video file size: {app_settings.video_size_limit}MB",
        reply_markup=markup,
    )


@bot.message_handler(commands=["help"])
def show_help(message):
    bot.reply_to(
        message,
        "1. Choose an action from menu.\n"
        "2. Set the parameters if necessary.\n"
        "3. Send your media file.\n"
        "4. Kindly wait. Processing audio file usually takes 1/5 of its duration; "
        "video processing takes about 100% of video duration.\n"
        "! Limitations:\n"
        f"Audio file size: {app_settings.audio_size_limit}MB\n"
        f"Video file size: {app_settings.video_size_limit}MB",
    )


@bot.message_handler(
    commands=[UtilityCommands.loudness.value], func=lambda msg: not extract_arguments(msg.text)
)
def set_loudness(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=3)
    choices = [
        f"/{UtilityCommands.loudness.value} {i}"
        for i in range(app_settings.min_loudness, app_settings.max_loudness, 2)
    ]
    markup.add(*choices)

    msg_text = formatting.format_text(
        formatting.escape_markdown("Select target loudness in "),
        formatting.mlink("LUFS", url=app_settings.lufs_rtfm_link),
        formatting.escape_markdown(" (Recommended: -18~-14)"),
        separator="",
    )
    bot.send_message(
        message.chat.id,
        msg_text,
        parse_mode="MarkdownV2",
        disable_web_page_preview=True,
        reply_markup=markup,
    )


@bot.message_handler(
    commands=[UtilityCommands.loudness.value], func=lambda msg: extract_arguments(msg.text)
)
def set_loudness_(message):
    value = extract_arguments(message.text)
    try:
        loudness = int(value)
        assert app_settings.min_loudness <= loudness <= app_settings.max_loudness
    except (ValueError, AssertionError):
        msg_text = formatting.format_text(
            formatting.escape_markdown(
                f"Set loudness between [{app_settings.min_loudness}, {app_settings.max_loudness}] "
            ),
            formatting.mlink("LUFS", url=app_settings.lufs_rtfm_link),
            separator="",
        )
        bot.reply_to(
            message,
            text=msg_text,
            parse_mode="MarkdownV2",
            disable_web_page_preview=True,
        )
    else:
        bot.add_data(message.from_user.id, message.chat.id, loudness=loudness)
        bot.reply_to(
            message,
            f"Target loudness is set at {loudness} LUFS",
            reply_markup=ReplyKeyboardRemove(),
        )


@bot.message_handler(
    commands=[UtilityCommands.low_cut.value], func=lambda msg: not extract_arguments(msg.text)
)
def set_low_cut(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=3)
    choices = [
        f"/{UtilityCommands.low_cut.value} {i}"
        for i in range(app_settings.min_low_cut, app_settings.max_low_cut + 1, 10)
    ]
    markup.add(*choices)
    bot.send_message(
        message.chat.id,
        "Select low cut frequency (recommended: 60-90Hz)",
        reply_markup=markup,
    )


@bot.message_handler(
    commands=[UtilityCommands.low_cut.value], func=lambda msg: extract_arguments(msg.text)
)
def set_low_cut_(message):
    value = extract_arguments(message.text)
    try:
        low_cut = int(value)
        assert app_settings.min_low_cut <= low_cut <= app_settings.max_low_cut
    except (ValueError, AssertionError):
        bot.reply_to(
            message,
            f"Set low cut between [{app_settings.min_low_cut}, {app_settings.max_low_cut}] Hz, or"
            f" just send an audio to render with default cut at {app_settings.default_low_cut} Hz",
        )
    else:
        bot.add_data(message.from_user.id, message.chat.id, low_cut=low_cut)
        bot.reply_to(
            message, f"Low cut frequency is set at {low_cut} Hz", reply_markup=ReplyKeyboardRemove()
        )


@bot.message_handler(commands=[MainCommands.make_it_loud.value])
def make_it_loud(message):
    bot.set_state(message.from_user.id, MainCommands.make_it_loud.value, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as user_data:
        loudness = user_data.get("loudness", app_settings.default_loudness)

    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=1)
    markup.add(f"/{UtilityCommands.loudness.value}")

    msg_text = formatting.format_text(
        formatting.escape_markdown(
            f"We are going to render your audio at target loudness of {loudness} "
        ),
        formatting.mlink("LUFS", url=app_settings.lufs_rtfm_link),
        formatting.escape_markdown(
            "\nTo change target loudness, use"
            f" command:\n/{UtilityCommands.loudness.value} [value]\nTo continue, send your media"
            " file."
        ),
        separator="",
    )
    bot.send_message(
        message.chat.id,
        text=msg_text,
        parse_mode="MarkdownV2",
        disable_web_page_preview=True,
        reply_markup=markup,
    )
    reset_menu(message.chat.id, [bot_command_loudness])


@bot.message_handler(commands=[MainCommands.small_speakers.value])
def small_speakers(message):
    bot.set_state(message.from_user.id, MainCommands.small_speakers.value, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as user_data:
        loudness = user_data.get("loudness", app_settings.default_loudness)
        low_cut = user_data.get("low_cut", app_settings.default_low_cut)

    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=1)
    markup.add(f"/{UtilityCommands.loudness.value}", f"/{UtilityCommands.low_cut.value}")

    msg_text = formatting.format_text(
        formatting.escape_markdown(
            f"We are going to render your audio at target loudness of: {loudness} "
        ),
        formatting.mlink("LUFS", url=app_settings.lufs_rtfm_link),
        formatting.escape_markdown(
            f"\nLow cut frequency: {low_cut} Hz\n"
            "To render at these settings, send media file.\n"
            "To change settings, use corresponding commands and then send file:\n"
            f"/{UtilityCommands.loudness.value} [value]\n"
            f"/{UtilityCommands.low_cut.value} [value]",
        ),
        separator="",
    )

    bot.send_message(
        message.chat.id,
        text=msg_text,
        parse_mode="MarkdownV2",
        disable_web_page_preview=True,
        reply_markup=markup,
    )
    reset_menu(message.chat.id, [bot_command_loudness, bot_command_low_cut])


@bot.message_handler(commands=[MainCommands.enhance_speech.value])
def enhance_speech(message):
    bot.set_state(message.from_user.id, MainCommands.enhance_speech.value, message.chat.id)
    bot.send_message(
        message.chat.id,
        "Send your audio/video file.\nTo preserve video quality, send it as document.\nIf video is"
        " too big, it is recommended to extract audio with a third-party tool and send only it.",
        reply_markup=ReplyKeyboardRemove(),
    )
    reset_menu(message.chat.id)


@bot.message_handler(content_types=["audio"])
def handle_audio(message):
    audio = message.audio
    if audio.file_size / 1024 / 1024 > app_settings.audio_size_limit:
        return bot.reply_to(
            message, f"Audio size limit exceeded ({app_settings.audio_size_limit}M)"
        )
    algorithm = (
        bot.get_state(message.from_user.id, message.chat.id) or MainCommands.make_it_loud.value
    )
    with bot.retrieve_data(message.from_user.id, message.chat.id) as user_data:
        kwargs = user_data or {}
    bot.reply_to(message, "Downloading file", reply_markup=ReplyKeyboardRemove())
    file_info = bot.get_file(audio.file_id)
    logger.info(
        f"file from {message.from_user}\n"
        f"info: {file_info}\n"
        f"algorithm: {algorithm}\n"
        f"kwargs: {kwargs}"
    )
    bot.reply_to(
        message,
        "Audio is being processed.",
    )
    process_audio.delay(
        file_info.file_path,
        algorithm,
        kwargs,
        message.chat.id,
        message.id,
        message.user_id,
        audio.file_name,
    )
    reset_menu(message.chat.id, commands=main_commands)


@bot.message_handler(content_types=["video", "document"])
def handle_video(message):
    if message.video:
        video = message.video
    elif re.fullmatch(app_settings.video_mime_types, message.document.mime_type):
        video = message.document
    else:
        return bot.reply_to(message, "Unsupported media type")

    if video.file_size / 1024 / 1024 > app_settings.video_size_limit:
        return bot.reply_to(
            message, f"Video size limit exceeded ({app_settings.video_size_limit}M)"
        )
    algorithm = (
        bot.get_state(message.from_user.id, message.chat.id) or MainCommands.make_it_loud.value
    )
    with bot.retrieve_data(message.from_user.id, message.chat.id) as user_data:
        kwargs = user_data or {}
    bot.reply_to(message, "Downloading file", reply_markup=ReplyKeyboardRemove())
    file_info = bot.get_file(video.file_id)
    logger.info(
        f"file from {message.from_user}\n"
        f"info: {file_info}\n"
        f"algorithm: {algorithm}\n"
        f"kwargs: {kwargs}"
    )
    bot.reply_to(
        message,
        "Video is being processed.",
    )
    process_video.delay(
        file_info.file_path,
        algorithm,
        kwargs,
        message.chat.id,
        message.id,
    )
    reset_menu(message.chat.id, commands=main_commands)


@bot.message_handler(
    content_types=[
        "animation",
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
    bot.reply_to(message, "Unsupported media type")


@bot.message_handler(
    commands=[MainCommands.balance_info.value]
)
def balance_info(message):
    bot.reply_to(
        message,
        f"Your balance: {message.user.balance_seconds} seconds",
    )


@bot.message_handler(
    commands=[MainCommands.balance_top_up.value]
)
def send_top_up_link(message):
    bot.reply_to(
        message,
        "Top up your balance here: https://t.me/tribute/app?startapp=pbS6",
    )
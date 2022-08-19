from telebot.types import BotCommand
from enum import Enum


class MainCommands(Enum):
    make_it_loud = "make_it_loud"
    enhance_speech = "enhance_speech"
    small_speakers = "small_speakers"

    def _missing_(cls, value: object):
        return cls.make_it_loud


class UtilityCommands(Enum):
    loudness = "loudness"
    low_cut = "low_cut"
    start = "start"


bot_command_start = BotCommand(UtilityCommands.start.value, "Start over")
bot_command_loudness = BotCommand(UtilityCommands.loudness.value, "Set target loudness")
bot_command_low_cut = BotCommand(UtilityCommands.low_cut.value, "Set low cut frequency")

menu_commands = [
    BotCommand(
        MainCommands.make_it_loud.value,
        "Make your audio evenly loud",
    ),
    BotCommand(
        MainCommands.enhance_speech.value,
        "Emphasize your speech and make it evenly loud. Good for vlog, podcast, etc.",
    ),
    BotCommand(
        MainCommands.small_speakers.value,
        "Optimise audio for your portable speaker and increase its loudness.",
    ),
]

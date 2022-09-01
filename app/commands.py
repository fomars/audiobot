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
    help = "help"


bot_command_start = BotCommand(UtilityCommands.start.value, "Start over")
bot_command_help = BotCommand(UtilityCommands.help.value, "Help")
bot_command_loudness = BotCommand(UtilityCommands.loudness.value, "Set target loudness")
bot_command_low_cut = BotCommand(UtilityCommands.low_cut.value, "Set low cut frequency")

main_commands = [
    BotCommand(
        MainCommands.make_it_loud.value,
        "Make your audio evenly loud",
    ),
    BotCommand(
        MainCommands.enhance_speech.value,
        "Use for vlog, podcast, etc. Emphasizes speech and makes it evenly loud.",
    ),
    BotCommand(
        MainCommands.small_speakers.value,
        "Optimise for portable speaker and increase loudness.",
    ),
]

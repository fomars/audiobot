from telebot.types import BotCommand


commands = [
    BotCommand(
        "adjust_loudness",
        "This will dynamically modify the loudness of your audio making it evenly loud throughout"
        " its duration.",
    ),
    BotCommand(
        "enhance_speech",
        "This will remove unwanted frequencies, bring your speech to the front and make it evenly"
        " loud. Good for vlog, podcast, etc.",
    ),
    BotCommand(
        "optimise_for_small_speaker",
        "This will optimise frequency range for small speakers and increase audio loudness.",
    ),
]

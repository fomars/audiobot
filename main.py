from app.handlers import bot

if __name__ == "__main__":
    bot.infinity_polling(allowed_updates=["message"])

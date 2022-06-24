from bot import bot

if __name__ == "__main__":
    import asyncio
    asyncio.run(bot.infinity_polling())
    # bot.infinity_polling()
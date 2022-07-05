from app.bot import bot

if __name__ == "__main__":
    import asyncio
    asyncio.run(bot.infinity_polling())
from telethon import TelegramClient
from config import API_ID, API_HASH, BOT_TOKEN
from utils.database import engine
from utils.base import Base
from common.handlers import setup_common_handlers
from progress.handlers import setup_progress_handlers



Base.metadata.create_all(engine)
bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Імпортуємо setup-функції для авторизації та тестування
from auth.handlers import setup_auth_handlers
from testing.handlers import setup_testing_handlers
import asyncio

async def setup_handlers():
    await setup_auth_handlers(bot)
    await setup_testing_handlers(bot)
    await setup_common_handlers(bot)
    await setup_progress_handlers(bot)

bot.loop.run_until_complete(setup_handlers())

def main():
    print("🤖 Бот запущений...")
    bot.run_until_disconnected()

if __name__ == '__main__':
    main()

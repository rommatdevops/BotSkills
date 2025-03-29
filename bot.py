from telethon import TelegramClient, events, Button
from config import API_ID, API_HASH, BOT_TOKEN
from auth.auth import register_user, check_authorization, authorize_user
from auth.models import Base
from utils.database import engine
from sqlalchemy import text

Base.metadata.create_all(engine)

bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

WELCOME_TEXT = (
    "👋 Вітаю!\n\n"
    "Це бот, який допоможе вам отримати нові знання та трохи розважитися.\n"
    "Щоб почати, натисніть /start"
)

MENU_BUTTON = [
    [Button.text("📌 Очікуйте оновлень", resize=True)]
]

REGISTRATION_BUTTONS = [
    [Button.text("✅ Зареєструватися", resize=True), Button.text("❌ Відмовитися", resize=True)]
]

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    telegram_id = event.sender_id
    username = event.sender.username
    full_name = f"{event.sender.first_name or ''} {event.sender.last_name or ''}".strip()

    session = engine.connect()
    result = session.execute(
        text("SELECT is_authorized FROM users WHERE telegram_id = :telegram_id"),
        {"telegram_id": telegram_id}
    ).scalar()
    session.close()

    if result:
        await event.reply(
            "🔹 Ви вже зареєстровані! Оберіть пункт із меню.",
            buttons=MENU_BUTTON
        )
    else:
        await event.reply(
            "🤔 Ви ще не зареєстровані. Хочете зареєструватись?",
            buttons=REGISTRATION_BUTTONS
        )

@bot.on(events.NewMessage(pattern='✅ Зареєструватися'))
async def register(event):
    telegram_id = event.sender_id
    username = event.sender.username
    full_name = f"{event.sender.first_name or ''} {event.sender.last_name or ''}".strip()

    if not check_authorization(telegram_id):
        register_user(telegram_id, username, full_name)
        authorize_user(telegram_id)  # Встановлюємо is_authorized=True
        await event.reply(
            "✅ Ви успішно зареєстровані! Дякую, що приєдналися.",
            buttons=MENU_BUTTON
        )
    else:
        await event.reply("🔹 Ви вже зареєстровані.", buttons=MENU_BUTTON)

@bot.on(events.NewMessage(pattern='❌ Відмовитися'))
async def decline_registration(event):
    await event.reply("🚫 Ви відмовились від реєстрації. Якщо передумаєте, натисніть /start")

@bot.on(events.NewMessage(pattern='📌 Очікуйте оновлень'))
async def updates(event):
    await event.reply("🕑 Незабаром тут з'являться нові можливості. Слідкуйте за оновленнями!")

@bot.on(events.NewMessage(func=lambda e: e.is_private and e.text != '/start' 
                          and e.text not in ['✅ Зареєструватися', '❌ Відмовитися', '📌 Очікуйте оновлень']))
async def greet_if_first_time(event):
    await event.reply(WELCOME_TEXT)

def main():
    print("🤖 Бот запущений...")
    bot.run_until_disconnected()

if __name__ == '__main__':
    main()

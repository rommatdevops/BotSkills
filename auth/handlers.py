# auth/handlers.py
from telethon import events, Button
from auth.auth import register_user, authorize_user, check_authorization
from utils.database import SessionLocal
from sqlalchemy import text

async def setup_auth_handlers(bot_client):
    @bot_client.on(events.NewMessage(pattern='/start'))
    async def start_handler(event):
        telegram_id = event.sender_id
        username = event.sender.username
        full_name = f"{event.sender.first_name or ''} {event.sender.last_name or ''}".strip()

        session = SessionLocal()
        result = session.execute(
            text("SELECT is_authorized FROM users WHERE telegram_id = :telegram_id"),
            {"telegram_id": telegram_id}
        ).scalar()
        session.close()

        if result:
            await event.reply(
                "🔹 Ви вже зареєстровані! Оберіть пункт із меню.",
                buttons=[
                    [Button.text("🧪 Тестування", resize=True)],
                    [Button.text("📈 Мій прогрес", resize=True)],
                    [Button.text("📌 Очікуйте оновлень", resize=True)]
                ]
            )
        else:
            await event.reply(
                "🤔 Ви ще не зареєстровані. Хочете зареєструватись?",
                buttons=[
                    [Button.text("✅ Зареєструватися", resize=True),
                     Button.text("❌ Відмовитися", resize=True)]
                ]
            )

    @bot_client.on(events.NewMessage(pattern='✅ Зареєструватися'))
    async def register_handler(event):
        telegram_id = event.sender_id
        username = event.sender.username
        full_name = f"{event.sender.first_name or ''} {event.sender.last_name or ''}".strip()

        if not check_authorization(telegram_id):
            register_user(telegram_id, username, full_name)
            authorize_user(telegram_id)
            await event.reply(
                "✅ Ви успішно зареєстровані! Дякую, що приєдналися.",
                buttons=[
                    [Button.text("🧪 Тестування", resize=True)],
                    [Button.text("📈 Мій прогрес", resize=True)],
                    [Button.text("📌 Очікуйте оновлень", resize=True)]
                ]
            )
        else:
            await event.reply(
                "🔹 Ви вже зареєстровані.",
                buttons=[
                    [Button.text("🧪 Тестування", resize=True)],
                    [Button.text("📈 Мій прогрес", resize=True)],
                    [Button.text("📌 Очікуйте оновлень", resize=True)]
                ]
            )

    @bot_client.on(events.NewMessage(pattern='❌ Відмовитися'))
    async def decline_registration(event):
        await event.reply("🚫 Ви відмовились від реєстрації. Якщо передумаєте, натисніть /start")

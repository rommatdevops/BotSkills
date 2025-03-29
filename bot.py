import random
from telethon import TelegramClient, events, Button
from config import API_ID, API_HASH, BOT_TOKEN
from sqlalchemy import text
from auth.auth import register_user, check_authorization, authorize_user
from testing.test_logic import get_test_categories, get_random_question
from testing.models import TestCategory, Test, Question, Answer  # ← додано імпорт моделей
#---Імпорт бази-----
from utils.base import Base
from utils.database import engine, SessionLocal

#-------------------
Base.metadata.create_all(engine)



bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

WELCOME_TEXT = (
    "👋 Вітаю!\n\n"
    "Це бот, який допоможе вам отримати нові знання та трохи розважитися.\n"
    "Щоб почати, натисніть /start"
)

MAIN_MENU_BUTTONS = [
    [Button.text("🧪 Тестування", resize=True)],
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
            buttons=MAIN_MENU_BUTTONS
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
            buttons=MAIN_MENU_BUTTONS
        )
    else:
        await event.reply("🔹 Ви вже зареєстровані.", buttons=MAIN_MENU_BUTTONS)

@bot.on(events.NewMessage(pattern='❌ Відмовитися'))
async def decline_registration(event):
    await event.reply("🚫 Ви відмовились від реєстрації. Якщо передумаєте, натисніть /start")

@bot.on(events.NewMessage(pattern='📌 Очікуйте оновлень'))
async def updates(event):
    await event.reply("🕑 Незабаром тут з'являться нові можливості. Слідкуйте за оновленнями!")

# @bot.on(events.NewMessage(func=lambda e: e.is_private and e.text != '/start' 
#                           and e.text not in ['✅ Зареєструватися', '❌ Відмовитися', '📌 Очікуйте оновлень']))
# async def greet_if_first_time(event):
#     await event.reply(WELCOME_TEXT)

@bot.on(events.NewMessage(pattern='🧪 Тестування'))
async def testing_menu(event):
    categories = get_test_categories()
    if not categories:
        await event.reply("😕 Наразі немає жодного доступного тесту.")
        return
    
    buttons = [[Button.text(cat.name, resize=True)] for cat in categories]
    await event.reply("📚 Оберіть тему для тестування:", buttons=buttons)

@bot.on(events.NewMessage)
async def handle_category_selection(event):
    session = SessionLocal()
    category = session.query(TestCategory).filter(TestCategory.name == event.text).first()
    if category:
        tests = session.query(Test).filter(Test.category_id == category.id).all()
        if not tests:
            await event.reply("😕 В обраній темі немає тестів.")
            session.close()
            return
        
        test = random.choice(tests)
        question = get_random_question(test.id)
        if question:
            buttons = [[Button.text(ans.answer_text, resize=True)] for ans in question.answers]
            await event.reply(f"❓ {question.question_text}", buttons=buttons)
        else:
            await event.reply("😕 В тесті немає питань.")
    session.close()


def main():
    print("🤖 Бот запущений...")
    bot.run_until_disconnected()

if __name__ == '__main__':
    main()

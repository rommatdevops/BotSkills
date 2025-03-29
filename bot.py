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
            # Створюємо інлайн-кнопки замість звичайних кнопок текстового меню
            # Для кожної відповіді додаємо її id як callback_data
            buttons = [
                [Button.inline(ans.answer_text, data=f"answer_{ans.id}")]
                for ans in question.answers
            ]
            
            # Зберігаємо id питання для перевірки відповіді
            await event.reply(
                f"❓ {question.question_text}", 
                buttons=buttons
            )
        else:
            await event.reply("😕 В тесті немає питань.")
    session.close()

@bot.on(events.CallbackQuery(pattern=r"answer_(\d+)"))
async def handle_answer(event):
    answer_id = int(event.data.decode('utf-8').split('_')[1])
    
    session = SessionLocal()
    answer = session.query(Answer).filter(Answer.id == answer_id).first()
    
    if answer:
        if answer.is_correct:
            await event.answer("✅ Правильно!")  # Показує спливаюче повідомлення
            await bot.send_message(
                event.chat_id,
                f"✅ Правильно! {answer.answer_text}",
            )
        else:
            correct_answer = session.query(Answer).filter(
                Answer.question_id == answer.question_id,
                Answer.is_correct == True
            ).first()
            
            correct_text = correct_answer.answer_text if correct_answer else "Не знайдено"
            
            await event.answer("❌ Неправильно")  # Показує спливаюче повідомлення
            await bot.send_message(
                event.chat_id,
                f"❌ Неправильно. Ви обрали: {answer.answer_text}\n"
                f"Правильна відповідь: {correct_text}",
            )
        
        # Додаємо кнопку для наступного питання
        await bot.send_message(
            event.chat_id,
            "Бажаєте продовжити?",
            buttons=[Button.inline("Наступне питання", data="next_question")]
        )
    
    session.close()

@bot.on(events.CallbackQuery(pattern=r"next_question"))
async def handle_next_question(event):
    # Видаляємо попереднє повідомлення з кнопкою "Наступне питання"
    await event.delete()
    
    # Отримуємо список категорій для тестування
    categories = get_test_categories()
    
    # Створюємо інлайн-кнопки для кожної категорії
    category_buttons = [
        [Button.inline(cat.name, data=f"category_{cat.id}")]
        for cat in categories
    ]
    
    # Додаємо кнопку "На головну"
    category_buttons.append([Button.inline("🏠 На головну", data="go_home")])
    
    # Відправляємо нове повідомлення з запрошенням вибрати тему
    await bot.send_message(
        event.chat_id,
        "📚 Виберіть з меню тему для тестування:",
        buttons=category_buttons
    )

# Додаємо обробник для кнопки "На головну"
@bot.on(events.CallbackQuery(pattern=r"go_home"))
async def go_home(event):
    await event.delete()  # Видаляємо повідомлення з меню вибору теми
    
    # Відправляємо головне меню
    await bot.send_message(
        event.chat_id,
        "🔹 Ви повернулися до головного меню. Оберіть пункт із меню.",
        buttons=MAIN_MENU_BUTTONS
    )

# Додаємо обробник для вибору категорії через інлайн-кнопки
@bot.on(events.CallbackQuery(pattern=r"category_(\d+)"))
async def handle_category_inline_selection(event):
    # Отримуємо id категорії з callback_data
    category_id = int(event.data.decode('utf-8').split('_')[1])
    
    session = SessionLocal()
    category = session.query(TestCategory).filter(TestCategory.id == category_id).first()
    
    if category:
        tests = session.query(Test).filter(Test.category_id == category.id).all()
        if not tests:
            await event.answer("😕 В обраній темі немає тестів.")
            session.close()
            return
        
        test = random.choice(tests)
        question = get_random_question(test.id)
        
        if question:
            # Видаляємо повідомлення з вибором категорії
            await event.delete()
            
            # Створюємо інлайн-кнопки для варіантів відповідей
            buttons = [
                [Button.inline(ans.answer_text, data=f"answer_{ans.id}")]
                for ans in question.answers
            ]
            
            # Відправляємо нове повідомлення з питанням та варіантами відповідей
            await bot.send_message(
                event.chat_id,
                f"❓ {question.question_text}",
                buttons=buttons
            )
        else:
            await event.answer("😕 В тесті немає питань.")
    else:
        await event.answer("😕 Категорію не знайдено.")
    
    session.close()

# Додаємо обробник для кнопки "Завершити тест"
@bot.on(events.NewMessage(pattern='🛑 Завершити тест'))
async def finish_test(event):
    # Повертаємо користувача до меню тестування
    categories = get_test_categories()
    
    if not categories:
        await event.reply("😕 Наразі немає жодного доступного тесту.")
        return
    
    buttons = [[Button.text(cat.name, resize=True)] for cat in categories]
    await event.reply("📚 Оберіть тему для тестування:", buttons=buttons)

def main():
    print("🤖 Бот запущений...")
    bot.run_until_disconnected()

if __name__ == '__main__':
    main()

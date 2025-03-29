import random
from datetime import datetime
from telethon import events, Button
from utils.database import SessionLocal
from testing.test_logic import get_test_categories, get_random_question
from testing.models import TestCategory, Test, Question, Answer, UserTestSession, UserAnswer
from auth.models import User
from sqlalchemy import func

MAX_QUESTIONS_PER_TEST = 3

async def setup_testing_handlers(bot_client):
    @bot_client.on(events.NewMessage(pattern='🧪 Тестування'))
    async def testing_menu(event):
        categories = get_test_categories()
        if not categories:
            await event.reply("😕 Наразі немає жодного доступного тесту.")
            return
        # Використовуємо inline кнопки, щоб при натисканні одразу відправляти callback_data
        buttons = [[Button.inline(cat.name, data=f"category_{cat.id}")] for cat in categories]
        await event.reply("📚 Оберіть тему для тестування:", buttons=buttons)

    @bot_client.on(events.CallbackQuery(pattern=r"^category_(\d+)$"))
    async def handle_category_selection(event):
        category_id = int(event.data.decode('utf-8').split('_')[1])
        
        session = SessionLocal()
        category = session.query(TestCategory).filter(TestCategory.id == category_id).first()
        session.close()

        if not category:
            await event.answer("❌ Категорію не знайдено.")
            return

        await event.delete()

        # Зберігаємо category_id в data для callback (наприклад, starttest_5)
        buttons = [
            [Button.inline("✅ Розпочати тестування", data=f"starttest_{category.id}")],
            [Button.inline("🔙 Повернутись назад", data="go_back_to_categories")]
        ]

        await bot_client.send_message(
            event.chat_id,
            f"📚 Ви обрали категорію: *{category.name}*\n\nГотові почати тест?",
            buttons=buttons,
            parse_mode='markdown'
        )

    @bot_client.on(events.CallbackQuery(pattern=r"^go_back_to_categories$"))
    async def go_back_to_categories(event):
        await event.delete()

        categories = get_test_categories()
        if not categories:
            await bot.send_message(event.chat_id, "😕 Наразі немає жодного доступного тесту.")
            return

        buttons = [[Button.inline(cat.name, data=f"category_{cat.id}")] for cat in categories]
        await bot.send_message(event.chat_id, "📚 Оберіть тему для тестування:", buttons=buttons)


    # @bot_client.on(events.CallbackQuery(pattern=r"^category_(\d+)$"))
    # async def handle_category_inline_selection(event):
    #     # Отримуємо id категорії з callback_data
    #     category_id = int(event.data.decode('utf-8').split('_')[1])
    #     session = SessionLocal()
    #     category = session.query(TestCategory).filter(TestCategory.id == category_id).first()
    #     if category:
    #         tests = session.query(Test).filter(Test.category_id == category.id).all()
    #         if not tests:
    #             await event.answer("😕 В обраній темі немає тестів.")
    #             session.close()
    #             return
    #         test = random.choice(tests)
    #         question = get_random_question(test.id)
    #         if question:
    #             await event.delete()  # Видаляємо повідомлення з вибором категорії
    #             # Створюємо inline кнопки для кожного варіанту відповіді
    #             buttons = [
    #                 [Button.inline(ans.answer_text, data=f"answer_{ans.id}")]
    #                 for ans in question.answers
    #             ]
    #             await bot_client.send_message(
    #                 event.chat_id,
    #                 f"❓ {question.question_text}",
    #                 buttons=buttons
    #             )
    #         else:
    #             await event.answer("😕 В тесті немає питань.")
    #     else:
    #         await event.answer("😕 Категорію не знайдено.")
    #     session.close()
    
    @bot_client.on(events.CallbackQuery(pattern=r"^answer_(\d+)$"))
    async def handle_answer(event):
        answer_id = int(event.data.decode('utf-8').split('_')[1])
        session = SessionLocal()
        answer = session.query(Answer).filter(Answer.id == answer_id).first()
        if answer:
            if answer.is_correct:
                await event.answer("✅ Правильно!")
                await bot_client.send_message(
                    event.chat_id,
                    f"✅ Правильно! {answer.answer_text}"
                )
            else:
                correct_answer = session.query(Answer).filter(
                    Answer.question_id == answer.question_id,
                    Answer.is_correct == True
                ).first()
                correct_text = correct_answer.answer_text if correct_answer else "Не знайдено"
                await event.answer("❌ Неправильно")
                await bot_client.send_message(
                    event.chat_id,
                    f"❌ Неправильно. Ви обрали: {answer.answer_text}\n"
                    f"Правильна відповідь: {correct_text}"
                )
            # Додаємо кнопку для наступного питання
            await bot_client.send_message(
                event.chat_id,
                "Бажаєте продовжити?",
                buttons=[Button.inline("Наступне питання", data="next_question")]
            )
        session.close()
    
    @bot_client.on(events.CallbackQuery(pattern=r"^next_question$"))
    async def handle_next_question(event):
        await event.delete()
        categories = get_test_categories()
        category_buttons = [[Button.inline(cat.name, data=f"category_{cat.id}")]
                            for cat in categories]
        category_buttons.append([Button.inline("🏠 На головну", data="go_home")])
        await bot_client.send_message(
            event.chat_id,
            "📚 Виберіть з меню тему для тестування:",
            buttons=category_buttons
        )
    
    @bot_client.on(events.CallbackQuery(pattern=r"^go_home$"))
    async def go_home(event):
        await event.delete()
        await bot_client.send_message(
            event.chat_id,
            "🔹 Ви повернулися до головного меню. Оберіть пункт із меню.",
            buttons=[[Button.text("🧪 Тестування", resize=True)],
                     [Button.text("📌 Очікуйте оновлень", resize=True)]]
        )

    @bot_client.on(events.CallbackQuery(pattern=r"^starttest_(\d+)$"))
    async def handle_start_test(event):
        category_id = int(event.data.decode('utf-8').split('_')[1])
        telegram_id = event.sender_id

        session = SessionLocal()

        # Знаходимо користувача
        user = session.query(User).filter(User.telegram_id == telegram_id).first()
        if not user:
            await event.answer("❌ Ви не зареєстровані.")
            session.close()
            return

        # Обираємо випадковий тест з категорії
        test = session.query(Test).filter(Test.category_id == category_id).order_by(func.rand()).first()
        if not test:
            await event.answer("❌ В цій категорії немає тестів.")
            session.close()
            return

        # Створюємо сесію тестування
        test_session = UserTestSession(
            user_id=user.id,
            test_id=test.id,
            started_at=datetime.utcnow()
        )
        session.add(test_session)
        session.commit()

        # Отримуємо перше питання
        question = get_random_question(test.id)
        if not question:
            await bot_client.send_message(event.chat_id, "❌ У цьому тесті немає питань.")
            session.close()
            return

        # Зберігаємо session_id + question_id у callback data (для наступного кроку)
        buttons = [
            [Button.inline(ans.answer_text, data=f"ans_{test_session.id}_{question.id}_{ans.id}")]
            for ans in question.answers
        ]

        await event.delete()

        await bot_client.send_message(
            event.chat_id,
            f"❓ {question.question_text}",
            buttons=buttons
        )

        session.close()

    @bot_client.on(events.CallbackQuery(pattern=r"^ans_(\d+)_(\d+)_(\d+)$"))
    async def handle_user_answer(event):
        data = event.data.decode('utf-8').split('_')
        session_id, question_id, answer_id = map(int, data[1:])

        session = SessionLocal()

        answer = session.query(Answer).filter(Answer.id == answer_id).first()
        if not answer:
            await event.answer("❌ Відповідь не знайдена.")
            session.close()
            return

        # Зберігаємо відповідь
        is_correct = answer.is_correct
        user_answer = UserAnswer(
            session_id=session_id,
            question_id=question_id,
            answer_id=answer.id,
            is_correct=is_correct
        )
        session.add(user_answer)
        session.commit()

        # Підготовка фідбеку
        if is_correct:
            feedback = f"✅ Правильно! {answer.answer_text}"
        else:
            correct_answer = session.query(Answer).filter(
                Answer.question_id == question_id,
                Answer.is_correct == True
            ).first()
            feedback = (
                f"❌ Неправильно. Ви обрали: {answer.answer_text}\n"
                f"✔️ Правильна відповідь: {correct_answer.answer_text if correct_answer else 'Невідомо'}"
            )

        await event.answer("✔️ Відповідь прийнята")
        await event.delete()
        await bot_client.send_message(event.chat_id, feedback)

        # Кількість наданих відповідей
        answered_count = session.query(UserAnswer).filter(
            UserAnswer.session_id == session_id
        ).count()

        # Якщо досягнуто максимум — завершення
        if answered_count >= MAX_QUESTIONS_PER_TEST:
            buttons = [
                [Button.inline("💾 Зарахувати результат", data=f"finalize_{session_id}")],
                [Button.inline("❌ Скасувати", data="go_home")]
            ]
            await bot_client.send_message(
                event.chat_id,
                "🎉 Ви відповіли на всі заплановані питання! Що робимо далі?",
                buttons=buttons
            )
            session.close()
            return

        # Отримаємо список вже пройдених питань
        answered_ids = session.query(UserAnswer.question_id).filter(
            UserAnswer.session_id == session_id
        ).all()
        answered_ids = [row[0] for row in answered_ids]

        current_session = session.query(UserTestSession).filter(UserTestSession.id == session_id).first()

        remaining_questions = session.query(Question).filter(
            Question.test_id == current_session.test_id,
            ~Question.id.in_(answered_ids)
        ).all()

        next_question = random.choice(remaining_questions) if remaining_questions else None

        if next_question:
            buttons = [
                [Button.inline(ans.answer_text, data=f"ans_{session_id}_{next_question.id}_{ans.id}")]
                for ans in next_question.answers
            ]
            await bot_client.send_message(
                event.chat_id,
                f"❓ {next_question.question_text}",
                buttons=buttons
            )
        else:
            # Раптом у тесті питань менше, ніж MAX
            buttons = [
                [Button.inline("💾 Зарахувати результат", data=f"finalize_{session_id}")],
                [Button.inline("❌ Скасувати", data="go_home")]
            ]
            await bot_client.send_message(
                event.chat_id,
                "🛑 Більше питань немає. Бажаєте завершити тест?",
                buttons=buttons
            )

        session.close()


    @bot_client.on(events.CallbackQuery(pattern=r"^finalize_(\d+)$"))
    async def handle_finalize_test(event):
        session_id = int(event.data.decode('utf-8').split('_')[1])

        session = SessionLocal()

        # Отримуємо сесію тестування
        test_session = session.query(UserTestSession).filter(
            UserTestSession.id == session_id
        ).first()

        if not test_session:
            await event.answer("❌ Сесію не знайдено.")
            session.close()
            return

        # Отримуємо відповіді користувача
        user_answers = session.query(UserAnswer).filter(
            UserAnswer.session_id == session_id
        ).all()

        total = len(user_answers)
        correct = sum(1 for ua in user_answers if ua.is_correct)
        incorrect = total - correct
        score = int((correct / total) * 100) if total > 0 else 0
        is_passed = score >= 70  # 🔧 умова проходження — можна змінити

        # Оновлюємо сесію
        test_session.completed_at = datetime.utcnow()
        test_session.score = score
        test_session.is_passed = is_passed
        session.commit()

        # Виводимо результат
        result_message = (
            f"📊 *Результати тесту:*\n\n"
            f"✅ Правильних відповідей: {correct}\n"
            f"❌ Помилкових відповідей: {incorrect}\n"
            f"📈 Результат: *{score}%* — {'✅ Зараховано' if is_passed else '❌ Не зараховано'}"
        )

        await event.delete()
        await bot_client.send_message(
            event.chat_id,
            result_message,
            buttons=[
                [Button.inline("🔙 Повернутись в меню", data="go_main_menu")]
            ],
            parse_mode='markdown'
        )

        session.close()


    @bot_client.on(events.CallbackQuery(pattern=r"^go_main_menu$"))
    async def go_main_menu(event):
        await event.answer()
        await event.delete()

        await bot_client.send_message(
            event.chat_id,
            "🔹 Ви повернулися до головного меню. Оберіть дію:",
            buttons=[
                [Button.text("🧪 Тестування", resize=True)],
                [Button.text("📌 Очікуйте оновлень", resize=True)]
            ]
        )
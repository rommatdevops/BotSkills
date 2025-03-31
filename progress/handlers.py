from telethon import events
from sqlalchemy.orm import joinedload
from utils.database import SessionLocal
from testing.models import UserTestSession
from auth.models import User

async def setup_progress_handlers(bot_client):
    @bot_client.on(events.NewMessage(pattern=r"📈 Мій прогрес"))
    async def handle_progress(event):
        session = SessionLocal()
        telegram_id = event.sender_id

        user = session.query(User).filter(User.telegram_id == telegram_id).first()
        if not user:
            await event.reply("❌ Ви не зареєстровані.")
            session.close()
            return

        # Всі завершені сесії з оцінками
        sessions = session.query(UserTestSession).options(joinedload(UserTestSession.test)).filter(
            UserTestSession.user_id == user.id,
            UserTestSession.completed_at.isnot(None),
            UserTestSession.score.isnot(None)
        ).all()

        # Залишаємо лише найкращу сесію для кожного тесту
        best_sessions_by_test = {}
        for s in sessions:
            if s.test_id not in best_sessions_by_test or (s.score or 0) > (best_sessions_by_test[s.test_id].score or 0):
                best_sessions_by_test[s.test_id] = s

        best_sessions = list(best_sessions_by_test.values())

        total = len(best_sessions)
        perfect = sum(1 for s in best_sessions if s.score == 100)
        avg_score = sum(s.score for s in best_sessions if s.score is not None) // total if total > 0 else 0

        # Формуємо текст звіту
        msg = (
            "**Ваш прогрес:**\n\n"
            f"🧪 Пройдено тестів: {total}\n"
            f"🎯 Ідеально (100%): {perfect}\n"
            f"📈 Середній результат: {avg_score}%\n\n"
            f"📝 **Найкращий результат по тестах:**"
        )

        for s in best_sessions:
            emoji = "✅" if s.score >= 70 else "❌"
            msg += f"\n• {s.test.title}: {s.score}% {emoji}"

        await event.reply(msg, parse_mode='markdown')
        session.close()

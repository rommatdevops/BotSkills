from telethon import events, Button

async def setup_common_handlers(bot_client):
    @bot_client.on(events.CallbackQuery(pattern=r"^go_main_menu$"))
    async def go_main_menu(event):
        await event.answer()
        await event.delete()

        await bot_client.send_message(
            event.chat_id,
            "🔹 Ви повернулися до головного меню. Оберіть дію:",
            buttons=[
                [Button.text("🧪 Тестування", resize=True)],
                [Button.text("📈 Мій прогрес", resize=True)],
                [Button.text("📌 Очікуйте оновлень", resize=True)]
            ]
        )

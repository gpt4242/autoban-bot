"""
Webhook версия бота для деплоя на Render/Heroku.
Используется когда polling невозможен (serverless платформы).
"""
import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.exceptions import TelegramForbiddenError
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

# Настройки
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
TARGET_CHAT_ID = os.getenv("TARGET_CHAT_ID")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
WEB_HOST = os.getenv("WEB_HOST", "0.0.0.0")
WEB_PORT = int(os.getenv("WEB_PORT", 8080))
PUBLIC_URL = os.getenv("PUBLIC_URL", "")

# Логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Хранилище
subscribers_cache = {}
banned_users = set()


async def ban_user(user_id: int, reason: str = "Отписка от канала") -> bool:
    """Банит пользователя в целевом чате."""
    try:
        if user_id in banned_users:
            logger.info(f"Пользователь {user_id} уже забанен")
            return False

        await bot.ban_chat_member(
            chat_id=TARGET_CHAT_ID,
            user_id=user_id,
            until_date=int((datetime.now() + timedelta(days=365)).timestamp())
        )

        banned_users.add(user_id)
        logger.info(f"✅ Забанен {user_id}. Причина: {reason}")

        try:
            await bot.send_message(
                chat_id=ADMIN_ID,
                text=f"🔨 <b>Забанен пользователь:</b>\n"
                     f"ID: <code>{user_id}</code>\n"
                     f"Причина: {reason}"
            )
        except Exception as e:
            logger.error(f"Ошибка уведомления: {e}")

        return True

    except TelegramForbiddenError:
        logger.error(f"Нет прав для бана {user_id}")
        return False
    except Exception as e:
        logger.error(f"Ошибка бана {user_id}: {e}")
        return False


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Команда /start"""
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔️ У вас нет доступа")
        return

    await message.answer(
        "🤖 <b>Автобан отписчиков (webhook)!</b>\n\n"
        f"📋 <b>Настройки:</b>\n"
        f"• Канал: <code>{CHANNEL_ID}</code>\n"
        f"• Бан в: <code>{TARGET_CHAT_ID}</code>\n\n"
        f"<b>Команды:</b>\n"
        f"/status - статус\n"
        f"/ban <user_id> - забанить вручную"
    )


@dp.message(Command("status"))
async def cmd_status(message: types.Message):
    """Команда /status"""
    if message.from_user.id != ADMIN_ID:
        return

    await message.answer(
        f"📊 <b>Статус:</b>\n\n"
        f"✅ Бот активен (webhook)\n"
        f"👥 Подписчиков в кэше: {len(subscribers_cache)}\n"
        f"🔨 Забанено: {len(banned_users)}"
    )


@dp.message(Command("ban"))
async def cmd_manual_ban(message: types.Message):
    """Ручной бан"""
    if message.from_user.id != ADMIN_ID:
        return

    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("❌ Использование: /ban <user_id>")
            return

        user_id = int(parts[1])
        success = await ban_user(user_id, "Ручной бан")

        if success:
            await message.answer(f"✅ {user_id} забанен")
        else:
            await message.answer(f"❌ Не удалось забанить {user_id}")

    except ValueError:
        await message.answer("❌ Неверный формат ID")


@dp.chat_member()
async def handle_chat_member_update(chat_member_update: types.ChatMemberUpdated):
    """Отслеживает отписки от канала."""
    user_id = chat_member_update.from_user.id
    old_status = chat_member_update.old_chat_member.status
    new_status = chat_member_update.new_chat_member.status

    logger.info(f"{user_id}: {old_status} -> {new_status}")

    if old_status in ["member", "administrator"] and new_status in ["left", "kicked"]:
        logger.info(f"⚠️ {user_id} отписался!")
        await ban_user(user_id, "Отписка от канала")

    elif new_status == "member":
        subscribers_cache[user_id] = datetime.now()
        logger.info(f"✅ {user_id} подписался")


async def health_check(request):
    """Эндпоинт для пинга (чтобы сервер не спал)."""
    return web.Response(text="OK")


async def on_startup(bot: Bot):
    """Настройка webhook при запуске."""
    if PUBLIC_URL:
        webhook_url = f"{PUBLIC_URL}/webhook"
        await bot.set_webhook(webhook_url)
        logger.info(f"Webhook установлен: {webhook_url}")
    else:
        logger.warning("PUBLIC_URL не установлен. Webhook не будет работать!")


async def main():
    """Запуск бота с webhook."""
    logger.info("=" * 50)
    logger.info("🤖 Запуск бота (webhook режим)")
    logger.info(f"📺 Канал: {CHANNEL_ID}")
    logger.info(f"🎯 Бан в: {TARGET_CHAT_ID}")
    logger.info("=" * 50)

    # Загружаем забаненных
    try:
        if os.path.exists("banned_users.txt"):
            with open("banned_users.txt", "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        banned_users.add(int(line))
            logger.info(f"Загружено {len(banned_users)} забаненных")
    except Exception as e:
        logger.error(f"Ошибка загрузки забаненных: {e}")

    # Запускаем webhook бота
    asyncio.create_task(on_startup(bot))

    # Настраиваем веб-сервер
    app = web.Application()
    app.router.add_get("/health", health_check)

    # Telegram webhook handler
    webhook_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot
    )
    webhook_handler.register(app, path="/webhook")

    setup_application(app, dp, bot=bot)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, WEB_HOST, WEB_PORT)
    await site.start()

    logger.info(f"Сервер запущен на {WEB_HOST}:{WEB_PORT}")

    # Бесконечный цикл
    try:
        await asyncio.Event().wait()
    finally:
        # Сохраняем забаненных
        try:
            with open("banned_users.txt", "w", encoding="utf-8") as f:
                for uid in banned_users:
                    f.write(f"{uid}\n")
        except Exception:
            pass
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен")

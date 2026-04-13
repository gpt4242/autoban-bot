"""
🤖 Telegram Автобан Бот — полная версия
Функции:
- Автобан отписчиков
- Админ-панель с inline кнопками
- Лид-магниты с генерацией ссылок
- Проверка подписки перед выдачей
- Статистика подписок/источников
- Управление банами и вайтлистом
- Ежедневные отчёты
"""
import asyncio
import logging
import os
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from dotenv import load_dotenv
from datetime import datetime, timedelta

from database import (
    add_banned, remove_banned, is_banned, get_all_banned,
    add_to_whitelist, remove_from_whitelist, is_whitelisted, get_whitelist,
    create_magnet, update_magnet_link, deactivate_magnet,
    get_active_magnets, get_magnet, increment_magnet_downloads,
    log_subscription, log_action, get_logs,
    save_daily_report, get_daily_reports, get_sub_stats
)

load_dotenv()

# ============ НАСТРОЙКИ ============
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
WEB_HOST = os.getenv("WEB_HOST", "0.0.0.0")
WEB_PORT = int(os.getenv("WEB_PORT", 8080))
PUBLIC_URL = os.getenv("PUBLIC_URL", "")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


class AdminStates(StatesGroup):
    waiting_for_magnet_topic = State()
    waiting_for_magnet_title = State()
    waiting_for_magnet_content = State()
    waiting_for_magnet_file = State()


# ============ ВСПОМОГАТЕЛЬНЫЕ ============

def admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Статистика", callback_data="admin:stats"),
            InlineKeyboardButton(text="🔨 Забаненные", callback_data="admin:banned"),
        ],
        [
            InlineKeyboardButton(text="➕ Белый список", callback_data="admin:whitelist"),
            InlineKeyboardButton(text="🎁 Лид-магниты", callback_data="admin:magnets"),
        ],
        [
            InlineKeyboardButton(text="📋 Логи", callback_data="admin:logs"),
            InlineKeyboardButton(text="📅 Отчёты", callback_data="admin:reports"),
        ],
        [InlineKeyboardButton(text="🚪 Выход", callback_data="admin:close")],
    ])


def magnets_keyboard(magnets):
    buttons = []
    for m in magnets:
        buttons.append([InlineKeyboardButton(
            text=f"🎁 {m['title']}",
            callback_data=f"magnet:{m['id']}"
        )])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_magnets_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Создать магнит", callback_data="magnet_create")],
        [InlineKeyboardButton(text="📋 Список магнитов", callback_data="magnet_list")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin:menu")],
    ])


async def _ban_user(user_id, reason="Ручной бан"):
    """Банит пользователя. Проверяет вайтлист."""
    if is_whitelisted(user_id):
        logger.info(f"Пользователь {user_id} в вайтлисте, не баню")
        return False
    if is_banned(user_id):
        return False
    try:
        add_banned(user_id, reason=reason)
        await bot.ban_chat_member(
            chat_id=CHANNEL_ID,
            user_id=user_id,
            until_date=int((datetime.now() + timedelta(days=365)).timestamp())
        )
        log_action("ban", user_id, f"Причина: {reason}")
        return True
    except Exception as e:
        logger.error(f"Ошибка бана {user_id}: {e}")
        return False


# ============ СТАРТ ============

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer(
            "🤖 <b>Автобан бот</b>\n\n"
            "Админ-панель готова к работе.\nВыберите действие:",
            reply_markup=admin_keyboard()
        )
        return

    magnets = get_active_magnets()
    if magnets:
        await message.answer(
            f"👋 <b>Привет, {message.from_user.first_name}!</b>\n\n"
            "Выберите материал, который хотите получить:",
            reply_markup=magnets_keyboard(magnets)
        )
    else:
        await message.answer(
            f"👋 Привет, {message.from_user.first_name}!\n\n"
            "Сейчас нет доступных материалов."
        )


@dp.message(Command("menu"))
async def cmd_menu(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("Выберите действие:", reply_markup=admin_keyboard())
    else:
        await cmd_start(message)


# ============ САМОПИНГ ============

async def self_ping():
    if not PUBLIC_URL:
        logger.warning("PUBLIC_URL не установлен — self-ping отключён")
        return
    health_url = f"{PUBLIC_URL}/health"
    logger.info(f"Self-ping: {health_url} каждые 3 мин")
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(health_url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        logger.debug("Self-ping OK")
        except Exception as e:
            logger.warning(f"Self-ping ошибка: {e}")
        await asyncio.sleep(180)


# ============ АДМИН CALLBACK'И ============

@dp.callback_query(F.data == "admin:menu")
async def admin_menu(cb: types.CallbackQuery):
    await cb.message.edit_text("Выберите действие:", reply_markup=admin_keyboard())
    await cb.answer()


@dp.callback_query(F.data == "admin:close")
async def admin_close(cb: types.CallbackQuery):
    try:
        await cb.message.delete()
    except Exception:
        await cb.message.edit_text("Панель закрыта")
    await cb.answer()


@dp.callback_query(F.data == "admin:stats")
async def admin_stats(cb: types.CallbackQuery):
    stats = get_sub_stats()
    text = (
        f"📊 <b>Статистика подписок</b>\n\n"
        f"👥 Всего подписалось: <b>{stats['total_subs']}</b>\n"
        f"🚪 Всего отписалось: <b>{stats['total_unsubs']}</b>\n"
        f"📈 Чистый прирост: <b>{stats['net_subs']}</b>\n\n"
        f"📅 <b>За сегодня:</b>\n"
        f"➕ Подписок: {stats['subs_today']}\n"
        f"➖ Отписок: {stats['unsubs_today']}\n"
    )
    if stats['sources']:
        text += "\n📍 <b>Источники:</b>\n"
        for s in stats['sources']:
            text += f"  • {s['source']}: {s['cnt']}\n"
    await cb.message.edit_text(text, reply_markup=admin_keyboard())
    await cb.answer()


@dp.callback_query(F.data == "admin:banned")
async def admin_banned(cb: types.CallbackQuery):
    banned_list = get_all_banned()
    if not banned_list:
        text = "🔨 <b>Забаненные</b>\n\nПока никого нет."
    else:
        text = f"🔨 <b>Забаненные</b> ({len(banned_list)})\n\n"
        for b in banned_list[:15]:
            name = b.get('first_name') or ''
            uname = b.get('username') or ''
            reason = b.get('reason') or ''
            text += f"• {name} <code>{b['user_id']}</code>"
            if uname:
                text += f" (@{uname})"
            text += f"\n  {reason}\n\n"
        if len(banned_list) > 15:
            text += f"...и ещё {len(banned_list) - 15}"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin:menu")],
    ])
    await cb.message.edit_text(text, reply_markup=kb)
    await cb.answer()


@dp.callback_query(F.data == "admin:whitelist")
async def admin_whitelist(cb: types.CallbackQuery):
    wl = get_whitelist()
    if not wl:
        text = "➕ <b>Белый список</b>\n\nПока никого нет."
    else:
        text = f"➕ <b>Белый список</b> ({len(wl)})\n\n"
        for w in wl[:15]:
            name = w.get('username') or str(w['user_id'])
            comment = w.get('comment') or ''
            text += f"• <code>{w['user_id']}</code> — {name}"
            if comment:
                text += f" ({comment})"
            text += "\n"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin:menu")],
    ])
    await cb.message.edit_text(text, reply_markup=kb)
    await cb.answer()


@dp.callback_query(F.data == "admin:logs")
async def admin_logs(cb: types.CallbackQuery):
    logs = get_logs(20)
    if not logs:
        text = "📋 <b>Логи</b>\n\nПока пусто."
    else:
        text = "📋 <b>Последние действия</b>\n\n"
        for l in logs:
            uid = f" (user {l['user_id']})" if l['user_id'] else ""
            text += f"• {l['action']}{uid}\n"
            if l.get('details'):
                text += f"  {l['details']}\n"
            text += f"  <i>{l['created_at']}</i>\n\n"
    await cb.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin:menu")],
    ]))
    await cb.answer()


@dp.callback_query(F.data == "admin:reports")
async def admin_reports(cb: types.CallbackQuery):
    reports = get_daily_reports(7)
    if not reports:
        text = "📅 <b>Отчёты</b>\n\nПока нет данных."
    else:
        text = "📅 <b>Ежедневные отчёты</b>\n\n"
        for r in reports:
            text += (
                f"📆 <b>{r['date']}</b>\n"
                f"  ➕ {r['new_subs']} ➖ {r['unsubs']} 🔨 {r['bans']} 🎁 {r['magnet_downloads']}\n\n"
            )
    await cb.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Сохранить сейчас", callback_data="admin:reports_save")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin:menu")],
    ]))
    await cb.answer()


@dp.callback_query(F.data == "admin:reports_save")
async def admin_reports_save(cb: types.CallbackQuery):
    save_daily_report()
    await cb.answer("✅ Отчёт сохранен!")
    await admin_reports(cb)


# ============ ЛИД-МАГНИТЫ (ЮЗЕР) ============

@dp.callback_query(F.data.startswith("magnet:"))
async def magnet_get(cb: types.CallbackQuery):
    magnet_id = int(cb.data.split(":")[1])
    magnet = get_magnet(magnet_id)
    if not magnet:
        await cb.answer("Магнит не найден", show_alert=True)
        return

    user_id = cb.from_user.id
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        is_subscribed = member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.error(f"Ошибка проверки подписки: {e}")
        is_subscribed = False

    if not is_subscribed:
        text = (
            f"🎁 <b>{magnet['title']}</b>\n\n"
            f"Для получения подпишитесь на канал:\n"
            f"{magnet['invite_link'] or CHANNEL_ID}\n\n"
            f"После подписки нажмите ещё раз."
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Я подписался!", callback_data=f"magnet:{magnet_id}")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")],
        ])
        await cb.message.edit_text(text, reply_markup=kb)
        await cb.answer()
        return

    # Подписан — выдаём
    increment_magnet_downloads(magnet_id)
    text = f"🎁 <b>{magnet['title']}</b>\n\nДержи:"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Другие материалы", callback_data="back_to_menu")],
    ])
    await cb.message.edit_text(text, reply_markup=kb)

    if magnet.get('content_text'):
        await cb.message.answer(magnet['content_text'])
    if magnet.get('content_file_id'):
        try:
            await bot.send_document(cb.from_user.id, magnet['content_file_id'])
        except Exception as e:
            logger.error(f"Ошибка отправки файла: {e}")
    if magnet.get('content_url'):
        await cb.message.answer(f"🔗 Ссылка: {magnet['content_url']}")

    log_action("magnet_download", user_id, magnet['topic'])
    await cb.answer()


@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(cb: types.CallbackQuery):
    magnets = get_active_magnets()
    user_id = cb.from_user.id
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        is_sub = member.status in ["member", "administrator", "creator"]
    except Exception:
        is_sub = False
    sub_status = "✅ Подписан" if is_sub else "❌ Не подписан"
    text = f"👋 Материалы ({sub_status})\n\nВыберите:"
    await cb.message.edit_text(text, reply_markup=magnets_keyboard(magnets))
    await cb.answer()


# ============ АДМИН: МАГНИТЫ ============

@dp.callback_query(F.data == "admin:magnets")
async def admin_magnets_menu(cb: types.CallbackQuery):
    magnets = get_active_magnets()
    text = (
        f"🎁 <b>Лид-магниты</b>\n\n"
        f"Активных: <b>{len(magnets)}</b>\n\n"
        f"Создайте магнит с уникальной ссылкой.\n"
        f"Бот проверит подписку и выдаст материал."
    )
    await cb.message.edit_text(text, reply_markup=admin_magnets_keyboard())
    await cb.answer()


@dp.callback_query(F.data == "magnet_create")
async def magnet_create(cb: types.CallbackQuery):
    text = (
        "🎁 <b>Создание лид-магнита</b>\n\n"
        "Отправьте <b>тему</b> (код), например:\n"
        "<code>checklist</code>, <code>gaid</code>\n\n"
        "/exit — отмена"
    )
    await cb.message.edit_text(text)
    await cb.answer()
    await cb.message.bot.set_chat_state(cb.from_user.id, "typing")
    await AdminStates.waiting_for_magnet_topic.set()


@dp.message(AdminStates.waiting_for_magnet_topic)
async def magnet_topic_entered(message: types.Message, state: FSMContext):
    if message.text and message.text.strip().lower() == "/exit":
        await state.clear()
        await message.answer("❌ Отменено", reply_markup=admin_keyboard())
        return
    await state.update_data(topic=message.text.strip())
    await state.set_state(AdminStates.waiting_for_magnet_title)
    await message.answer(
        "Теперь отправьте <b>название</b> (видно юзерам):\n"
        "📋 Чек-лист: 10 шагов к успеху"
    )


@dp.message(AdminStates.waiting_for_magnet_title)
async def magnet_title_entered(message: types.Message, state: FSMContext):
    if message.text and message.text.strip().lower() == "/exit":
        await state.clear()
        await message.answer("❌ Отменено", reply_markup=admin_keyboard())
        return
    await state.update_data(title=message.text.strip())
    await state.set_state(AdminStates.waiting_for_magnet_content)
    await message.answer("Отправьте <b>содержимое</b> (текст для юзеров):")


@dp.message(AdminStates.waiting_for_magnet_content)
async def magnet_content_entered(message: types.Message, state: FSMContext):
    if message.text and message.text.strip().lower() == "/exit":
        await state.clear()
        await message.answer("❌ Отменено", reply_markup=admin_keyboard())
        return
    await state.update_data(content_text=message.text)
    await message.answer(
        "📎 Отправьте <b>файл</b> или напишите /skip:"
    )
    await state.set_state(AdminStates.waiting_for_magnet_file)


@dp.message(AdminStates.waiting_for_magnet_file, F.document)
async def magnet_file_received(message: types.Message, state: FSMContext):
    file_id = message.document.file_id
    data = await state.get_data()
    magnet_id = create_magnet(
        topic=data['topic'],
        title=data['title'],
        content_text=data.get('content_text', ''),
        content_file_id=file_id
    )
    try:
        link_obj = await bot.create_chat_invite_link(
            chat_id=CHANNEL_ID,
            name=f"magnet_{data['topic']}"
        )
        update_magnet_link(magnet_id, link_obj.invite_link, data['topic'])
        text = (
            f"✅ <b>Магнит создан!</b>\n\n"
            f"📋 Тема: <code>{data['topic']}</code>\n"
            f"📝 Название: {data['title']}\n"
            f"🔗 Ссылка:\n{link_obj.invite_link}"
        )
    except Exception as e:
        text = (
            f"✅ Магнит создан! ID: {magnet_id}\n"
            f"⚠️ Ошибка ссылки: {e}\n"
            f"Добавьте вручную: /addlink {magnet_id} https://..."
        )
    await state.clear()
    await message.answer(text, reply_markup=admin_keyboard())


@dp.message(AdminStates.waiting_for_magnet_file)
async def magnet_file_skip(message: types.Message, state: FSMContext):
    if message.text and message.text.strip().lower() == "/skip":
        data = await state.get_data()
        magnet_id = create_magnet(
            topic=data['topic'],
            title=data['title'],
            content_text=data.get('content_text', ''),
        )
        await state.clear()
        await message.answer(
            f"✅ Магнит создан (текст)!\n"
            f"Ссылку добавьте: /addlink {magnet_id} https://...",
            reply_markup=admin_keyboard()
        )
        return
    await message.answer("Отправьте файл или /skip")


@dp.callback_query(F.data == "magnet_list")
async def magnet_list(cb: types.CallbackQuery):
    magnets = get_active_magnets()
    if not magnets:
        text = "📋 <b>Магниты</b>\n\nПока нет. Создайте первый!"
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="admin:magnets")],
        ])
    else:
        text = f"📋 <b>Магниты</b> ({len(magnets)})\n\n"
        buttons = []
        for m in magnets:
            text += (
                f"🎁 <b>{m['title']}</b>\n"
                f"  Тема: <code>{m['topic']}</code>\n"
                f"  Скачиваний: {m['downloads']}\n"
                f"  Ссылка: {m.get('invite_link') or '❌ нет'}\n\n"
            )
            buttons.append([InlineKeyboardButton(
                text=f"❌ Деактивировать",
                callback_data=f"magnet_deact:{m['id']}"
            )])
        buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin:magnets")])
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await cb.message.edit_text(text, reply_markup=kb)
    await cb.answer()


@dp.callback_query(F.data.startswith("magnet_deact:"))
async def magnet_deactivate(cb: types.CallbackQuery):
    magnet_id = int(cb.data.split(":")[1])
    deactivate_magnet(magnet_id)
    await cb.answer("✅ Деактивирован")
    await magnet_list(cb)


# ============ КОМАНДЫ АДМИНА ============

@dp.message(Command("ban"))
async def cmd_ban(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❌ /ban <user_id>")
        return
    try:
        uid = int(parts[1])
        ok = await _ban_user(uid, "Ручной бан")
        await message.answer(f"✅ {uid} забанен" if ok else f"❌ Не удалось")
    except ValueError:
        await message.answer("❌ Неверный формат")


@dp.message(Command("unban"))
async def cmd_unban(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❌ /unban <user_id>")
        return
    try:
        uid = int(parts[1])
        remove_banned(uid)
        log_action("unban", uid)
        await message.answer(f"✅ {uid} разбанен")
    except ValueError:
        await message.answer("❌ Неверный формат")


@dp.message(Command("addwl"))
async def cmd_addwl(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=2)
    if len(parts) < 2:
        await message.answer("❌ /addwl <user_id> [коммент]")
        return
    try:
        uid = int(parts[1])
        comment = parts[2] if len(parts) > 2 else None
        add_to_whitelist(uid, comment=comment, added_by=ADMIN_ID)
        log_action("whitelist_add", uid, comment)
        await message.answer(f"✅ {uid} в белом списке")
    except ValueError:
        await message.answer("❌ user_id числом")


@dp.message(Command("rmwl"))
async def cmd_rmwl(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❌ /rmwl <user_id>")
        return
    try:
        uid = int(parts[1])
        remove_from_whitelist(uid)
        log_action("whitelist_remove", uid)
        await message.answer(f"✅ {uid} удалён из вайтлиста")
    except ValueError:
        await message.answer("❌ Неверный формат")


@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    stats = get_sub_stats()
    text = (
        f"📊 Статистика:\n\n"
        f"Подписок: {stats['total_subs']}\n"
        f"Отписок: {stats['total_unsubs']}\n"
        f"Прирост: {stats['net_subs']}\n"
        f"Сегодня: +{stats['subs_today']} / -{stats['unsubs_today']}\n"
    )
    if stats['sources']:
        text += "\nИсточники:\n"
        for s in stats['sources']:
            text += f"  • {s['source']}: {s['cnt']}\n"
    await message.answer(text)


@dp.message(Command("logs"))
async def cmd_logs(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    logs = get_logs(15)
    text = "📋 Последние действия:\n\n"
    for l in logs:
        uid = f" (user {l['user_id']})" if l['user_id'] else ""
        text += f"• {l['action']}{uid}\n"
        if l.get('details'):
            text += f"  {l['details'][:60]}\n"
        text += f"  _{l['created_at']}_\n\n"
    await message.answer(text)


@dp.message(Command("addlink"))
async def cmd_addlink(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer("❌ /addlink <magnet_id> <ссылка>")
        return
    try:
        mid = int(parts[1])
        update_magnet_link(mid, parts[2], parts[2])
        await message.answer("✅ Ссылка добавлена!")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


# ============ ОТСЛЕЖИВАНИЕ ПОДПИСОК ============

@dp.chat_member()
async def handle_chat_member(update: types.ChatMemberUpdated):
    user_id = update.from_user.id
    old = update.old_chat_member.status
    new = update.new_chat_member.status
    username = update.from_user.username
    first_name = update.from_user.first_name

    invite_link = None
    invite_link_name = None
    source = "direct"

    if hasattr(update, 'invite_link') and update.invite_link:
        invite_link = update.invite_link.invite_link
        invite_link_name = update.invite_link.name
        source = "invite_link"
        magnet = get_magnet_by_invite(invite_link_name)
        if magnet:
            source = f"magnet:{magnet['topic']}"

    logger.info(f"{user_id}: {old} → {new} ({source})")

    if old in ["member", "administrator"] and new in ["left", "kicked"]:
        log_subscription(user_id, username, first_name, "unsubscribe", source, invite_link, invite_link_name)
        if not is_whitelisted(user_id):
            ok = await _ban_user(user_id, "Отписка от канала")
            if ok:
                log_action("auto_ban", user_id, f"Отписка. Источник: {source}")
    elif new == "member":
        log_subscription(user_id, username, first_name, "subscribe", source, invite_link, invite_link_name)
        log_action("subscribe", user_id, f"Источник: {source}")


# ============ ЕЖЕДНЕВНЫЙ ОТЧЁТ ============

async def daily_report_task():
    logger.info("Ежедневный отчёт запущен")
    while True:
        now = datetime.now()
        midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        wait = (midnight - now).total_seconds()
        await asyncio.sleep(wait)
        save_daily_report()
        reports = get_daily_reports(1)
        if reports:
            r = reports[0]
            text = (
                f"📅 <b>Отчёт за {r['date']}</b>\n\n"
                f"➕ Подписок: {r['new_subs']}\n"
                f"➖ Отписок: {r['unsubs']}\n"
                f"🔨 Банов: {r['bans']}\n"
                f"🎁 Скачиваний: {r['magnet_downloads']}"
            )
            try:
                await bot.send_message(chat_id=ADMIN_ID, text=text)
            except Exception as e:
                logger.error(f"Ошибка отправки отчёта: {e}")


# ============ ЭНДПОИНТЫ ============

async def health_check(request):
    return web.Response(text="OK")


async def on_startup(b: Bot):
    if PUBLIC_URL:
        url = f"{PUBLIC_URL}/webhook"
        await b.set_webhook(url, drop_pending_updates=True)
        logger.info(f"Webhook: {url}")
    else:
        logger.warning("PUBLIC_URL не установлен!")


# ============ ЗАПУСК ============

async def main():
    logger.info("=" * 50)
    logger.info("🤖 Автобан бот — полная версия")
    logger.info(f"Канал: {CHANNEL_ID}")
    logger.info(f"Админ: {ADMIN_ID}")
    logger.info("=" * 50)

    asyncio.create_task(self_ping())
    asyncio.create_task(on_startup(bot))
    asyncio.create_task(daily_report_task())

    app = web.Application()
    app.router.add_get("/health", health_check)

    webhook_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_handler.register(app, path="/webhook")

    setup_application(app, dp, bot=bot)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, WEB_HOST, WEB_PORT)
    await site.start()

    logger.info(f"Сервер: {WEB_HOST}:{WEB_PORT}")

    try:
        await asyncio.Event().wait()
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен")

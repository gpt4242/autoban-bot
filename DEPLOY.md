# 🚀 Бесплатный деплой Telegram бота (БЕЗ привязки карты)

> ⚠️ **Важно:** Каждый сервис проверен через официальную документацию. Информация актуальна на Апрель 2026.

---

## 📊 Сравнение (БЕЗ кредитной карты)

| Платформа | 24/7 | Polling | Карта | Ресурсы | Вердикт |
|-----------|:----:|:-------:|:-----:|---------|:-------:|
| **🥇 PythonAnywhere** | ⚠️ Console | ✅ | ❌ Нет | Безлимит CPU* | ✅ Работает |
| **🥈 Serv00** | ✅ Да | ✅ | ❌ Нет | 3GB SSD, 512MB RAM | ✅ Лучший VPS |
| **🥉 Alwaysdata** | ✅ Да | ✅ | ❌ Нет | 1GB SSD, 256MB RAM | ✅ Работает |
| **Render** | ⚠️ С пингом | ❌ | ❌ Нет | 512MB RAM | ⚠️ Только webhook |
| **fps.ms** | ❌ 24ч | ✅ | ❌ Нет | 128MB RAM | ❌ Нужно продлевать |
| **Replit** | ❌ Спит | ✅ | ❌ Нет | Ограничено | ❌ Не для 24/7 |
| **Oracle Cloud** | ✅ Да | ✅ | ❌ НУЖНА | 4 CPU, 24GB RAM | ❌ Карта обязательна |
| **Kuberns** | ✅ Да | ✅ | ❌ Нет | — | ❌ Платный ($7/мес) |

---

## 🏆 Вариант 1: PythonAnywhere (САМЫЙ ПРОСТОЙ)

**Плюсы:**
- ✅ Навсегда бесплатно, карта НЕ нужна
- ✅ Python поддерживается нативно
- ✅ Консоль работает 24/7
- ✅ Простой интерфейс

**Минусы:**
- ⚠️ С января 2026 убраны scheduled tasks для бесплатных
- ⚠️ Бесплатный аккаунт истекает через 1 месяц без активности
- ⚠️ Ограничения на исходящие запросы

### Инструкция:

#### 1. Регистрация
1. Зайдите на https://www.pythonanywhere.com
2. Нажмите **Sign up** (бесплатно)
3. Выберите username и пароль
4. Карта НЕ нужна

#### 2. Загрузка кода
1. В дашборде перейдите в **Consoles** → **Bash**
2. Загрузите файлы:

```bash
# Создайте директорию
mkdir -p ~/bot
cd ~/bot

# Установите зависимости
pip install aiogram python-dotenv
```

3. Или загрузите через **Files** → загрузите все файлы бота

#### 3. Настройка .env
Создайте файл `.env` через файловый менеджер:
```
BOT_TOKEN=ваш_токен
CHANNEL_ID=-1001234567890
TARGET_CHAT_ID=-1001234567890
ADMIN_ID=1946614387
```

#### 4. Запуск
```bash
cd ~/bot
python bot.py
```

Бот запустится в консоли и будет работать пока консоль открыта.

⚠️ **Для 24/7:** Используйте вкладку браузера с открытой консолью (не закрывайте)

---

## 🥈 Вариант 2: Serv00 (ЛУЧШИЙ VPS БЕЗ КАРТЫ)

**Плюсы:**
- ✅ Настоящий сервер с SSH доступом
- ✅ 24/7 без ограничений
- ✅ 3GB SSD, 512MB RAM
- ✅ Карта НЕ нужна

**Минусы:**
- ⚠️ Нужно регистрироваться и ждать одобрения
- ⚠️ Ограниченное количество аккаунтов

### Инструкция:

#### 1. Регистрация
1. Зайдите на https://www.serv00.com
2. Зарегистрируйтесь (без карты)
3. Дождитесь подтверждения аккаунта

#### 2. Подключение по SSH
```bash
# С вашего Mac
ssh ваш_логин@serv00.com
```

#### 3. Установка бота
```bash
# Создайте директорию
mkdir ~/bot && cd ~/bot

# Загрузите файлы через SFTP
# С Mac:
# sftp ваш_логин@serv00.com
# put -r "/Users/j/telegram autoban bot/" ~/bot/
```

Или через git:
```bash
cd ~/bot
git clone https://github.com/ВАШ_НИК/telegram-autoban-bot.git .
```

#### 4. Установка Python
```bash
# На Serv00 Python обычно предустановлен
python3 --version

# Если нет, используйте devpkg
devpkg install python3
```

#### 5. Установка зависимостей
```bash
cd ~/bot
python3 -m pip install --user -r requirements.txt
```

#### 6. Создание .env
```bash
nano .env
# Вставьте переменные и сохраните (Ctrl+O, Enter, Ctrl+X)
```

#### 7. Запуск через tmux (24/7)
```bash
# Установите tmux если нет
devpkg install tmux

# Создайте сессию
tmux new -s bot

# Запустите бота
cd ~/bot
python3 bot.py

# Отключитесь от сессии (бот продолжит работать)
# Нажмите: Ctrl+B, затем D

# Подключиться обратно:
tmux attach -t bot
```

---

## 🥉 Вариант 3: Alwaysdata (ПРОСТОЙ ХОСТИНГ)

**Плюсы:**
- ✅ Навсегда бесплатно, карта НЕ нужна
- ✅ 1GB SSD, 256MB RAM
- ✅ Поддержка Python

**Минусы:**
- ⚠️ Мало RAM (256MB)
- ⚠️ Медленный CPU (¼ ядра)

### Инструкция:

#### 1. Регистрация
1. Зайдите на https://www.alwaysdata.com
2. Нажмите **Sign up**
3. Карта НЕ нужна

#### 2. Создание Python приложения
1. В панели управления: **Application** → **Add**
2. Type: **Python**
3. Command: `python bot.py`
4. Working directory: `/www`

#### 3. Загрузка файлов
1. Перейдите в **Files**
2. Загрузите все файлы через FTP или файловый менеджер
3. Создайте `.env` с вашими переменными

#### 4. Установка зависимостей
```bash
# Через SSH или веб-консоль
cd /www
pip install -r requirements.txt --target=.
```

#### 5. Запуск
1. В панели: **Application** → запустите ваше приложение
2. Бот будет работать 24/7

---

## 🔄 Вариант 4: Render + Webhook (С ОБХОДОМ СНА)

**Плюсы:**
- ✅ Бесплатно навсегда, карта НЕ нужна
- ✅ Деплой из GitHub одной кнопкой

**Минусы:**
- ❌ Засыпает через 15 мин без запросов
- ❌ Polling НЕ работает
- ⚠️ Нужен webhook + пинг через UptimeRobot

### Инструкция:

#### 1. Подготовьте webhook версию бота

Создайте файл `webhook_bot.py`:

```python
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
TARGET_CHAT_ID = os.getenv("TARGET_CHAT_ID")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
WEB_HOST = os.getenv("WEB_HOST", "0.0.0.0")
WEB_PORT = int(os.getenv("WEB_PORT", 8080))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

banned_users = set()
subscribers_cache = {}


async def ban_user(user_id: int, reason: str = "Отписка") -> bool:
    if user_id in banned_users:
        return False
    try:
        await bot.ban_chat_member(
            chat_id=TARGET_CHAT_ID,
            user_id=user_id,
            until_date=int((datetime.now() + timedelta(days=365)).timestamp())
        )
        banned_users.add(user_id)
        logger.info(f"Забанен {user_id}")
        await bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🔨 Забанен: {user_id}\nПричина: {reason}"
        )
        return True
    except Exception as e:
        logger.error(f"Ошибка бана: {e}")
        return False


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔️ Нет доступа")
        return
    await message.answer("🤖 Бот работает на webhook!")


@dp.chat_member()
async def handle_chat_member(update: types.ChatMemberUpdated):
    old = update.old_chat_member.status
    new = update.new_chat_member.status
    user_id = update.from_user.id

    if old in ["member", "administrator"] and new in ["left", "kicked"]:
        await ban_user(user_id, "Отписка от канала")
    elif new == "member":
        subscribers_cache[user_id] = datetime.now()


async def on_startup(bot: Bot):
    """Настройка webhook при запуске"""
    webhook_url = f"{os.getenv('PUBLIC_URL')}/webhook"
    await bot.set_webhook(webhook_url)
    logger.info(f"Webhook установлен: {webhook_url}")


# Flask/FastAPI для keep-alive пингов
async def health_check(request):
    """Эндпоинт для пинга (чтобы Render не спал)"""
    return web.Response(text="OK")


async def main():
    # Запускаем бота
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

    logger.info(f"Сервер запущен на порту {WEB_PORT}")

    # Бесконечный цикл
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен")
```

Создайте `Procfile`:
```
web: python webhook_bot.py
```

Создайте `runtime.txt`:
```
python-3.12.0
```

#### 2. Деплой на Render

1. Зайдите на https://render.com
2. Sign up через GitHub (без карты)
3. **New** → **Web Service**
4. Подключите ваш GitHub репозиторий
5. Настройки:
   - Name: `telegram-autoban-bot`
   - Environment: `Python`
   - Build: `pip install -r requirements.txt`
   - Start: `python webhook_bot.py`
6. Добавьте Environment Variables:
   ```
   BOT_TOKEN=...
   CHANNEL_ID=...
   TARGET_CHAT_ID=...
   ADMIN_ID=...
   PUBLIC_URL=https://ваше-приложение.onrender.com
   ```
7. **Deploy**

#### 3. Настройка пинга (чтобы не спал)

1. Зайдите на https://uptimerobot.com
2. Зарегистрируйтесь (бесплатно, без карты)
3. Добавьте монитор:
   - Type: **HTTP(s)**
   - URL: `https://ваше-приложение.onrender.com/health`
   - Interval: **Every 5 minutes**
4. Это будет пинговать ваш сервис и не даст уснуть

---

## 🏠 Вариант 5: Self-Hosted (СВОЙ КОМПЬЮТЕР)

**Плюсы:**
- ✅ Полный контроль
- ✅ Без ограничений
- ✅ Бесплатно

**Минусы:**
- ⚠️ Компьютер должен быть включен
- ⚠️ Нужен белый IP для webhook (или используйте polling)

### Инструкция:

```bash
cd "/Users/j/telegram autoban bot"

# Установите зависимости
pip install -r requirements.txt

# Запустите
python bot.py
```

Для 24/7 работы Mac:
- System Preferences → Energy Saver → Prevent computer from sleeping
- Или используйте cron для автозапуска

---

## 🎯 Итоговая рекомендация

| Для чего | Что выбрать |
|----------|-------------|
| **Самый простой** | PythonAnywhere |
| **Лучший бесплатный VPS** | Serv00 |
| **Для продакшена бесплатно** | Serv00 или Alwaysdata |
| **С GitHub деплоем** | Render + UptimeRobot |
| **Максимум ресурсов** | Oracle Cloud (НО нужна карта) |

## ⚡ Быстрый старт за 10 минут (Serv00):

```bash
# 1. Зарегистрируйтесь на serv00.com

# 2. Подключитесь
ssh ваш_логин@serv00.com

# 3. Создайте и запустите
mkdir ~/bot && cd ~/bot
# Загрузите файлы через SFTP
pip install -r requirements.txt
nano .env  # вставьте переменные
tmux new -s bot
python3 bot.py
# Ctrl+B, D - отключиться (бот работает)
```

## ⚡ Быстрый старт за 5 минут (PythonAnywhere):

```bash
# 1. Зарегистрируйтесь на pythonanywhere.com

# 2. Откройте Bash консоль
mkdir ~/bot && cd ~/bot

# 3. Установите зависимости
pip install aiogram python-dotenv

# 4. Загрузите файлы через Files менеджер

# 5. Запустите
python bot.py
# (держите вкладку открытой)
```

## 🔧 Troubleshooting

### Бот не запускается:
- Проверьте что все зависимости установлены
- Проверьте `.env` переменные
- Смотрите логи ошибки

### PythonAnywhere бот останавливается:
- Откройте консоль снова
- Убедитесь что аккаунт активен (войдите раз в месяц)

### Serv00 бот упал:
```bash
tmux attach -t bot  # подключиться
# Если сессия убита - запустите снова:
tmux new -s bot
cd ~/bot && python3 bot.py
```

### Render засыпает:
- Убедитесь что UptimeRobot настроен
- Проверьте что `/health` эндпоинт работает

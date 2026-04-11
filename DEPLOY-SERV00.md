# 🚀 Деплой на Serv00

**Время: 10 минут. Цена: Бесплатно. Карта: НЕ нужна.**

---

## Шаг 1: Регистрация (2 минуты)

1. Открой https://www.serv00.com
2. Нажми **Sign Up** / **Register**
3. Заполни:
   - Login (придумай имя)
   - Email
   - Пароль
4. **Отправь форму**
5. ⏳ Жди подтверждения на email (обычно 1-24 часа)

> ⚠️ Если аккаунт не одобрили — попробуй другой логин или напиши в поддержку. Количество бесплатных аккаунтов ограничено.

---

## Шаг 2: Подключение по SSH (1 минута)

Когда получишь письмо об активации:

```bash
# Открой Терминал на Mac и введи:
ssh твой_логин@serv00.com
```

Первый раз спросит добавить fingerprint — введи `yes`.

---

## Шаг 3: Подготовка окружения (2 минуты)

После входа по SSH выполни:

```bash
# Проверь Python (должен быть установлен)
python3 --version

# Создай директорию для бота
mkdir ~/bot && cd ~/bot
```

---

## Шаг 4: Загрузка файлов (2 минуты)

### Способ A: Через git (рекомендую)

```bash
# Сначала на Mac (в НОВОМ окне терминала):
cd "/Users/j/telegram autoban bot"
git init && git add . && git commit -m "bot"

# Создай репозиторий на GitHub:
# https://github.com/new → autoban-bot → Create

# Push:
git branch -M main
git remote add origin https://github.com/ТВОЙ_НИК/autoban-bot.git
git push -u origin main

# Теперь обратно на сервере (по SSH):
cd ~/bot
git clone https://github.com/ТВОЙ_НИК/autoban-bot.git .
```

### Способ B: Через SFTP (если нет GitHub)

```bash
# На Mac (в НОВОМ окне терминала):
sftp твой_логин@serv00.com

# Внутри sftp:
cd ~/bot
put -r /Users/j/telegram\ autoban\ bot/bot.py
put -r /Users/j/telegram\ autoban\ bot/requirements.txt
put -r /Users/j/telegram\ autoban\ bot/main.py
quit
```

---

## Шаг 5: Установка зависимостей (1 минута)

```bash
cd ~/bot

# Установи зависимости
pip3 install --user -r requirements.txt
```

Если pip3 нет:
```bash
# Попробуй так:
python3 -m pip install --user -r requirements.txt

# Или установи pip:
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py --user
pip3 install --user -r requirements.txt
```

---

## Шаг 6: Создание .env (1 минута)

```bash
cd ~/bot
nano .env
```

Вставь свои данные:
```env
BOT_TOKEN=123456:ABCdefGHIjklMNOpqrs
CHANNEL_ID=-1001234567890
TARGET_CHAT_ID=-1001234567890
ADMIN_ID=1946614387
```

Сохрани: `Ctrl+O` → `Enter` → `Ctrl+X`

---

## Шаг 7: Запуск бота через tmux (1 минута)

tmux позволяет боту работать 24/7 даже после отключения от SSH.

```bash
# Создай tmux сессию с именем "bot"
tmux new -s bot

# Запусти бота
cd ~/bot
python3 bot.py
```

Бот запустится, увидишь логи. **Чтобы отключиться** (бот продолжит работать):

Нажми: **`Ctrl+B`** потом **`D`**

Теперь ты снова в обычной консоли, а бот работает.

### Полезные команды tmux:

```bash
# Подключиться обратно к боту:
tmux attach -t bot

# Посмотреть все сессии:
tmux ls

# Убить сессию:
tmux kill-session -t bot
```

---

## Шаг 8: Проверь (30 секунд)

Открой Telegram и напиши боту:
```
/start
```

Бот ответил? **Готово!** ✅

---

## Автозапуск при перезагрузке (опционально)

Чтобы бот запускался сам после перезагрузки сервера:

```bash
# Добавь в crontab:
crontab -e

# Вставь эту строку:
@reboot cd ~/bot && /usr/bin/python3 bot.py > ~/bot/bot.log 2>&1 &
```

---

## Если что-то пошло не так

### Python не найден:
```bash
# Проверь где он:
which python3
ls /usr/bin/python*

# Или попробуй:
python --version
```

### pip не установлен:
```bash
# Скачай и установи:
cd ~
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py --user

# Добавь в PATH:
echo 'export PATH=$HOME/.local/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

### Бот упал:
```bash
# Подключись к tmux и посмотри что случилось:
tmux attach -t bot

# Перезапусти:
cd ~/bot
python3 bot.py
```

### Бот не отвечает на /start:
1. Проверь что бот запущен: `tmux ls`
2. Проверь логи внутри tmux: `tmux attach -t bot`
3. Проверь .env — все переменные правильные?
4. Проверь что токен бота рабочий

---

## 📋 Чеклист

- [ ] Зарегистрировался на Serv00
- [ ] Получил письмо об активации
- [ ] Подключился по SSH
- [ ] Создал ~/bot директорию
- [ ] Загрузил файлы (git или SFTP)
- [ ] Установил зависимости
- [ ] Создал .env с переменными
- [ ] Запустил через tmux
- [ ] Бот ответил на /start

---

## 💡 Советы

1. **Не закрывай tmux сессию** через `exit` — используй `Ctrl+B, D`
2. **Проверяй бота раз в день**: `tmux attach -t bot`
3. **Логи бота** можно смотреть внутри tmux или перенаправить в файл
4. **Для обновления кода**:
   ```bash
   tmux kill-session -t bot
   cd ~/bot && git pull
   python3 bot.py  # в новой tmux сессии
   ```

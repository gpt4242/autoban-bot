# 🚀 Деплой в 1 клик — Render

**5 минут. Бесплатно. Без карты.**

---

## Всё в одном: скопируй и вставь

### 1. Git + GitHub (2 мин)

```bash
# === СКОПИРУЙ ВСЁ ОТ СЮДА ===
cd "/Users/j/telegram autoban bot"

git init
git add .
git commit -m "Автобан бот"
# === ДО СЮДА ===
```

Теперь:
1. Открой https://github.com/new
2. Name: `autoban-bot`, **Public**
3. Create

```bash
# === ВСТАВЬ СВОЮ ССЫЛКУ ===
git branch -M main
git remote add origin https://github.com/ТВОЙ_НИК/autoban-bot.git
git push -u origin main
# === КОНЕЦ ===
```

---

### 2. Render (2 мин)

1. Открой https://render.com → **Sign Up** → **GitHub**
2. Dashboard → **New +** → **Web Service**
3. Выбери `autoban-bot` → **Connect**
4. Заполни:

```
Name:          autoban-bot
Region:        Frankfurt
Branch:        main
Runtime:       Python 3
Build Command: pip install -r requirements.txt
Start Command: python bot.py
Plan:          Free
```

5. **Environment Variables** → добавь 5 штук:

```
BOT_TOKEN        = 123456:ABCdefGHI...
CHANNEL_ID       = -1001234567890
TARGET_CHAT_ID   = -1001234567890
ADMIN_ID         = 1946614387
PUBLIC_URL       = (пока оставь пустым — заполним после деплоя)
```

6. **Create Web Service** 🚀

---

### 3. PUBLIC_URL (1 мин)

После деплоя Render покажет URL:
```
https://autoban-bot-xxxx.onrender.com
```

1. Скопируй его
2. **Environment** → найди `PUBLIC_URL` → ✏️
3. Вставь URL (без `/` в конце!)
4. Сохрани — перезапустится сам

---

### 4. Проверка (30 сек)

Напиши боту в Telegram:
```
/start
```

**Ответил?** ✅ Готово!

---

## Чеклист

- [ ] Получил токен у @BotFather
- [ ] Бот — админ канала
- [ ] Бот — админ группы (право "Банить")
- [ ] Узнал CHANNEL_ID (через @RawDataBot)
- [ ] Узнал TARGET_CHAT_ID
- [ ] Узнал ADMIN_ID (через @userinfobot)
- [ .git push на GitHub
- [ ] Создал сервис на Render
- [ ] Добавил 4 env переменные
- [ ] Добавил PUBLIC_URL после деплоя
- [ ] Бот ответил на /start

---

## Troubleshooting

### Бот молчит:
```
Render Dashboard → Logs → ищи красные строки
```

### Ошибка webhook:
```
PUBLIC_URL = https://autoban-bot-xxxx.onrender.com
БЕЗ слеша на конце!
```

### Обновить код:
```bash
git add . && git commit -m "fix" && git push
# Render обновит сам
```

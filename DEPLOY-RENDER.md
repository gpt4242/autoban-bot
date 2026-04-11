# 🚀 Деплой на Render

**Время: 5 минут. Цена: Бесплатно. Карта: НЕ нужна.**
**Бот сам себя пингует — UptimeRobot НЕ нужен!**

---

## Шаг 1: Залей на GitHub

```bash
cd "/Users/j/telegram autoban bot"
git init
git add .
git commit -m "🤖 Автобан бот"
```

Создай репозиторий: https://github.com/new
- Name: `autoban-bot`
- **Public**
- Create

```bash
git branch -M main
git remote add origin https://github.com/ТВОЙ_НИК/autoban-bot.git
git push -u origin main
```

---

## Шаг 2: Регистрация на Render

1. https://render.com → **Sign Up**
2. **Continue with GitHub**
3. ✅ Карта НЕ нужна

---

## Шаг 3: Деплой

1. https://dashboard.render.com → **New +** → **Web Service**
2. Подключи репозиторий `autoban-bot` → **Connect**
3. Заполни:

| Поле | Значение |
|------|----------|
| **Name** | `autoban-bot` |
| **Region** | Frankfurt (Europe) |
| **Branch** | `main` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python bot.py` |
| **Plan** | **Free** |

4. **Environment Variables** → добавь:

```
BOT_TOKEN        = 123456:ABCdef...
CHANNEL_ID       = -1001234567890
TARGET_CHAT_ID   = -1001234567890
ADMIN_ID         = 1946614387
```

5. Нажми **Create Web Service** 🎉

---

## Шаг 4: Добавь PUBLIC_URL

После деплоя Render покажет URL:
```
https://autoban-bot-xxxx.onrender.com
```

1. Иди в **Environment** → найди `PUBLIC_URL`
2. Если нет — добавь новую переменную:

```
PUBLIC_URL = https://autoban-bot-xxxx.onrender.com
```

(без `/` в конце!)

3. Сохрани — сервис перезапустится сам

---

## Шаг 5: Проверь

Напиши боту в Telegram:
```
/start
```

Ответил? **Готово!** ✅

Бот сам пингует себя каждые 3 минуты — Render не будет его усыплять.

---

## Как работает self-ping

```
Бот запущен
    ↓
Каждые 3 мин пингует свой /health
    ↓
Render видит трафик → НЕ усыпляет
    ↓
Отписка → бот ловит webhook → банит мгновенно
```

---

## Обновление кода

```bash
# Внеси изменения в bot.py
git add . && git commit -m "fix" && git push
```

Render подхватит изменения автоматически.

---

## Troubleshooting

### Бот не отвечает:
1. Render Dashboard → Logs → ищи ошибки
2. Проверь что PUBLIC_URL правильный (без `/` в конце)

### Ошибка webhook:
```
PUBLIC_URL должен быть: https://имя.onrender.com
НЕ: https://имя.onrender.com/
```

### Бот не банит:
- Бот — админ канала и группы (право "Банить")
- CHANNEL_ID начинается с `-100`
- Проверь ADMIN_ID

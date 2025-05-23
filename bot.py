import requests
import time
import os
from fake_useragent import UserAgent
from telegram.ext import Application, MessageHandler, ContextTypes, filters, CommandHandler

# === Настройки ===
IDS = [
    "u-h6h42", "u-ggdd04", "u-58026", "u-6534c", "u-758che",
    "u-307hh", "u-1089c", "u-h342d", "u-g36f9", "u-gf61",
    "u-f798cf", "u-6dfc1", "u-278d9h", "u-ee5928", "u-585325",
    "u-32758", "u-9ff22", "u-045g44", "u-21f74", "u-395745"
]

API_URL = "https://www.gameloft.com/redeem/ajax/validateCode "

HELP_TEXT = """
🎮 <b>Gameloft Promo Bot</b> (v1.0)

💎 Просто отправьте промокод, и я попробую его активировать для всех ID.

📊 <b>Система отметок:</b>
🟢 — Успешная активация
🔴 — Промокод не подходит / уже использован
⚡ — Ошибка сети или сервера
❌ — Неверный ответ от сайта
"""


async def start(update, context):
    await update.message.reply_text(HELP_TEXT, parse_mode='HTML')


def activate_code(user_id, code):
    ua = UserAgent()
    headers = {
        "User-Agent": ua.random,
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "XMLHttpRequest"
    }
    data = {"playerId": user_id, "code": code}

    try:
        r = requests.post(API_URL, headers=headers, data=data, timeout=30)
        if r.status_code == 200:
            res = r.json()
            if res.get("success"):
                return f"🟢 {user_id}: Успешно!"
            else:
                msg = res.get("message", "Неизвестная ошибка")
                return f"🔴 {user_id}: {msg}"
        else:
            return f"❌ {user_id}: HTTP {r.status_code}"

    except requests.exceptions.RequestException as e:
        return f"⚡ {user_id}: {str(e)}"
    except Exception as e:
        return f"💥 {user_id}: {str(e)}"


async def handle_promo(update, context):
    promo_code = update.message.text.strip()

    if len(promo_code) < 5:
        await update.message.reply_text("❌ Промокод должен содержать минимум 5 символов!")
        return

    progress = await update.message.reply_text("🔄 Начинаю обработку...")

    results = []
    stats = {"success": 0, "used": 0, "error": 0, "other": 0}

    for i, user_id in enumerate(IDS, 1):
        result = activate_code(user_id, promo_code)
        results.append(result)

        # Подсчёт статистики
        if "🟢" in result: stats["success"] += 1
        elif "🔴" in result: stats["used"] += 1
        elif "⚡" in result or "💥" in result: stats["error"] += 1
        else: stats["other"] += 1

        # Обновление прогресса каждые 2 сообщения
        if i % 2 == 0:
            await progress.edit_text(
                f"⏳ Прогресс: {i}/{len(IDS)}\n"
                f"🟢 Успех: {stats['success']} | 🔴 Использован: {stats['used']}\n"
                f"⚡ Ошибок: {stats['error']} | ❌ Другие: {stats['other']}"
            )
        time.sleep(2)  # Чтобы не было блокировки

    report = [
        f"📊 <b>Итоговый отчет</b>",
        f"🟢 Успех: {stats['success']}",
        f"🔴 Использован: {stats['used']}",
        f"⚡ Ошибок: {stats['error']}",
        f"❌ Другие: {stats['other']}",
        "",
        "<b>Подробности:</b>",
        *results
    ]

    await progress.edit_text("\n".join(report), parse_mode='HTML')


def main():
    TOKEN = os.getenv("TOKEN", "7602499396:AAHNPjlPymZYTc2bxipow5jOB_35fzZaC20")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_promo))
    app.add_handler(CommandHandler("start", start))

    app.run_polling()


if __name__ == '__main__':
    main()

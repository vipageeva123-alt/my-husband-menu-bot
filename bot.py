import os
import random
import logging
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

PORT = int(os.getenv("PORT", "10000"))


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        return


def start_web_server():
    server = ThreadingHTTPServer(("0.0.0.0", PORT), HealthHandler)
    server.serve_forever()


BREAKFASTS = [
    "🍳 Яичница с сыром + тосты + авокадо 🥑",
    "🥞 Сырники со сметаной и ягодами",
    "🥪 Горячие бутерброды с сыром и ветчиной",
    "🥣 Овсянка с бананом, ягодами и орехами",
    "🍳 Омлет с сыром и овощами",
]

LUNCHES = [
    "🍗 Курица с картофелем + овощной салат",
    "🍝 Паста с курицей в сливочном соусе",
    "🍚 Плов + свежие овощи",
    "🥩 Котлета/стейк + пюре + салат",
    "🍲 Суп + горячий бутерброд",
]

DINNERS = [
    "🍝 Паста с томатным или сливочным соусом",
    "🥩 Стейк + овощи",
    "🍣 Суши — сегодня можно не готовить 😏",
    "🍕 Пицца — если жена тоже согласна ❤️",
    "🥔 Пюре + котлеты + огурчики",
    "🍗 Запечённая курица + овощи",
]

TREATS = [
    "🍫 Шоколад",
    "🍓 Клубника со сливками",
    "🍰 Чизкейк",
    "🍦 Мороженое",
    "🥐 Круассан",
    "🍪 Печенье с чаем",
]

WIFE_ADVICE = [
    "❤️ Поешь нормально, а не опять «я потом поем».",
    "😘 Подойди к жене и поцелуй её. Это важнее еды.",
    "😌 Сегодня можно что-нибудь вкусное. Жена разрешила.",
    "👀 Не забывай: жена всё видит.",
    "❤️ Если сомневаешься — выбирай то, что любит жена.",
    "🥰 Хорошего тебе аппетита, любимый!",
]

HUNGER = {
    "a_little": [
        "🥪 Небольшой перекус: бутерброд + чай.",
        "🍌 Банан + йогурт.",
        "🥣 Небольшая порция овсянки.",
    ],
    "normal": [
        "🍝 Паста + салат.",
        "🍗 Курица + гарнир + овощи.",
        "🍚 Рис/гречка + мясо + салат.",
    ],
    "very": [
        "🔴 Срочно кормить! Большая порция мяса + гарнир + салат.",
        "🔴 Холодильник в опасности. Заказываем нормальный ужин.",
        "🔴 Ты официально достиг стадии «съем холодильник». Пора есть!",
    ],
}

def main_menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🍳 Завтрак", callback_data="breakfast"),
            InlineKeyboardButton("🍲 Обед", callback_data="lunch"),
        ],
        [
            InlineKeyboardButton("🍝 Ужин", callback_data="dinner"),
            InlineKeyboardButton("🍫 Вкусненькое", callback_data="treat"),
        ],
        [
            InlineKeyboardButton("🍽 Я голодный", callback_data="hungry"),
            InlineKeyboardButton("❤️ Что жена советует?", callback_data="advice"),
        ],
    ])

def back_button():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Другой вариант", callback_data="repeat")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="home")],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["last_category"] = None
    text = (
        "Привет, любимый ❤️\n\n"
        "Здесь собраны маленькие подсказки от твоей жены, "
        "чтобы тебе было проще решить, что сегодня поесть 😘\n\n"
        "Что выбираем?"
    )
    await update.message.reply_text(text, reply_markup=main_menu())

async def choose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    category = query.data

    # Запоминаем только категории блюд.
    # Благодаря этому «🔄 Другой вариант» работает корректно.
    if category in ("breakfast", "lunch", "dinner", "treat"):
        context.user_data["last_category"] = category

    if category == "breakfast":
        text = f"☀️ Сегодня на завтрак:\n\n{random.choice(BREAKFASTS)}\n\n❤️ Одобрено женой."
    elif category == "lunch":
        text = f"🍲 Сегодня на обед:\n\n{random.choice(LUNCHES)}\n\n😋 Приятного аппетита!"
    elif category == "dinner":
        text = f"🌙 Сегодня на ужин:\n\n{random.choice(DINNERS)}\n\n❤️ Выбирай с любовью."
    elif category == "treat":
        text = f"🍫 Жена разрешила вкусненькое:\n\n{random.choice(TREATS)}\n\n😏 Но только немного!"
    elif category == "advice":
        text = random.choice(WIFE_ADVICE)
    elif category == "hungry":
        text = (
            "🍽 Насколько ты голодный?\n\n"
            "Выбирай честно — холодильник всё равно всё знает 😄"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔹 Немного", callback_data="h_a_little")],
            [InlineKeyboardButton("🔸 Нормально", callback_data="h_normal")],
            [InlineKeyboardButton("🔴 Я съем холодильник", callback_data="h_very")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="home")],
        ])
        await query.edit_message_text(text, reply_markup=keyboard)
        return
    elif category == "home":
        await query.edit_message_text(
            "❤️ Ну что, любимый, выбирай:",
            reply_markup=main_menu(),
        )
        return
    elif category == "repeat":
        last = context.user_data.get("last_category")
        if last in ("breakfast", "lunch", "dinner", "treat"):
            category = last
            menus = {
                "breakfast": BREAKFASTS,
                "lunch": LUNCHES,
                "dinner": DINNERS,
                "treat": TREATS,
            }
            text = (
                f"🔄 Тогда ещё вариант:\n\n"
                f"{random.choice(menus[category])}"
            )
            await query.edit_message_text(
                text,
                reply_markup=back_button(),
            )
            return
        await query.edit_message_text("❤️ Выбирай:", reply_markup=main_menu())
        return
    else:
        mapping = {
            "h_a_little": HUNGER["a_little"],
            "h_normal": HUNGER["normal"],
            "h_very": HUNGER["very"],
        }
        if category in mapping:
            text = random.choice(mapping[category])
        else:
            text = "❤️ Выбирай:"
            await query.edit_message_text(text, reply_markup=main_menu())
            return

    await query.edit_message_text(text, reply_markup=back_button())

def run():
    if not TOKEN:
        raise RuntimeError(
            "Не задан TELEGRAM_BOT_TOKEN..."
        )

    web_thread = threading.Thread(
        target=start_web_server,
        daemon=True
    )
    web_thread.start()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(choose))
    logging.info("Telegram bot is starting...")
    app.run_polling()


if __name__ == "__main__":
    run()

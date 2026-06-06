import os
import logging

from dotenv import load_dotenv

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

from src import bot_handlers


# =========================
# LOGGING
# =========================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)


# =========================
# ENV
# =========================

load_dotenv()

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("TOKEN environment variable not set")


# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    questions = context.bot_data["questions"]

    topics = bot_handlers.get_topics(questions)

    keyboard = []

    for topic in topics:
        keyboard.append([
            InlineKeyboardButton(
                topic,
                callback_data=f"topic:{topic}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "🎲 Все темы",
            callback_data="topic:all"
        )
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "📚 Выбери тему:",
        reply_markup=reply_markup
    )


# =========================
# TOPIC SELECT
# =========================

async def choose_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    topic = query.data.split(":")[1]

    context.user_data["topic"] = topic

    await send_question(query, context)


# =========================
# SEND QUESTION
# =========================

async def send_question(query, context):

    topic = context.user_data.get("topic", "all")

    question = bot_handlers.get_question(
        context.bot_data["questions"],
        topic
    )

    context.user_data["current_question"] = question

    keyboard = []

    for option in question["options"]:
        keyboard.append([
            InlineKeyboardButton(
                option,
                callback_data=f"answer:{option}"
            )
        ])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"🧠 Тема: {question['topic']}\n\n"
        f"{question['question']}",
        reply_markup=reply_markup
    )


# =========================
# ANSWER
# =========================

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    current_question = context.user_data.get("current_question")

    if not current_question:
        await query.edit_message_text("❌ Вопрос не найден")
        return

    user_answer = query.data.split("answer:")[1]

    if user_answer == current_question["correct"]:

        text = (
            "✅ Правильно!\n\n"
            f"{current_question['question']}"
        )

    else:

        text = (
            "❌ Неправильно\n\n"
            f"💡 Подсказка:\n{current_question['hint']}"
        )

    keyboard = [[
        InlineKeyboardButton(
            "➡️ Следующий вопрос",
            callback_data="next"
        )
    ]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text,
        reply_markup=reply_markup
    )


# =========================
# NEXT QUESTION
# =========================

async def next_question(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    await send_question(query, context)


# =========================
# ERRORS
# =========================

async def error_handler(update, context):

    logger.error(
        msg="Exception while handling update:",
        exc_info=context.error
    )


# =========================
# MAIN
# =========================

def main():

    app = ApplicationBuilder().token(TOKEN).build()

    questions = bot_handlers.load_questions()

    app.bot_data["questions"] = questions

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        CallbackQueryHandler(
            choose_topic,
            pattern=r"^topic:"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            handle_answer,
            pattern=r"^answer:"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            next_question,
            pattern=r"^next$"
        )
    )

    app.add_error_handler(error_handler)

    print("🚀 BOT STARTED")

    app.run_polling()


if __name__ == "__main__":
    main()
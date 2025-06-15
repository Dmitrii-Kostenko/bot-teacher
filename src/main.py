# # src/main.py


import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

import bot_handlers

# Логирование ошибок
import logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Загрузка токена из .env
load_dotenv()
TOKEN = os.getenv("TOKEN")

# Обработчик ошибок
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.warning('⚠️ Произошла ошибка: %s', context.error)

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет, {user.mention_html()}! 👋\n"
        "Нажми '🔄 Случайный вопрос', чтобы начать.",
    )

    # Кнопка для случайного вопроса
    keyboard = [[InlineKeyboardButton("🔄 Случайный вопрос", callback_data="random")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выбирай!", reply_markup=reply_markup)

# Получаем случайный вопрос
async def handle_random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        question = bot_handlers.get_question(context.bot_data["questions"])
        context.user_data["current_question"] = question

        buttons = [[InlineKeyboardButton(option, callback_data=option) for option in question["options"]]]
        reply_markup = InlineKeyboardMarkup(buttons)

        await query.edit_message_text(text=f"🧠 Вопрос: {question['question']}")
        await query.message.reply_text("Выбери правильный вариант:", reply_markup=reply_markup)

    except Exception as e:
        logger.error("Ошибка при получении вопроса: %s", str(e))
        await query.message.reply_text("❌ Не удалось получить вопрос. Попробуй ещё раз.")

# Проверяем ответ
async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    current_q = context.user_data.get("current_question")

    if not current_q:
        await query.edit_message_text("❌ Нет активного вопроса")
        return

    user_answer = query.data
    correct = current_q["correct"]
    hint = current_q.get("hint", "Подсказка отсутствует")

    if user_answer == correct:
        await query.edit_message_text(f"✅ Верно!\n\n{current_q['question']}")
    else:
        await query.edit_message_text(f"❌ Неверно.\nПодсказка: {hint}")

    # Кнопка следующего вопроса
    next_btn = [[InlineKeyboardButton("🔄 Следующий", callback_data="random")]]
    reply_markup = InlineKeyboardMarkup(next_btn)
    await query.message.reply_text("Нажми ниже:", reply_markup=reply_markup)

# Главная точка входа
if __name__ == '__main__':
    print("🚀 Бот стартовал...")

    try:
        # Создание приложения
        application = ApplicationBuilder().token(TOKEN).build()

        # Регистрация обработчика ошибок
        application.add_error_handler(error_handler)

        # Регистрация обработчиков
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CallbackQueryHandler(handle_random, pattern="^random$"))
        application.add_handler(CallbackQueryHandler(handle_answer))

        # Загрузка вопросов
        application.bot_data["questions"] = bot_handlers.load_questions()
        print("📚 Вопросы загружены")

    except Exception as e:
        print("❌ Ошибка загрузки вопросов:", str(e))
        exit()

    print("📡 Бот запущен...")
    application.run_polling()
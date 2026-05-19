import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

# ── Настройки ──────────────────────────────────────────────────────────────
import os
TOKEN = os.getenv("8939700240:AAHAAzM89yvCIhdIxsW8YZzZ3KKbjUhAD9c")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ── Состояния разговора ────────────────────────────────────────────────────
ASKING = range(1)

# ── Вопросы теста (10 штук) ────────────────────────────────────────────────
QUESTIONS = [
    "1️ Вы часто чувствуете усталость даже после полноценного сна?",
    "2️ У вас бывают частые головные боли или напряжение в шее/плечах?",
    "3️ Вам трудно сосредоточиться на задачах в течение дня?",
    "4️ Вы раздражаетесь по мелочам или срываетесь на близких?",
    "5️ Вы чувствуете тревогу или беспокойство без явной причины?",
    "6️ У вас нарушен сон (трудно засыпать или часто просыпаетесь)?",
    "7️ Вы избегаете общения с людьми или социальных мероприятий?",
    "8️ Вы чувствуете, что у вас слишком много дел и не хватает времени?",
    "9️ Вы часто едите «на бегу» или пропускаете приёмы пищи?",
    "10 У вас снизился интерес к хобби или занятиям, которые раньше нравились?",
]

# ── Клавиатура Да / Нет ────────────────────────────────────────────────────
YES_NO_KEYBOARD = ReplyKeyboardMarkup(
    [["✅ Да", "❌ Нет"]],
    resize_keyboard=True,
    one_time_keyboard=True,
)


# ── Результат по баллам ────────────────────────────────────────────────────
def get_result(score: int) -> str:
    if score <= 3:
        return (
            " *Уровень 1 — Низкий стресс*\n\n"
            "Вы справляетесь со стрессом отлично! "
            "Продолжайте поддерживать здоровый режим дня, заниматься физической активностью "
            "и уделять время отдыху. Ваш организм в хорошем балансе."
        )
    elif score <= 6:
        return (
            " *Уровень 2 — Умеренный стресс*\n\n"
            "У вас есть признаки умеренного стресса. Рекомендуется:\n"
            "• Делать короткие перерывы в работе каждые 1–1.5 часа\n"
            "• Практиковать глубокое дыхание или медитацию (10 мин/день)\n"
            "• Уделять внимание качеству сна (7–8 часов)\n"
            "• Ограничить потребление кофеина и экранное время перед сном"
        )
    else:
        return (
            " *Уровень 3 — Высокий стресс*\n\n"
            "Ваш уровень стресса высокий. Это серьёзный сигнал организма. "
            "Настоятельно рекомендуется:\n"
            "• Обратиться к психологу или врачу\n"
            "• Пересмотреть нагрузку и делегировать задачи\n"
            "• Включить ежедневную физическую активность (прогулки, йога)\n"
            "• Найти поддержку у близких людей\n"
            "• Снизить потребление алкоголя и кофеина\n\n"
            "⚠️ Хронический стресс негативно влияет на здоровье — не откладывайте заботу о себе!"
        )


# ── Хендлеры ──────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало теста."""
    context.user_data["score"] = 0
    context.user_data["q_index"] = 0

    await update.message.reply_text(
        "Привет! Я помогу оценить твой *уровень стресса*.\n\n"
        "Тест состоит из 10 вопросов. Отвечай честно — только *Да* или *Нет*.\n\n"
        "Давай начнём! ",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )

    await update.message.reply_text(
        QUESTIONS[0],
        reply_markup=YES_NO_KEYBOARD,
    )
    return ASKING


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка ответа пользователя."""
    text = update.message.text.strip()
    q_index = context.user_data.get("q_index", 0)

    if "Да" in text:
        context.user_data["score"] = context.user_data.get("score", 0) + 1
    elif "Нет" in text:
        pass  # 0 баллов за «Нет»
    else:
        await update.message.reply_text(
            "Пожалуйста, выбери *Да* или *Нет* на клавиатуре 👇",
            parse_mode="Markdown",
            reply_markup=YES_NO_KEYBOARD,
        )
        return ASKING

    q_index += 1
    context.user_data["q_index"] = q_index

    if q_index < len(QUESTIONS):
        # Следующий вопрос
        await update.message.reply_text(
            QUESTIONS[q_index],
            reply_markup=YES_NO_KEYBOARD,
        )
        return ASKING
    else:
        # Тест завершён
        score = context.user_data["score"]
        result = get_result(score)

        await update.message.reply_text(
            f" *Тест завершён!*\n\nТвой результат: *{score}/10*\n\n{result}",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup(
                [["/start"]],
                resize_keyboard=True,
            ),
        )
        return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена теста."""
    await update.message.reply_text(
        "Тест отменён. Напиши /start чтобы начать заново.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


# ── Запуск бота ───────────────────────────────────────────────────────────
def main() -> None:
    app = Application.builder().token(TOKEN).proxy("socks5://127.0.0.1:1080").build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASKING: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    print("🤖 Бот запущен! Нажмите Ctrl+C для остановки.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

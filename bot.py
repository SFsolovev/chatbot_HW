import asyncio
import logging
import os, sys
import telebot
from collections import Counter
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

load_dotenv()

TOKEN = os.getenv("TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

logging.basicConfig(level=logging.INFO)

ANIMALS = {
    "manul": {
        "name": "манул",
        "photo": "https://upload.wikimedia.org/wikipedia/commons/d/d6/Manoel.jpg",
        "text": "Ты манул: независимый, внимательный и немного загадочный.",
    },
    "capybara": {
        "name": "капибара",
        "photo": "https://upload.wikimedia.org/wikipedia/commons/8/8e/Capybara_%28Hydrochoerus_hydrochaeris%29.JPG",
        "text": "Ты капибара: спокойный дипломат и мастер дружелюбной атмосферы.",
    },
    "porcupine": {
        "name": "дикобраз",
        "photo": "https://upload.wikimedia.org/wikipedia/commons/6/6b/Hystrix_cristata_qtl1.jpg",
        "text": "Ты дикобраз: ценишь личные границы и умеешь защищать своё пространство.",
    },
    "bushdog": {
        "name": "кустарниковая собака",
        "photo": "https://upload.wikimedia.org/wikipedia/commons/f/fc/Bush_dog_Speothos_venaticus.jpg",
        "text": "Ты кустарниковая собака: командный игрок, которому важны свои.",
    },
    "leopard": {
        "name": "дальневосточный леопард",
        "photo": "https://upload.wikimedia.org/wikipedia/commons/b/b7/Amur_Leopard_Panthera_pardus_orientalis_Facing_Forward_1761px.jpg",
        "text": "Ты дальневосточный леопард: редкий, собранный и очень харизматичный.",
    },
}

QUESTIONS = [
    {
        "text": "Где вам комфортнее?",
        "answers": [
            ("В уединённом уютном месте", "manul"),
            ("У воды и с компанией", "capybara"),
            ("Там, где уважают дистанцию", "porcupine"),
            ("В дружной команде", "bushdog"),
            ("На большой территории без суеты", "leopard"),
        ],
    },
    {
        "text": "Ваш стиль общения?",
        "answers": [
            ("Смотрю сурово, но я милый", "manul"),
            ("Дружу почти со всеми", "capybara"),
            ("Не трогайте меня без предупреждения", "porcupine"),
            ("Всё делаем вместе", "bushdog"),
            ("Молчаливый профессионал", "leopard"),
        ],
    },
    {
        "text": "Ваш суперскилл?",
        "answers": [
            ("Незаметность", "manul"),
            ("Спокойствие", "capybara"),
            ("Защита личных границ", "porcupine"),
            ("Командность", "bushdog"),
            ("Редкая харизма", "leopard"),
        ],
    },
]


class Quiz(StatesGroup):
    question = State()
    feedback = State()


def start_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Начать викторину", callback_data="start_quiz")],
        [InlineKeyboardButton(text="Что такое опека?", callback_data="about_guardianship")],
    ])


def question_keyboard(q_index: int):
    buttons = [
        [InlineKeyboardButton(text=text, callback_data=f"answer:{q_index}:{animal}")]
        for text, animal in QUESTIONS[q_index]["answers"]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def result_keyboard(animal_key: str):
    share_text = f"Моё тотемное животное в Московском зоопарке — {ANIMALS[animal_key]['name']}!"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Узнать об опеке", callback_data="about_guardianship")],
        [InlineKeyboardButton(text="Связаться с сотрудником", callback_data="contact")],
        [InlineKeyboardButton(text="Поделиться результатом", switch_inline_query=share_text)],
        [InlineKeyboardButton(text="Попробовать ещё раз", callback_data="start_quiz")],
        [InlineKeyboardButton(text="Оставить отзыв", callback_data="feedback")],
    ])


async def show_question(message_or_call, state: FSMContext, q_index: int):
    await state.update_data(q_index=q_index)
    text = f"Вопрос {q_index + 1}/{len(QUESTIONS)}\n\n{QUESTIONS[q_index]['text']}"
    keyboard = question_keyboard(q_index)

    if isinstance(message_or_call, CallbackQuery):
        await message_or_call.message.answer(text, reply_markup=keyboard)
    else:
        await message_or_call.answer(text, reply_markup=keyboard)


async def show_result(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    answers = data.get("answers", [])
    result = Counter(answers).most_common(1)[0][0]
    animal = ANIMALS[result]

    await state.update_data(result=result)

    caption = (
        f"🎉 Да ты {animal['name']}!\n\n"
        f"{animal['text']}\n\n"
        "💚 Вы можете поддержать животных через программу опеки Московского зоопарка: "
        "это помощь в содержании обитателей и вклад в природоохранные проекты."
    )

    await call.message.answer_photo(
        photo=animal["photo"],
        caption=caption,
        reply_markup=result_keyboard(result),
    )


bot = Bot(TOKEN)
dp = Dispatcher(storage=MemoryStorage())


@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Привет! Это викторина «Какое у вас тотемное животное?» 🐾\n"
        "Ответьте на несколько вопросов, а я подберу животное из Московского зоопарка.",
        reply_markup=start_keyboard(),
    )


@dp.callback_query(F.data == "start_quiz")
async def start_quiz(call: CallbackQuery, state: FSMContext):
    await state.set_state(Quiz.question)
    await state.update_data(answers=[])
    await show_question(call, state, 0)
    await call.answer()


@dp.callback_query(F.data.startswith("answer:"))
async def process_answer(call: CallbackQuery, state: FSMContext):
    _, q_index, animal = call.data.split(":")
    q_index = int(q_index)

    data = await state.get_data()
    answers = data.get("answers", [])
    answers.append(animal)
    await state.update_data(answers=answers)

    if q_index + 1 < len(QUESTIONS):
        await show_question(call, state, q_index + 1)
    else:
        await show_result(call, state)

    await call.answer()


@dp.callback_query(F.data == "about_guardianship")
async def about_guardianship(call: CallbackQuery):
    await call.message.answer(
        "🐾 Программа опеки — это способ поддержать животных Московского зоопарка.\n\n"
        "Опекун помогает содержать выбранное животное и участвует в добром деле сохранения редких видов.\n"
        "Подробнее: https://moscowzoo.ru/about/guardianship"
    )
    await call.answer()


@dp.callback_query(F.data == "contact")
async def contact(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    result = data.get("result", "не определён")

    await call.message.answer(
        "Напишите сотруднику: zoo@example.com\n"
        "Я уже подготовил ваш результат для передачи специалисту."
    )

    if ADMIN_CHAT_ID:
        await bot.send_message(
            ADMIN_CHAT_ID,
            f"Пользователь @{call.from_user.username} хочет узнать об опеке.\n"
            f"Результат викторины: {result}"
        )

    await call.answer()


@dp.callback_query(F.data == "feedback")
async def ask_feedback(call: CallbackQuery, state: FSMContext):
    await state.set_state(Quiz.feedback)
    await call.message.answer("Напишите, что улучшить в викторине. Нам важно ваше мнение 📝")
    await call.answer()


@dp.message(Quiz.feedback)
async def save_feedback(message: Message, state: FSMContext):
    logging.info("Feedback from %s: %s", message.from_user.id, message.text)
    await message.answer("Спасибо за отзыв! 🐾", reply_markup=start_keyboard())
    await state.clear()


async def main():
    if not TOKEN:
        raise RuntimeError("TOKEN не найден.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

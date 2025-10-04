from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from bot import admins
from aiogram.types import KeyboardButtonPollType



def main_kb(user_telegram_id: int):
    kb_list = [
        [KeyboardButton(text="Давай инлайн!")],
        [KeyboardButton(text="📖 Кто я"), KeyboardButton(text="👤 Что смогу в будущем?")],
        [KeyboardButton(text="Задать вопрос")]
    ]
    if user_telegram_id in admins:
        kb_list.append([KeyboardButton(text="⚙️ Админ панель")])
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Воспользуйтесь меню:"
    )
    return keyboard

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

def ease_link_kb():
    inline_kb_list = [
        [InlineKeyboardButton(text="Мой вк", url='https://vk.com')],
        [InlineKeyboardButton(text="Мой Telegram", url='tg://resolve?domain=')],
        [InlineKeyboardButton(text="На главную", callback_data='back_home')]


    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
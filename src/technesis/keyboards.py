from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

upload_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Загрузить файл", callback_data="upload_file")],
    ]
)

to_start_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Начало", callback_data="to_start")]
    ]
)

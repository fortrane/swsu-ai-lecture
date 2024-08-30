from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

starting_button = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Далее", callback_data="start_listening")]
])

more_info = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Узнать больше", callback_data="more_info")]
])
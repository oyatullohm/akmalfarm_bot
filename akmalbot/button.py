from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup ,ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

builder = InlineKeyboardBuilder()
builder.row(InlineKeyboardButton(text="🇺🇿  UZ", callback_data="lang_uz"))
builder.row(InlineKeyboardButton(text="🇷🇺  RU", callback_data="lang_ru"))

inline_uz_ru = builder.as_markup()

builder_text_uz = InlineKeyboardBuilder()
builder_text_uz.row(InlineKeyboardButton(text="💊 Dori haqida ma'lumot olish", callback_data="dori_info"))
builder_text_uz.row(InlineKeyboardButton(text="👨‍⚕ Shifokor bilan maslahat", callback_data="maslahat"))
builder_text_uz.row(InlineKeyboardButton(text="🧑‍⚕ Diagnostika", callback_data="diagnostika"))
builder_text_uz.row(InlineKeyboardButton(text="🚚 Yetkazib berish",url="https://akmalfarm.uz"))
builder_text_uz.row(InlineKeyboardButton(text="👨‍💼Admin bilan Aloqa", callback_data="aloqa"))
builder_text_uz.row(InlineKeyboardButton(text="🏥 Bizning dorixonalar", callback_data="dorihona_uz"))
builder_text_uz.row(InlineKeyboardButton(text="❓ Boshqa savol", callback_data="other"))
inline_uz_text = builder_text_uz.as_markup()


builder_text_ru = InlineKeyboardBuilder()
builder_text_ru.row(InlineKeyboardButton(text="💊 Получить информацию о лекарствах", callback_data="dd"))
builder_text_ru.row(InlineKeyboardButton(text="👨‍⚕ Консультация врача", callback_data="maslahat"))
builder_text_ru.row(InlineKeyboardButton(text="🧑‍⚕ Диагностика", callback_data="diagnostika"))
builder_text_ru.row(InlineKeyboardButton(text="🚚 Доставка", callback_data="delivery"))
builder_text_ru.row(InlineKeyboardButton(text="🏥 Наши аптеки", callback_data="pharmacy"))
builder_text_ru.row(InlineKeyboardButton(text="❓ Другой вопрос", callback_data="other"))

inline_ru_text = builder_text_ru.as_markup()


go_back = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Ortga", callback_data="go_back")]
    ])



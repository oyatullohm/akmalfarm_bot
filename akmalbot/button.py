from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup ,ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

builder = InlineKeyboardBuilder()
builder.row(InlineKeyboardButton(text="🇺🇿  UZ", callback_data="lang_uz"))
builder.row(InlineKeyboardButton(text="🇷🇺  RU", callback_data="lang_ru"))

inline_uz_ru = builder.as_markup()

builder_text_uz = InlineKeyboardBuilder()
builder_text_uz.row(InlineKeyboardButton(text="📄 Retsept yuklash", callback_data="aloqa"))#1
builder_text_uz.row(InlineKeyboardButton(text="🚚 Yetkazib berish",url="https://akmalfarm.uz"))#2
builder_text_uz.row(InlineKeyboardButton(text="👨‍⚕ Shifokor bilan maslahat", callback_data="maslahat"))#3
builder_text_uz.row(InlineKeyboardButton(text="👩‍⚕️ Ayollar markazi", callback_data="diagnostika"))#4
builder_text_uz.row(InlineKeyboardButton(text="🏥 Bizning dorixonalar", callback_data="dorihona_uz"))# 5
builder_text_uz.row(InlineKeyboardButton(text="💊 Katalog", callback_data="dori_info"))#6
builder_text_uz.row(InlineKeyboardButton(text="❓ Boshqa savol", callback_data="other"))#7
inline_uz_text = builder_text_uz.as_markup()


builder_text_ru = InlineKeyboardBuilder()
builder_text_ru.row(InlineKeyboardButton(text="📄 Отправить рецепт", callback_data="aloqa_ru"))#1
builder_text_ru.row(InlineKeyboardButton(text="🚚 Доставка",url="https://akmalfarm.uz"))#6
builder_text_ru.row(InlineKeyboardButton(text="👨‍⚕ Консультация врача", callback_data="maslahat_ru"))#5
builder_text_ru.row(InlineKeyboardButton(text="👩‍⚕️ Женский центр", callback_data="diagnostika_ru"))#4
builder_text_ru.row(InlineKeyboardButton(text="🏥 Наши аптеки", callback_data="dorihona_ru"))# 1 
builder_text_ru.row(InlineKeyboardButton(text="💊 Каталог", callback_data="dori_info_ru"))#2
builder_text_ru.row(InlineKeyboardButton(text="❓ Другой вопрос", callback_data="other_ru"))#7

inline_ru_text = builder_text_ru.as_markup()



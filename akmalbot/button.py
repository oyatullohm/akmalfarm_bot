from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup ,ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

builder = InlineKeyboardBuilder()
builder.row(InlineKeyboardButton(text="🇺🇿  UZ", callback_data="lang_uz"))
builder.row(InlineKeyboardButton(text="🇷🇺  RU", callback_data="lang_ru"))

inline_uz_ru = builder.as_markup()

builder_text_uz = InlineKeyboardBuilder()
builder_text_uz.row(InlineKeyboardButton(text="💊 Dori haqida ma'lumot olish", callback_data="dori_info"))#2
builder_text_uz.row(InlineKeyboardButton(text="👩‍💻 Operator bilan Aloqa", callback_data="aloqa"))#3
builder_text_uz.row(InlineKeyboardButton(text="👨‍⚕ Shifokor bilan maslahat", callback_data="maslahat"))#5
builder_text_uz.row(InlineKeyboardButton(text="🧑‍⚕ Diagnostika", callback_data="diagnostika"))#4
builder_text_uz.row(InlineKeyboardButton(text="🚚 Yetkazib berish",url="https://akmalfarm.uz"))
builder_text_uz.row(InlineKeyboardButton(text="🏥 Bizning dorixonalar", callback_data="dorihona_uz"))# 1 
builder_text_uz.row(InlineKeyboardButton(text="❓ Boshqa savol", callback_data="other"))#7
inline_uz_text = builder_text_uz.as_markup()


builder_text_ru = InlineKeyboardBuilder()
builder_text_ru.row(InlineKeyboardButton(text="💊 Получить информацию о лекарствах", callback_data="dori_info_ru"))#2
builder_text_ru.row(InlineKeyboardButton(text="👩‍💻 Чат с оператором", callback_data="aloqa_ru"))#3
builder_text_ru.row(InlineKeyboardButton(text="👨‍⚕ Консультация врача", callback_data="maslahat_ru"))#5
builder_text_ru.row(InlineKeyboardButton(text="🧑‍⚕ Диагностика", callback_data="diagnostika_ru"))#4
builder_text_ru.row(InlineKeyboardButton(text="🚚 Доставка",url="https://akmalfarm.uz"))#6
builder_text_ru.row(InlineKeyboardButton(text="🏥 Наши аптеки", callback_data="dorihona_ru"))# 1 
builder_text_ru.row(InlineKeyboardButton(text="❓ Другой вопрос", callback_data="other_ru"))#7

inline_ru_text = builder_text_ru.as_markup()

photo_choice = InlineKeyboardBuilder()
photo_choice.row(
    InlineKeyboardButton(text="✅ Ha, rasm qo'shish", callback_data="add_photo"),
    InlineKeyboardButton(text="❌ Yo'q, faqat matn", callback_data="skip_photo")
)
photo_choice_markup = photo_choice.as_markup()


photo_choice_ru = InlineKeyboardBuilder()
photo_choice_ru.row(
    InlineKeyboardButton(text="✅ Да, добавить изображение", callback_data="add_photo_ru"),
    InlineKeyboardButton(text="❌ Нет, только текст", callback_data="skip_photo_ru")
)
photo_choice_markup_ru = photo_choice_ru.as_markup()

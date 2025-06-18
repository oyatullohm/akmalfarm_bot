from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, BotCommand
from aiogram.fsm.context import FSMContext
from aiogram import Bot, Dispatcher, html
from aiogram.filters import CommandStart
from asgiref.sync import sync_to_async
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram import Router, types
from aiogram import F
from button import *
from state import * 
import requests
import asyncio
import logging
import environ
import django
import sys
import os 


env = environ.Env()
environ.Env.read_env()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Admin.settings') 
django.setup()
from main.models import *

environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

router = Router()
TOKEN  = env.str('TOKEN')
# TOKEN = "7915282420:AAFFAj5SSgw8OfmBZ7qckCQYSC9tquRXY9I"

dp = Dispatcher()
@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    text = (
    "🖐 Salom! Men *AkmalFarmMedical*’ning \n"
    "qo'llab-quvvatlash botiman.\n"
    "Sizga yordam bermoqchiman!\n"
    "*Sizga qaysi tilda javob berish qulay?*\n\n"
    "🇷🇺 Привет! Я бот поддержки *AkmalFarmMedical*.\n"
    "Хочу вам помочь!\n"
    "*На каком языке вам отвечать?*"
)
    await message.answer(text, reply_markup=inline_uz_ru, parse_mode="Markdown")


async def send_main_menu(message: Message, state: FSMContext, lang: str = 'uz'):
    """Tilga qarab menyuni yuborish"""
    text = "Iltimos, bo'limni tanlang:" if lang == 'uz' else "Пожалуйста, выберите раздел:"
    markup = inline_uz_text if lang == 'uz' else inline_ru_text
    
    await message.answer(
        text,
        reply_markup=markup,
        parse_mode="Markdown"
    )
    await state.set_state(BotStates.menu_select)

@router.callback_query(lambda c: c.data in ["lang_uz", "lang_ru"])
async def handle_language_selection(callback: CallbackQuery, state: FSMContext):

    lang = callback.data.split("_")[1]
    
   
    await sync_to_async(TelegramUser.objects.update_or_create)(
        user_id=callback.from_user.id,
        defaults={
            'first_name': callback.from_user.first_name,
            'last_name': callback.from_user.last_name,
            'username': callback.from_user.username,
            'language': lang
        }
    )
    

    await send_main_menu(callback.message, state, lang)
    await callback.answer()

@dp.message(Command("menu"))
async def handle_menu_command(message: Message, state: FSMContext):

    try:
        user = await sync_to_async(TelegramUser.objects.get)(user_id=message.from_user.id)
        lang = user.language
    except TelegramUser.DoesNotExist:
        lang = 'uz'  
    
    await send_main_menu(message, state, lang)

pharmacies_cache = None

async def get_pharmacies():
    global pharmacies_cache
    if pharmacies_cache is None:
        import requests
        response = requests.get("https://akmalfarm.uz/api/apteka/")
        pharmacies_cache = response.json()
    return pharmacies_cache

@router.callback_query(lambda c: c.data.startswith(("dorihona_uz", "page_")))
async def send_pharmacies_list(callback: CallbackQuery):
    pharmacies = await get_pharmacies()

    if callback.data == "dorihona_uz":
        page = 1
    else:
        page = int(callback.data.split("_")[1])
    
    items_per_page = 8
    total_pages = (len(pharmacies) + items_per_page - 1) // items_per_page
    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page
    current_pharmacies = pharmacies[start_index:end_index]
    
    await callback.message.delete()
    
    for pharmacy in current_pharmacies:
        text = f"🏥 <b>{pharmacy['title']}</b>"
        button = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📍 Joylashuv", callback_data=f"loc_{pharmacy['id']}")]
        ])
        await callback.message.answer(text, reply_markup=button, parse_mode="HTML")

    pagination_buttons = []
    if page > 1:
        pagination_buttons.append(InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"page_{page-1}"))
    
    pagination_buttons.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="current_page"))
    
    if page < total_pages:
        pagination_buttons.append(InlineKeyboardButton(text="Keyingi ➡️", callback_data=f"page_{page+1}"))
    
    pagination_markup = InlineKeyboardMarkup(inline_keyboard=[pagination_buttons])
    await callback.message.answer(
        "Dorixonalar ro'yxati:",
        reply_markup=pagination_markup
    )
    
    await callback.answer()

@router.callback_query(lambda c: c.data and c.data.startswith("loc_"))
async def show_location(callback: CallbackQuery):
    pharmacy_id = int(callback.data.split("_")[1])

    import requests
    response = requests.get(f"https://akmalfarm.uz/api/apteka/{pharmacy_id}/")
    data = response.json()

    lat = float(data['lat'])
    lon = float(data['lon'])
    title = str(data['title'])
    address = str(data['address'])
    # shift = str(data['shift'])
    phone_number = str(data['phone_number'])
    await callback.message.answer(
        f"🏥 <b>{title}</b>\n"
        f"📍 {address}\n"
        # f"⏰ {shift}\n"
        f"📞 {phone_number}",
        parse_mode="HTML"
)

    await callback.message.answer_location(latitude=lat, longitude=lon)
    await callback.answer()


@router.callback_query(lambda c:c.data == "dori_info")
async def dori_info(callback:CallbackQuery,  state: FSMContext):
    await callback.message.answer("📝 Iltimos, dori nomini yozing:")
    await state.set_state(BotStates.dori_info_search) 
    await callback.answer()



@router.callback_query(lambda c: c.data == "aloqa")
async def admin_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("📝 Iltimos, xabar matnini yuboring:")
    await state.set_state(AdminPost.waiting_for_text)
    await callback.answer()


@router.message(AdminPost.waiting_for_text)
async def process_text(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await message.answer("🖼 Endi ritsep rasmni yuboring:")
    await state.set_state(AdminPost.waiting_for_photo)


@router.message(AdminPost.waiting_for_photo, F.photo)
async def process_photo(message: Message, state: FSMContext, bot: Bot):
 
    GROUP_ID = -4818444712 
    
    user_data = await state.get_data()
    text = user_data.get('text', '')
    photo = message.photo[-1]  
    

    user = message.from_user
    user_profile = f"<a href='tg://user?id={user.id}'>{user.full_name}</a>"
    

    try:
        await bot.send_photo(
            chat_id=GROUP_ID,
            photo=photo.file_id,
            caption=f"{text}\n\n👤 Yuboruvchi: {user_profile}",
            parse_mode="HTML"
        )
        await message.answer("✅ Xabar guruhga muvaffaqiyatli yuborildi!")
    except Exception as e:
        await message.answer(f"❌ Xatolik yuz berdi: {str(e)}")
    
    await state.clear()

@router.message(Command("groupid", "id"))
async def get_group_id(message: Message):
    if message.chat.type in ["group", "supergroup"]:
        await message.reply(f"Guruh ID: <code>{message.chat.id}</code>", parse_mode="HTML")
    else:
        await message.reply("Bu buyruq faqat guruhlarda ishlaydi")

@router.message(BotStates.dori_info_search)
async def search_dori(message: types.Message, state: FSMContext):
    dori_nomi = message.text.strip()

    response = requests.get(f'https://akmalfarm.uz/api/product/?search={dori_nomi}')

    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and data:
            for product in data[:5]:
                try:
                    name = product.get('name', 'Nomaʼlum')
                    prices = product.get('prices', {})
                    price = prices.get('price', 'Narx mavjud emas') if isinstance(prices, dict) else 'Narx mavjud emas'
                    country = product.get('country', 'Nomaʼlum')
                    producer = product.get('producer', 'Nomaʼlum')
 
                    product_type_info = product.get('product_type_display', {})
                    if isinstance(product_type_info, dict):
                        product_type_text = product_type_info.get('text', 'Без рецепта')
                    else:
                        product_type_text = str(product_type_info)
                    
                    product_type_display = "🔴 Рецептурный" if "Рецепт" in product_type_text else "🟢 Без рецепта"
                    
                    # Format price with thousand separators if it's a number
                    if isinstance(price, (int, float)):
                        price = f"{price:,} so'm".replace(",", " ")
                    
                    # Send the message
                    await message.answer(
                        f"<b>🔍 {name}</b>\n\n"
                        f"💊 <i>Ishlab chiqaruvchi:</i> {producer}\n"
                        f"🌍 <i>Davlat:</i> {country}\n"
                        f"💰 <i>Narx:</i> <b>{price}</b>\n"
                        f"🏷️ <i>Turi:</i> {product_type_display}",
                        parse_mode="HTML"
                    )
                except Exception as e:
                    continue  
                # for text_part in split_text(clean_text, max_length=3000):
                    # await message.answer(text_part)
        else:
            await message.answer("❗️ Hech qanday dori topilmadi.")
    else:
        await message.answer("⚠️ Serverdan javob kelmadi.")

    await state.clear()


@router.callback_query(lambda c:c.data == "diagnostika")
async def diagnostika(callback:CallbackQuery,  state: FSMContext):
    diagnostika = await sync_to_async(list)(Doctor.objects.filter(is_active=True,status="diagnostika"))
    await callback.answer()
    if diagnostika:
        buttons = [
            [InlineKeyboardButton(text=f"👨‍⚕️ {doctor.name} {doctor.pozitsion}", url=f"https://t.me/{doctor.telegram}")]
            for doctor in diagnostika
        ]
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

        await callback.answer()
        await callback.message.answer("Mutahasislar dan  birini tanlang:", reply_markup=keyboard)
    else:
        await callback.message.answer("""
                                     Yaqinda bu yerda diagnostika xizmatlari ro'yxati paydo bo'ladi.
                                      """)
        await callback.answer()


@router.callback_query(lambda c:c.data == "maslahat")
async def maslahat(callback:CallbackQuery,  state: FSMContext):
    diagnostika = await sync_to_async(list)(Doctor.objects.filter(is_active=True,status="doctor"))
    await callback.answer()
    if diagnostika:
        buttons = [
            [InlineKeyboardButton(text=f"👨‍⚕️ {doctor.name} {doctor.pozitsion}", url=f"https://t.me/{doctor.telegram}")]
            for doctor in diagnostika
        ]
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

        await callback.answer()
        await callback.message.answer("Mutahasislar dan  birini tanlang:", reply_markup=keyboard)
    else:
        await callback.message.answer("""
                                     Yaqinda bu yerda malakalishifokor xizmatlari ro'yxati paydo bo'ladi.
                                      """)
        await callback.answer()


    
@router.callback_query(lambda c:c.data == "other")
async def other(callback:CallbackQuery):
    await callback.message.answer(
    text=(
        "❓ <b>Savollar yoki takliflaringiz bormi?</b>\n"
        "📞 Biz bilan bog'laning: <b>(78) 298-00-88</b>\n"
        "📱 Yoki qisqa raqam: <b>1080</b>"
    ),
    parse_mode="HTML"
)
    await callback.answer()
 

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Botni ishga tushirish"),
        BotCommand(command="menu", description="Asosiy menyu")
    ]
    await bot.set_my_commands(commands)


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await set_commands(bot)
    await dp.start_polling(bot)
    


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    dp.include_router(router)
    asyncio.run(main())
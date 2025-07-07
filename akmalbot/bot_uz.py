from button import *
from bot_ru import *


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


    bot_token = TOKEN
    user_id = callback.from_user.id
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.telegram.org/bot{bot_token}/getUserProfilePhotos?user_id={user_id}&limit=1") as resp:
            data = await resp.json()
            photos = data.get("result", {}).get("photos", [])

            if photos:
                file_id = photos[0][-1]["file_id"]

                async with session.get(f"https://api.telegram.org/bot{bot_token}/getFile?file_id={file_id}") as resp2:
                    file_data = await resp2.json()
                    file_path = file_data["result"]["file_path"]

                    async with session.get(f"https://api.telegram.org/file/bot{bot_token}/{file_path}") as resp3:
                        image_bytes = await resp3.read()

    def save_user():
        user, created = TelegramUser.objects.update_or_create(
            user_id=user_id,
            defaults={
                'first_name': callback.from_user.first_name,
                'last_name': callback.from_user.last_name,
                'username': callback.from_user.username,
                'language': lang,
            }
        )
        if photos:
            # Fayl nomini yaratish
            file_name = f"{user_id}.jpg"
            user.image.save(file_name, ContentFile(image_bytes), save=True)
        return user

    user = await sync_to_async(save_user)()
    if not user.phone_number:
        contact_keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(
                    text="📱 Raqam yuborish" if lang == 'uz' else "📱 Отправить номер",
                    request_contact=True
                )]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )

        await callback.message.answer(
            "📲 Iltimos, telefon raqamingizni yuboring:" if lang == 'uz' else
            "📲 Пожалуйста, отправьте свой номер телефона:",
            reply_markup=contact_keyboard
        )

        await callback.answer()
    else:
        await send_main_menu(callback.message, state, user.language)
        await callback.answer()


@router.message(F.contact)
async def handle_contact(message: Message, state: FSMContext):
    phone_number = message.contact.phone_number

    await sync_to_async(TelegramUser.objects.update_or_create)(
        user_id=message.from_user.id,
        defaults={'phone_number': phone_number}
    )

    try:
        user = await sync_to_async(TelegramUser.objects.get)(user_id=message.from_user.id)
        lang = user.language if user.language in ['uz', 'ru'] else 'uz'

        await message.answer(
            "✅ Raqamingiz saqlandi!" if lang == 'uz' else "✅ Ваш номер сохранён!",
            reply_markup=ReplyKeyboardRemove()
        )
        await send_main_menu(message, state, lang)

    except TelegramUser.DoesNotExist:
        await message.answer("❗ Foydalanuvchi topilmadi.")


@dp.message(Command("menu"))
async def handle_menu_command(message: Message, state: FSMContext):

    try:
        user = await sync_to_async(TelegramUser.objects.get)(user_id=message.from_user.id)
        lang = user.language
    except TelegramUser.DoesNotExist:
        lang = 'uz'  
    
    await send_main_menu(message, state, lang)


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
        button = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📍 Joylashuv", callback_data=f"loc_{pharmacy['id']}")]
        ])
        await callback.message.answer(f"🏥 <b>{pharmacy['title']}</b>\n"
                                      f"📍 {pharmacy['address']}\n"
                                      f"📞 {pharmacy['phone_number']}"
                                      , reply_markup=button, parse_mode="HTML")

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


@router.message(Command("cancel"))
async def cancel_feedback(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Aloqa tugatildi. Qayta yozish uchun  dan Retsept yuklash tallang.")


@router.callback_query(lambda c: c.data == "aloqa")
async def admin_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "📝 Siz  savollaringizni yuborishingiz mumkin.\n"
        "Matn yoki rasm yuboring, biz javob beramiz.\n\n"
        "⛔ Yopish uchun: /cancel"
    )
    await state.set_state(AdminPost.waiting_for_text)
    await callback.answer()


@router.message(AdminPost.waiting_for_text, F.text)
async def process_user_text(message: Message, state: FSMContext, bot: Bot):
    user = message.from_user
    username = (
    f"@{user.username}" if user.username 
    else user.full_name if user.full_name 
    else f"ID:{user.id}"
    )
    user_profile = f"<a href='tg://user?id={user.id}'>{username}</a>"
    text = message.text

    try:
        sent_msg = await bot.send_message(
            chat_id=GROUP_ID,
            text=f"{text}\n\n👤 Yuboruvchi: {user_profile}",
            reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✉️ Javob yozilmagan",
                        callback_data=f"reply_to_"
                    )
                ]
            ]
        ),
            parse_mode="HTML"
        )
        channel_layer = get_channel_layer()
        telegram = await sync_to_async(TelegramUser.objects.get)(user_id=user.id)
        saved_message =  await sync_to_async(Message.objects.create)(
            telegramuser=telegram,
            room_name=user.id,
            content=text,
            is_read=True 
        )
        
        await channel_layer.group_send(
            f"chat_{saved_message.room_name}",
            {
                "type": "external_message",
                "message_id": saved_message.id,
            }
        )
        r.setex(sent_msg.message_id, 86400, json.dumps(telegram.user_id))
        # message_user_map[sent_msg.message_id] = user.id
        await message.answer("✅ Xabaringiz yuborildi. Mutaxassis javobini kuting.")
    except Exception as e:
        await message.answer(f"❌ Xatolik: {str(e)}")


@router.message(AdminPost.waiting_for_text, F.photo)
async def process_user_photo(message: Message, state: FSMContext, bot: Bot):
    user = message.from_user
    username = (
    f"@{user.username}" if user.username 
    else user.full_name if user.full_name 
    else f"ID:{user.id}"
    )

    user_profile = f"<a href='tg://user?id={user.id}'>{username}</a>"
    photo = message.photo[-1]
    caption = message.caption or "🖼 Rasm"

    try:
        sent_msg = await bot.send_photo(
            chat_id=GROUP_ID,
            photo=photo.file_id,
            caption=f"{caption}\n\n👤 Yuboruvchi: {user_profile}",
            reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✉️ Javob yozilmagan",
                        callback_data=f"reply_to_"
                    )
                ]
            ]),
            parse_mode="HTML"
        )
        import aiohttp

        file = await bot.get_file(photo.file_id)
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}"

        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as resp:
                if resp.status == 200:
                    image_data = await resp.read()

                    telegram_user = await sync_to_async(TelegramUser.objects.get)(user_id=user.id)
                    django_file = ContentFile(image_data, name=f"{photo.file_unique_id}.jpg")

                    saved_message = await sync_to_async(Message.objects.create)(
                        telegramuser=telegram_user,
                        room_name=telegram_user.user_id,
                        image=django_file,
                        is_read=True
                    )
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            f"chat_{saved_message.room_name}",
            {
                "type": "external_message",
                "message_id": saved_message.id,
            }
        )
        r.setex(sent_msg.message_id, 86400, json.dumps(telegram_user.user_id))
        # message_user_map[sent_msg.message_id] = user.id
        await message.answer("✅ Rasmingiz yuborildi. Mutaxassis javobini kuting.")
    except Exception as e:
        await message.answer(f"❌ Xatolik: {str(e)}")


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
                    
                    if isinstance(price, (int, float)):
                        price = f"{price:,} so'm".replace(",", " ")
                    
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

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔍 Yana qidirish", callback_data="search_again")],
                [InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="main_menu")],
                [InlineKeyboardButton(text="❌ Yopish", callback_data="close_search")]
            ])
            
            await message.answer(
                "Qidiruv yakunlandi. Keyingi amalni tanlang:",
                reply_markup=keyboard
            )
            
            
            await state.set_state(BotStates.after_search_choice)
            
        else:
            await message.answer("❗️ Hech qanday dori topilmadi.")
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔍 Yana qidirish", callback_data="search_again")],
                [InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="main_menu")],
                [InlineKeyboardButton(text="❌ Yopish", callback_data="close_search")]
            ])
            
            await message.answer(
                "Qidiruv yakunlandi. Keyingi amalni tanlang:",
                reply_markup=keyboard
            )
            await state.set_state(BotStates.after_search_choice)
    else:
        await message.answer("⚠️ Serverdan javob kelmadi.")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔍 Qidirish", callback_data="search_again")],
                [InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="main_menu")],
                [InlineKeyboardButton(text="❌ Yopish", callback_data="close_search")]
            ])
            
        await message.answer(
                "Qidiruv yakunlandi. Keyingi amalni tanlang:",
                reply_markup=keyboard
            )
        await state.set_state(BotStates.after_search_choice)


@router.callback_query(BotStates.after_search_choice, lambda c: c.data in ["search_again", "main_menu", "close_search"])
async def handle_search_actions(callback: CallbackQuery, state: FSMContext):
    action = callback.data
    
    if action == "search_again":
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer("Yana qidirish uchun dori nomini yuboring:")
        await state.set_state(BotStates.dori_info_search)
        
    elif action == "main_menu":
        await callback.message.edit_reply_markup(reply_markup=None)
        await send_main_menu(callback.message, state)
        
    elif action == "close_search":
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer("Qidiruv yakunlandi. Istaingizcha /menu buyrug'i bilan menyuni ochishingiz mumkin.")
        await state.clear()
    
    await callback.answer()


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
        BotCommand(command="start", description="/start"),
        BotCommand(command="menu", description="/menu"),
        BotCommand(command="cancel", description="/cancel")]
    await bot.set_my_commands(commands)


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await set_commands(bot)
    await dp.start_polling(bot)
    

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    dp.include_router(router)
    asyncio.run(main())

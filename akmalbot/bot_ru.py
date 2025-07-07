from state import * 
from button import *
pharmacies_cache = None

async def send_main_menu_ru(message: Message, state: FSMContext, lang: str = 'uz'):

    text ="Пожалуйста, выберите раздел:"
    markup = inline_ru_text
    
    await message.answer(
        text,
        reply_markup=markup,
        parse_mode="Markdown"
    )
    await state.set_state(BotStates.menu_select_ru)


async def get_pharmacies():
    global pharmacies_cache
    if pharmacies_cache is None:
        import requests
        response = requests.get("https://akmalfarm.uz/api/apteka/")
        pharmacies_cache = response.json()
    return pharmacies_cache


@router.message(Command("cancel"))
async def cancel_feedback(message: Message, state: FSMContext):
    await state.clear()
    
    user_id = message.from_user.id

    lang = 'uz'
    try:
        user = await sync_to_async(TelegramUser.objects.get)(user_id=user_id)
        lang = user.language
    except TelegramUser.DoesNotExist:
        pass 

    if lang == 'ru':
        text = "❌ Связь завершена. Чтобы снова отправить сообщение, выберите « Отправить рецепт » из меню."
    else:
        text = "❌ Aloqa tugatildi. Qayta yozish uchun menu dan « Retsept yuklashni » tanlang."

    await message.answer(text)


@router.callback_query(lambda c: c.data.startswith(("dorihona_ru", "page_")))
async def send_pharmacies_list_ru(callback: CallbackQuery):
    pharmacies = await get_pharmacies()

    if callback.data == "dorihona_ru":
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
            [InlineKeyboardButton(text="📍 Локация", callback_data=f"loc_{pharmacy['id']}")]
        ])
        await callback.message.answer(f"🏥 <b>{pharmacy['title']}</b>\n"
                                      f"📍 {pharmacy['address']}\n"
                                      f"📞 {pharmacy['phone_number']}"
                                      , reply_markup=button, parse_mode="HTML")

    pagination_buttons = []
    if page > 1:
        pagination_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"page_{page-1}"))
    
    pagination_buttons.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="current_page"))
    
    if page < total_pages:
        pagination_buttons.append(InlineKeyboardButton(text="Вперёд ➡️", callback_data=f"page_{page+1}"))
    
    pagination_markup = InlineKeyboardMarkup(inline_keyboard=[pagination_buttons])
    await callback.message.answer(
        "Список аптек:",
        reply_markup=pagination_markup
    )
    
    await callback.answer()


@router.callback_query(lambda c: c.data == "dori_info_ru")
async def dori_info_ru(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("📝 Пожалуйста, введите название лекарства:")
    await state.set_state(BotStates.dori_info_search_ru)
    await callback.answer()


@router.message(BotStates.dori_info_search_ru)
async def search_dori_ru(message: types.Message, state: FSMContext):
    dori_nomi = message.text.strip()
    
    response = requests.get(f'https://akmalfarm.uz/api/product/?search={dori_nomi}')

    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and data:
            # Найденные лекарства
            for product in data[:5]:
                try:
                    name = product.get('name', 'Неизвестно')
                    prices = product.get('prices', {})
                    price = prices.get('price', 'Цена не указана') if isinstance(prices, dict) else 'Цена не указана'
                    country = product.get('country', 'Неизвестно')
                    producer = product.get('producer', 'Неизвестно')
 
                    product_type_info = product.get('product_type_display', {})
                    if isinstance(product_type_info, dict):
                        product_type_text = product_type_info.get('text', 'Без рецепта')
                    else:
                        product_type_text = str(product_type_info)
                    
                    product_type_display = "🔴 По рецепту" if "Рецепт" in product_type_text else "🟢 Без рецепта"
                    
                    if isinstance(price, (int, float)):
                        price = f"{price:,} сум".replace(",", " ")
                    
                    await message.answer(
                        f"<b>🔍 {name}</b>\n\n"
                        f"💊 <i>Производитель:</i> {producer}\n"
                        f"🌍 <i>Страна:</i> {country}\n"
                        f"💰 <i>Цена:</i> <b>{price}</b>\n"
                        f"🏷️ <i>Тип:</i> {product_type_display}",
                        parse_mode="HTML"
                    )
                except Exception as e:
                    continue
            
            # Клавиатура
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔍 Искать снова", callback_data="search_again_ru")],
                [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu_ru")],
                [InlineKeyboardButton(text="❌ Закрыть", callback_data="close_search_ru")]
            ])
            
            await message.answer(
                "Поиск завершён. Выберите следующее действие:",
                reply_markup=keyboard
            )
            
            await state.set_state(BotStates.after_search_choice_ru)
            
        else:
            await message.answer("❗️ Ничего не найдено.")
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔍 Искать снова", callback_data="search_again_ru")],
                [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu_ru")],
                [InlineKeyboardButton(text="❌ Закрыть", callback_data="close_search_ru")]
            ])
            
            await message.answer(
                "Поиск завершён. Выберите следующее действие:",
                reply_markup=keyboard
            )
            await state.set_state(BotStates.after_search_choice_ru)
    else:
        await message.answer("⚠️ Сервер не отвечает.")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔍 Искать снова", callback_data="search_again_ru")],
                [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu_ru")],
                [InlineKeyboardButton(text="❌ Закрыть", callback_data="close_search_ru")]
            ])
            
        await message.answer(
            "Поиск завершён. Выберите следующее действие:",
            reply_markup=keyboard
        )
        await state.set_state(BotStates.after_search_choice_ru)


@router.callback_query(BotStates.after_search_choice_ru, lambda c: c.data in ["search_again_ru", "main_menu_ru", "close_search_ru"])
async def handle_search_actions_ru(callback: CallbackQuery, state: FSMContext):
    action = callback.data
    
    if action == "search_again_ru":
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer("Чтобы выполнить новый поиск, отправьте название лекарства:")
        await state.set_state(BotStates.dori_info_search_ru)
        
    elif action == "main_menu_ru":
        await callback.message.edit_reply_markup(reply_markup=None)
        await send_main_menu_ru(callback.message, state)
        
    elif action == "close_search_ru":
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer("Поиск завершён. Вы можете открыть меню с помощью команды /menu.")
        await state.clear()
    
    await callback.answer()


@router.callback_query(lambda c: c.data == "aloqa_ru")
async def admin_start_ru(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "📝 Вы можете отправить свои вопросы.\n"
        "Отправьте текст или фото, и мы обязательно ответим.\n\n"
        "⛔ Чтобы завершить, введите команду: /cancel"
    )
    await state.set_state(AdminPost.waiting_for_text_ru)
    await callback.answer()


@router.message(AdminPost.waiting_for_text_ru, F.text)
async def process_user_text_ru(message: Message, state: FSMContext, bot: Bot):
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
            text=f"{text}\n\n👤 Отправитель: {user_profile}",
            reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✉️ Ответ не был написан.",
                        callback_data=f"reply_to_"
                    )
                ]
            ]),
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
        await message.answer("✅ Ваше сообщение отправлено. Ожидайте ответ специалиста.")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


@router.message(AdminPost.waiting_for_text_ru, F.photo)
async def process_user_photo_ru(message: Message, state: FSMContext, bot: Bot):
    user = message.from_user
    username = (
    f"@{user.username}" if user.username 
    else user.full_name if user.full_name 
    else f"ID:{user.id}"
    )

    user_profile = f"<a href='tg://user?id={user.id}'>{username}</a>"
    photo = message.photo[-1]
    caption = message.caption or "🖼 Фото"

    try:
        sent_msg = await bot.send_photo(
            chat_id=GROUP_ID,
            photo=photo.file_id,
            caption=f"{caption}\n\n👤 Отправитель: {user_profile}",
            reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✉️ Ответ не был написан.",
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
        await message.answer(f"✅ Ваше фото отправлено. Ожидайте ответ специалиста.{user.id}")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


@router.callback_query(F.data.startswith("reply_to_"))
async def remove_reply_button(callback: CallbackQuery):
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception as e:
        pass
    
    # Xohlovchi javob yozishi mumkin — xabar chiqarmasa ham bo‘ladi
    await callback.answer("✉️ Tugma olib tashlandi.", show_alert=False)


@router.message(F.reply_to_message & ~F.contact)
async def handle_reply(message: Message, bot: Bot):

    original_msg_id = message.reply_to_message.message_id
    # user_id = message_user_map.get(original_msg_id)
    user_id = r.get(original_msg_id)
    try:
        await message.reply_to_message.edit_reply_markup(reply_markup=None)
    except Exception as e:
        print(f"❗ Tugmani o‘chirishda xatolik: {e}")

    if not user_id:
        await message.reply(texts["user_not_found"]["ru"])
        return

    try:
        tg_user = await sync_to_async(TelegramUser.objects.get)(user_id=user_id)
        dj_user = await sync_to_async(User.objects.last)()
        user_lang = tg_user.language if tg_user.language in ["uz", "ru"] else "uz"
    except TelegramUser.DoesNotExist:
        await message.reply(texts["user_not_found"]["ru"])
        return

    saved_message = None

    try:
        if message.photo:
            photo = message.photo[-1].file_id
            file = await bot.get_file(photo)
            file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}"

            async with aiohttp.ClientSession() as session:
                async with session.get(file_url) as resp:
                    if resp.status == 200:
                        content = await resp.read()
                        saved_message = await sync_to_async(Message.objects.create)(
                            telegramuser=tg_user,
                            user=dj_user,
                            room_name=tg_user.id,
                            image=ContentFile(content, name=os.path.basename(file.file_path)),
                            is_read=False
                        )
            
            caption = message.caption or message.text or ""
            await bot.send_photo(
                chat_id=user_id,
                photo=photo,
                caption=caption,
                reply_markup=ReplyKeyboardRemove(),
                parse_mode="HTML"
            )

        elif message.sticker:
            sticker_id = message.sticker.file_id
            await bot.send_sticker(
                chat_id=user_id,
                sticker=sticker_id,
                reply_markup=ReplyKeyboardRemove()
            )

        elif message.voice:
            voice_id = message.voice.file_id
            file = await bot.get_file(voice_id)
            file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}"

            async with aiohttp.ClientSession() as session:
                async with session.get(file_url) as resp:
                    if resp.status == 200:
                        content = await resp.read()
                        saved_message = await sync_to_async(Message.objects.create)(
                            telegramuser=tg_user,
                            user=dj_user,
                            room_name=tg_user.user_id,
                            voice=ContentFile(content, name=f"voice_{timezone.now().strftime('%Y%m%d%H%M%S')}.ogg"),
                            is_read=False
                        )

            await bot.send_voice(
                chat_id=user_id,
                voice=voice_id,
                caption=message.caption or None,
                reply_markup=ReplyKeyboardRemove()
            )

        elif message.text:
            text_to_send = message.text
            saved_message = await sync_to_async(Message.objects.create)(
                telegramuser=tg_user,
                room_name=tg_user.user_id,
                user=dj_user,
                content=text_to_send,
                is_read=False
            )
            await bot.send_message(
                chat_id=user_id,
                text=f"{texts['response_prefix'][user_lang]}{text_to_send}",
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            await message.reply(texts["send_text_or_photo"][user_lang])
            return

        await sync_to_async(
            lambda: Message.objects.filter(
                telegramuser__user_id=tg_user.user_id, is_read=True
            ).update(is_read=False)
        )()

        
        await message.reply(texts["response_sent"][user_lang])
        if saved_message:
            channel_layer = get_channel_layer()
            await channel_layer.group_send(
                f"chat_{saved_message.room_name}",
                {
                    "type": "external_message",
                    "message_id": saved_message.id,
                }
            )
    except Exception as e:
        await message.reply(f"❌ {str(e)}")


@router.callback_query(lambda c: c.data == "diagnostika_ru")
async def diagnostika_ru(callback: CallbackQuery, state: FSMContext):
    diagnostika = await sync_to_async(list)(Doctor.objects.filter(is_active=True, status="diagnostika"))
    await callback.answer()
    
    if diagnostika:
        buttons = [
            [InlineKeyboardButton(text=f"👨‍⚕️ {doctor.name} {doctor.pozitsion}", url=f"https://t.me/{doctor.telegram}")]
            for doctor in diagnostika
        ]
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

        await callback.message.answer("Выберите одного из специалистов:", reply_markup=keyboard)
    else:
        await callback.message.answer("""
                                     Скоро здесь появится список диагностических услуг.
                                     """)
        await callback.answer()


@router.callback_query(lambda c: c.data == "maslahat_ru")
async def maslahat_ru(callback: CallbackQuery, state: FSMContext):
    diagnostika = await sync_to_async(list)(Doctor.objects.filter(is_active=True, status="doctor"))
    await callback.answer()
    
    if diagnostika:
        buttons = [
            [InlineKeyboardButton(text=f"👨‍⚕️ {doctor.name} {doctor.pozitsion}", url=f"https://t.me/{doctor.telegram}")]
            for doctor in diagnostika
        ]
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

        await callback.message.answer("Выберите одного из специалистов:", reply_markup=keyboard)
    else:
        await callback.message.answer("""
                                     Скоро здесь появится список квалифицированных врачей.
                                     """)
        await callback.answer()


@router.callback_query(lambda c: c.data == "other_ru")
async def other_ru(callback: CallbackQuery):
    await callback.message.answer(
        text=(
            "❓ <b>Есть вопросы или предложения?</b>\n"
            "📞 Свяжитесь с нами: <b>(78) 298-00-88</b>\n"
            "📱 Или короткий номер: <b>1080</b>"
        ),
        parse_mode="HTML"
    )
    await callback.answer()

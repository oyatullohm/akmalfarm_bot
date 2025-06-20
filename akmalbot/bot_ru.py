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
    await callback.message.answer("📝 Пожалуйста, отправьте текст сообщения:")
    await state.set_state(AdminPost.waiting_for_text_ru)
    await callback.answer()

@router.message(AdminPost.waiting_for_text_ru)
async def process_text_ru(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    
    await message.answer(
        "Хотите добавить изображение?",
        reply_markup=photo_choice_markup_ru
    )
    await state.set_state(AdminPost.photo_choice_ru)

@router.callback_query(AdminPost.photo_choice_ru, F.data == "add_photo_ru")
async def request_photo_ru(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("🖼 Пожалуйста, отправьте изображение рецепта:")
    await state.set_state(AdminPost.waiting_for_photo_ru)
    await callback.answer()

@router.callback_query(AdminPost.photo_choice_ru, F.data == "skip_photo_ru")
async def skip_photo_ru(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.message.edit_reply_markup(reply_markup=None)
    
    user_data = await state.get_data()
    text = user_data.get('text', '')
    
    # GROUP_ID = -4724451433 
    GROUP_ID = -1002524424597 
    user = callback.from_user
    username = f"@{user.username}" if user.username else user.full_name
    user_profile = f"<a href='tg://user?id={user.id}'>{username}</a>"
    
    try:
        sent_msg = await bot.send_message(
            chat_id=GROUP_ID,
            text=f"{text}\n\n👤 Отправитель: {user_profile}",
            parse_mode="HTML"
        )
        message_user_map[sent_msg.message_id] = user.id

        await callback.message.answer("✅ Сообщение отправлено в группу!\n"
                                      "Админы могут ответить на это сообщение.")
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка: {str(e)}")
    
    await state.clear()


@router.message(AdminPost.waiting_for_photo_ru, F.photo)
async def process_photo_ru(message: Message, state: FSMContext, bot: Bot):
    user_data = await state.get_data()
    text = user_data.get('text', '')
    
    # GROUP_ID = -4724451433 
    GROUP_ID = -1002524424597 
    user = message.from_user
    username = f"@{user.username}" if user.username else user.full_name
    user_profile = f"<a href='tg://user?id={user.id}'>{username}</a>"
    photo = message.photo[-1] 
    
    try:
        sent_msg = await bot.send_photo(
            chat_id=GROUP_ID,
            photo=photo.file_id,
            caption=f"{text}\n\n👤 Отправитель: {user_profile}",
            parse_mode="HTML"
        )
        message_user_map[sent_msg.message_id] = user.id

        await message.answer("✅ Сообщение с фото отправлено в группу!\n"
                             "Админы могут ответить на это сообщение.")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")
    
    await state.clear()

@router.message(F.reply_to_message)
async def handle_reply_ru(message: Message, bot: Bot):
    original_msg_id = message.reply_to_message.message_id
    user_id = message_user_map.get(original_msg_id)

    if user_id:
        try:
            await bot.send_message(
                chat_id=user_id,
                text=f"📩 Ответ на ваше сообщение:\n\n{message.text}"
            )
            await message.reply("✅ Ответ отправлен пользователю.")
        except Exception as e:
            await message.reply(f"❌ Не удалось отправить пользователю: {str(e)}")
    else:
        await message.reply("⚠️ Получатель этого сообщения не найден.")


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

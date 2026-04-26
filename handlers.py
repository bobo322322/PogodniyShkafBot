import os
import logging
import keyboards as kb
from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters.command import  CommandStart, Command
from states import Ward, Adding
from weather import get_weather_now
from daily_weather import get_daily_forecast, get_tomorrow_forecast
from aiogram.fsm.context import FSMContext
from database import add_item, ward_lookup, delete_item, copy_wardrobe
from gemini import ai_recommend, image_description
from aiogram.utils.chat_action import ChatActionSender
from database import ban_user, unban_user
user = Router()
logger = logging.getLogger(__name__)


@user.message(CommandStart())
async def cmd_start(message: Message):
    logger.info(
        f"User {message.from_user.id} started bot. "
        f"Username: @{message.from_user.username}, "
        f"First Name: {message.from_user.first_name}")
    logger.info(f"Пользователь @{message.from_user.username} ({message.from_user.id}) "
                f"написал: '{message.text}'")
    first_name = message.from_user.first_name.capitalize()
    await message.answer(f'👋 Привет, {first_name}! Я твой личный стилист во Владивостоке — городе, '
                         f'где погода меняется быстрее, чем настроение.\n\n'
                         f'Вот что я уже умею:\n '
                         f'🌤 Прогноз на сегодня и завтра\n '
                         f'🧥 Гардероб с добавлением по фото\n '
                         f'🚪 Просмотр и удаление вещей \n '
                         f'🤖 Аутфиты от нейросети заглядывай в меню — там всё просто \n'
                         f'👉 /menu'
                         )


@user.message(Command('help'))
async def cmd_help(message: Message):
    logger.info(f"Пользователь @{message.from_user.username} ({message.from_user.id}) "
                f"обратился в поддержку")
    await message.answer('Если у вас возникли проблемы с ботом, можете написать в поддержку: @ronaldo32222')


@user.message(Command('menu'))
async def cmd_menu(message: Message):
    logger.info(f'Пользователь @{message.from_user.username} ({message.from_user.id})'
                f'вышел в меню')
    await message.answer(text='Чем займемся?', reply_markup=kb.main_menu)

@user.callback_query(F.data == 'menu')
async def callback_menu(callback: CallbackQuery):
    logger.info(f'Пользователь @{callback.from_user.username} ({callback.from_user.id})'
                f'вышел в меню')
    await callback.message.delete()
    await callback.message.answer(text='Выберите действие', reply_markup=kb.main_menu)
    await callback.answer()

@user.message(F.text == '🌤 Прогноз погоды')
async def txt_forecast(message: Message):
    logger.info(f"Пользователь @{message.from_user.username} ({message.from_user.id}) "
                f"выбирает прогноз погоды")
    await message.answer('🌤 Смотрим погоду на сегодня или заглядываем на завтра? 👇', reply_markup=kb.forecast_date)

@user.callback_query(F.data == 'forecast_today')
async def forecast_today(callback_query: CallbackQuery):
    logger.info(f"Пользователь @{callback_query.from_user.username} ({callback_query.from_user.id}) "
                f"открыл прогноз погоды на сегодня")
    forecast = f"{get_weather_now()}\n\n{get_daily_forecast()}"
    await callback_query.message.edit_text(forecast, reply_markup=kb.back_to_menu)



@user.callback_query(F.data == 'forecast_tomorrow')
async def forecast_today(callback_query: CallbackQuery):
    logger.info(f"Пользователь @{callback_query.from_user.username} ({callback_query.from_user.id}) "
                f"открыл прогноз погоды на завтра")
    forecast = get_tomorrow_forecast()
    await callback_query.message.edit_text(forecast)



@user.message(F.text == '👕 Гардероб')
async def txt_wardrobe(message: Message):
    await message.answer("Добро пожаловать в Ваш гардероб", reply_markup=kb.wardrobe)
    logger.info(f"Пользователь @{message.from_user.username} ({message.from_user.id}) "
                f"зашел в гардероб")

@user.callback_query(F.data == 'wardrobe')
async def btn_wardrobe(callback_query: CallbackQuery):
    await callback_query.message.delete()
    await callback_query.message.answer("Добро пожаловать в Ваш гардероб", reply_markup=kb.wardrobe)
    await callback_query.answer()
    logger.info(f"Пользователь @{callback_query.from_user.username} ({callback_query.from_user.id}) "
                f"зашел в гардероб")

@user.callback_query(F.data == 'add_new')
async def add_new(callback_query: CallbackQuery):
    logger.info(f"Пользователь @{callback_query.from_user.username} ({callback_query.from_user.id}) "
                f"добавляет вещь вручную")
    await callback_query.message.delete()
    await callback_query.message.answer('📦 Каким способом добавим?', reply_markup=kb.add_method)
    await callback_query.answer()


@user.callback_query(F.data == 'add_new_ph')
async def add_new_ph(callback_query: CallbackQuery, state: FSMContext):
    logger.info(f'Пользователь @{callback_query.from_user.username} ({callback_query.from_user.id})'
                f' добавляет вещь по фото')
    await callback_query.message.delete()
    await callback_query.message.answer('📸 Понял. Теперь просто отправь фото вещи в чат.',
                                        reply_markup=kb.cancel_add)
    await state.set_state(Adding.photo)
    await callback_query.answer()


@user.message(Adding.photo)
async def get_photo(message: Message, bot: Bot, state: FSMContext):
    logger.info(f'Пользователь @{message.from_user.username} ({message.from_user.id}) '
                f'отправил фото вещи')
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    temp_input_path = f"input_{message.from_user.id}_{photo.file_id}.jpg"
    status_msg = await message.answer("🤖 Обрабатываю изображение...")
    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        try:
            await bot.download_file(file.file_path, destination=temp_input_path)
            data = await image_description(temp_input_path)
        except Exception as e:
            logger.error(f"Ошибка при обработке фото: {e}")
            await message.answer('😕 Произошла ошибка при распознавании. Попробуй ещё раз или добавь вручную.',
                                 reply_markup=kb.add_failed)
            return
        finally:
            if os.path.exists(temp_input_path):
                os.remove(temp_input_path)
        items = data.get("items")
        if not items:
            await message.answer('😕 Не удалось распознать вещь. Попробуй сделать другое фото или добавь вручную.',
                                 reply_markup=kb.add_failed)
            return
        current_index = 0
        await state.update_data(items=items)
        await state.update_data(current_index=current_index)
        await state.set_state(Adding.process)
        lines = [
            f"✨ Вещь: {items[current_index].get('item_name', 'Неизвестно')}",
            f"📁 Категория: {items[current_index].get('category', 'Не указана')}",
            f"🧵 Материал: {items[current_index].get('material') or 'не определен'}",
            f"🎨 Цвет: {items[current_index].get('color') or 'не определен'}",
            f"🕶 Стиль: {items[current_index].get('style') or 'не определен'}"
        ]
        description = "\n".join(lines)


        await status_msg.edit_text(f"🧐 Вещь {current_index + 1} из {len(items)}: \n"
                                               f"{description} \n"
                                               f"\n➕ Добавить — сохранить текущую вещь  в гардероб\n"
                                               f"◀️ ▶️ — просмотреть другие вещи\n"
                                               f"«🏁 Завершить добавление» — закончить и вернуться в гардероб\n",
                                               reply_markup=kb.add_confirm)


@user.callback_query(F.data == 'nav_next')
async def nav_next(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    items = data.get('items')
    current_index = data.get('current_index') + 1
    current_index = current_index if current_index < len(items) else 0
    await state.update_data(current_index=current_index)
    lines = [
        f"✨ Вещь: {items[current_index].get('item_name', 'Неизвестно')}",
        f"📁 Категория: {items[current_index].get('category', 'Не указана')}",
        f"🧵 Материал: {items[current_index].get('material') or 'не определен'}",
        f"🎨 Цвет: {items[current_index].get('color') or 'не определен'}",
        f"🕶 Стиль: {items[current_index].get('style') or 'не определен'}"
    ]
    description = "\n".join(lines)
    await callback_query.message.edit_text(f"🧐 Вещь {current_index + 1} из {len(items)}: \n"
                                           f"{description} \n"
                                           f"\n➕ Добавить — сохранить текущую вещь  в гардероб\n"
                                           f"◀️ ▶️ — просмотреть другие вещи\n"
                                           f"«🏁 Завершить добавление» — закончить и вернуться в гардероб\n",
                                           reply_markup=kb.add_confirm)
    await callback_query.answer()


@user.callback_query(F.data == 'nav_prev')
async def nav_prev(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    items = data.get('items')
    current_index = data.get('current_index') - 1
    current_index = current_index if current_index >= 0 else len(items) - 1
    await state.update_data(current_index=current_index)
    lines = [
        f"✨ Вещь: {items[current_index].get('item_name', 'Неизвестно')}",
        f"📁 Категория: {items[current_index].get('category', 'Не указана')}",
        f"🧵 Материал: {items[current_index].get('material') or 'не определен'}",
        f"🎨 Цвет: {items[current_index].get('color') or 'не определен'}",
        f"🕶 Стиль: {items[current_index].get('style') or 'не определен'}"
    ]
    description = "\n".join(lines)
    await callback_query.message.edit_text(f"🧐 Вещь {current_index + 1} из {len(items)}: \n"
                                           f"{description} \n"
                                           f"\n➕ Добавить — сохранить текущую вещь  в гардероб\n"
                                           f"◀️ ▶️ — просмотреть другие вещи\n"
                                           f"«🏁 Завершить добавление» — закончить и вернуться в гардероб\n",
                             reply_markup=kb.add_confirm)
    await callback_query.answer()


@user.callback_query(F.data == 'add_item')
async def add_ph_item(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    items = data.get('items')
    current_index = data.get('current_index')
    item = items[current_index]
    item["user_id"] = callback_query.from_user.id
    item["username"] = callback_query.from_user.username
    if not item.get('item_name'):
        await callback_query.message.answer("⚠️ Не найдены данные для добавления. Попробуй заново.",
                                            reply_markup=kb.wardrobe)

        await callback_query.answer()
        return
    add_item(item)
    await callback_query.message.answer(
        f'✅ Готово! Вещь «{item["item_name"]}» поселилась в твоём гардеробе.\n'
        f'Теперь я буду учитывать её при составлении образов 🎩✨'
    )
    await callback_query.answer()
    items.pop(current_index)



@user.callback_query(F.data == 'end_adding')
async def end_adding(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    await callback_query.message.answer(f'🏁 Добавление завершено! \n'
                                        f'Твои новые вещи уже в гардеробе. '
                                        f'Можешь посмотреть их в любое время 👀', reply_markup=kb.wardrobe)
    await callback_query.answer()
    await state.clear()

@user.callback_query(F.data == 'add_new_mnl')
async def btn_add_item(callback_query: CallbackQuery, state: FSMContext):
    logger.info(f"Пользователь @{callback_query.from_user.username} ({callback_query.from_user.id}) "
                f"добавляет новую вещь")
    await callback_query.message.delete()
    await state.update_data(user_id=callback_query.from_user.id,
                            username=callback_query.from_user.username)
    await state.set_state(Ward.first)
    await callback_query.message.answer(
        '🧢 Как назовём вещь? Укажи модель, цвет или бренд — так ты сразу её узнаешь.\n'
        '👉 Например: «Nike Air Force 1», «Черные джинсы Zara», «Синяя кофта-полузамок»',
        reply_markup=kb.cancel_add
    )
    await callback_query.answer()


@user.callback_query(F.data == 'cancel')
async def btn_cancel(callback: CallbackQuery, state: FSMContext):

    logger.info(f"Пользователь @{callback.from_user.username} ({callback.from_user.id}) "
                f"отменил добавление")
    await callback.message.delete()
    await callback.message.answer('👋 Добавление отменено.\n'
                                  'Если захочешь вернуться — просто вернись в гардероб',
                                  reply_markup=kb.wardrobe)
    await callback.answer()
    await state.clear()


@user.message(Ward.first)
async def process_item_name(message: Message, state: FSMContext):
        await state.update_data(item_name=message.text)
        await state.set_state(Ward.second)
        await message.answer('🧥 Окей, записал! Теперь выбери категорию.',
                             reply_markup=kb.category_keyboard)


@user.callback_query(Ward.second)
async def process_category(callback: CallbackQuery, state: FSMContext):
    await state.update_data(category=callback.data)
    await state.set_state(Ward.third)
    await callback.message.delete()
    await callback.message.answer("Супер! Из чего сделана вещь?",
                                  reply_markup=kb.material_keyboard)
    await callback.answer()


@user.callback_query(Ward.third)
async def process_material(callback: CallbackQuery, state: FSMContext):
    await state.update_data(material=callback.data)
    await state.set_state(Ward.fourth)
    await callback.message.delete()
    await callback.message.answer("🎨 Красота — в деталях!\n"
                                  "Какой цвет преобладает? Если не нашёл нужный — жми «🌈 Другой».",
                                  reply_markup=kb.color_keyboard)
    await callback.answer()


@user.callback_query(Ward.fourth)
async def process_color(callback: CallbackQuery, state: FSMContext):
    await state.update_data(color=callback.data)
    data = await state.get_data()
    await callback.message.delete()
    await callback.message.answer(
        f'✅ Готово! Вещь «{data["item_name"]}» поселилась в твоём гардеробе.\n'
        f'Теперь я буду учитывать её при составлении образов 🎩✨',
        reply_markup=kb.wardrobe
    )
    await callback.answer()
    add_item(data)
    logger.info(f"Пользователь @{callback.from_user.username} ({callback.from_user.id}) "
                f"добавил новую вещь")
    await state.clear()


@user.callback_query(F.data == 'lookup')
async def btn_ward_lookup(callback_query: CallbackQuery):
    await callback_query.message.delete()
    logger.info(f"Пользователь @{callback_query.from_user.username} ({callback_query.from_user.id}) "
                f"просматривает свой гардероб")
    result = ward_lookup(user_id=callback_query.from_user.id)
    if isinstance(result, tuple):
        text, builder = result
        if builder is not None:
            await callback_query.message.answer(text, reply_markup=builder.as_markup())
        else:
            await callback_query.message.answer(text, reply_markup=kb.empty_wardrobe)
    else:
        await callback_query.message.answer(result)
    await callback_query.answer()


@user.callback_query(F.data.startswith('del_'))
async def btn_del(callback_query: CallbackQuery, state: FSMContext):
    item_id = callback_query.data.split('_')[1]
    item_name = callback_query.data.split('_')[2]
    await state.update_data(item_id=item_id, item_name=item_name)
    await callback_query.message.delete()

    await callback_query.message.answer(f'Вы уверены, что хотите удалить вещь "{item_name}..."?', reply_markup=kb.confirm_delete)
    await callback_query.answer()


@user.callback_query(F.data == 'accept')
async def btn_item_name(callback_query: CallbackQuery, state: FSMContext):
    logger.info(f"Пользователь @{callback_query.from_user.username} ({callback_query.from_user.id}) "
                f"удаляет вещь")
    data = await state.get_data()
    item_name = data['item_name'] + '...'
    delete_item(data['item_id'])
    await callback_query.message.delete()
    await callback_query.message.answer(f'Вещь "{item_name}" удалена', reply_markup=kb.wardrobe)
    await callback_query.answer()


async def recommend_action(message: Message):
    logger.info(f"Рекомендация для @{message.from_user.username}")
    status_msg = await message.answer("🤖 Собираю данные и подбираю образ...")
    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        try:
            wardrobe_list = copy_wardrobe(user_id=message.from_user.id)
            recommendation = await ai_recommend(wardrobe_list=wardrobe_list)
            await status_msg.edit_text(recommendation)
        except Exception as e:
            logger.error(f"Ошибка при генерации рекомендации: {e}")
            await status_msg.edit_text(
                "⚠️ Не удалось получить рекомендацию. Попробуй позже или проверь гардероб."
            )

@user.message(Command("recommend"))
async def cmd_recommend(message: Message):
    await recommend_action(message)

@user.message(F.text == "🤔 Что надеть?")
async def btn_recommend(message: Message):
    await recommend_action(message)


ADMIN = "bobo1836"

@user.message(Command("ban"))
async def ban_command(message: Message):
    if message.from_user.username != ADMIN:
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Укажи username")
        return
    target = args[1].lstrip('@')
    ban_user(target)
    await message.answer(f"✅ @{target} забанен")

@user.message(Command("unban"))
async def unban_command(message: Message):
    if message.from_user.username != ADMIN:
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Укажи username")
        return
    target = args[1].lstrip('@')
    unban_user(target)
    await message.answer(f"✅ @{target} разбанен")

@user.message()
async def echo(message: Message):
    logger.info(f"Пользователь @{message.from_user.username} [{message.from_user.id}] "
                f"написал: '{message.text}'")
    await message.send_copy(chat_id=message.from_user.id)

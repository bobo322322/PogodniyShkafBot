from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)


main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='🌤 Прогноз погоды')],
        [KeyboardButton(text='👕 Гардероб')],
        [KeyboardButton(text='🤔 Что надеть?')],
    ],
    resize_keyboard=True,
    input_field_placeholder='❄️'
)

wardrobe = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='🚪 Посмотреть свой гардероб', callback_data='lookup')],
        [InlineKeyboardButton(text='➕ Добавить вещь', callback_data='add_new')],
        [InlineKeyboardButton(text='🏠 Меню', callback_data='menu')],

    ]
)


add_method = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='📸 По фото', callback_data='add_new_ph')],
        [InlineKeyboardButton(text='✍️ Вручную', callback_data='add_new_mnl')],
    ]
)



back_to_menu = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='🏠 Меню', callback_data='menu')],]
)

cancel_add = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='❌ Отмена', callback_data='cancel')],
    ]
)

empty_wardrobe = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='➕ Добавить вещь', callback_data='add_new')]
    ]
)
confirm_delete = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='✅ Да, удалить', callback_data='accept'),
         InlineKeyboardButton(text='❌ Нет, оставить', callback_data='lookup')],
    ]
)

add_confirm = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='✅ Да, добавить', callback_data='add_item'),
        InlineKeyboardButton(text='🏁 Завершить добавление', callback_data='end_adding')],
        [InlineKeyboardButton(text='◀️ Предыдущая вещь', callback_data='nav_prev'),
         InlineKeyboardButton(text='▶️ Следующая вещь', callback_data='nav_next')],
        [InlineKeyboardButton(text='✍️ Заполнить вручную', callback_data='add_new_mnl'),
         InlineKeyboardButton(text='❌ Отмена', callback_data='cancel')],
    ]
)

add_failed = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='🔄 Новое фото', callback_data='add_new_ph')],
        [InlineKeyboardButton(text='✍️ Заполнить вручную', callback_data='add_new_mnl'),
         InlineKeyboardButton(text='❌ Отмена', callback_data='cancel')],
    ]
)

forecast_date = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='📅 На сегодня', callback_data='forecast_today'),
         InlineKeyboardButton(text='⏭ На завтра', callback_data='forecast_tomorrow')],
        [InlineKeyboardButton(text='🏠 Меню', callback_data='menu')],
    ]
)



category_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='🧥 Верхняя одежда', callback_data='верхняя одежда')],
        [InlineKeyboardButton(text='👕 Верх (база)', callback_data='Верх(База)')],
        [InlineKeyboardButton(text='👖 Низ', callback_data='Низ')],
        [InlineKeyboardButton(text='👟 Обувь', callback_data='Обувь')],
        [InlineKeyboardButton(text='🕶️ Аксессуары', callback_data='Аксессуар'),
         InlineKeyboardButton(text='🎩 Головные уборы', callback_data='Головной убор')],
        [InlineKeyboardButton(text='❌ Отмена', callback_data='cancel')]
    ]
)

material_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='🌿 Хлопок / Лен', callback_data='Хлопок'),
         InlineKeyboardButton(text='🧶 Шерсть / Кашемир ', callback_data='Шерсть')],

        [InlineKeyboardButton(text='🧵 Трикотаж', callback_data='Синтентика'),
         InlineKeyboardButton(text='🐄 Кожа / Замша', callback_data='Кожа')],

        [InlineKeyboardButton(text='✨ Шелк / Атлас', callback_data='Синтентика'),
         InlineKeyboardButton(text='🧪 Синтетика', callback_data='Кожа')],

        [InlineKeyboardButton(text='👖 Деним', callback_data='Деним'),
         InlineKeyboardButton(text='🧬 Смесовая ткань', callback_data='Другое')],
        [InlineKeyboardButton(text='❌ Отмена', callback_data='cancel')]
    ]
)


color_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='⚫ Чёрный', callback_data='Черный'),
         InlineKeyboardButton(text='⚪ Белый', callback_data='Белый')],
        [InlineKeyboardButton(text='🔵 Синий', callback_data='Синий'),
         InlineKeyboardButton(text='🔴 Красный', callback_data='Красный')],
        [InlineKeyboardButton(text='🟢 Зелёный', callback_data='Зеленый'),
         InlineKeyboardButton(text='🟡 Жёлтый', callback_data='Желтый')],
        [InlineKeyboardButton(text='🔘 Серый', callback_data='Серый'),
         InlineKeyboardButton(text='🟤 Коричневый', callback_data='Коричневый')],
        [InlineKeyboardButton(text='🌈 Разноцветный', callback_data='Разноцветный')],
        [InlineKeyboardButton(text='❌ Отмена', callback_data='cancel')]
    ]
)

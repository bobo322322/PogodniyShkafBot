import sqlite3
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
def add_item(data):
    # print(data)
    connection = sqlite3.connect('ward.db')
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wardrobe (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INT,
            username TEXT,
            item_name TEXT,
            category TEXT,
            material TEXT,
            season TEXT,
            color TEXT,
            style TEXT
        )
    """)
    sql_query = """
        INSERT INTO wardrobe (user_id, username, item_name, category, material, color) 
        VALUES (:user_id, :username, :item_name, :category, :material, :color)
    """
    cursor.execute(sql_query, data)
    connection.commit()
    connection.close()


def ward_lookup(user_id):
    connection = sqlite3.connect('ward.db')
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wardrobe (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INT,
            username TEXT,
            item_name TEXT,
            category TEXT,
            material TEXT,
            season TEXT,
            color TEXT,
            style TEXT
        )
    """)

    cursor.execute(
        "SELECT rowid, item_name, category, color, material FROM wardrobe WHERE user_id = ?;",
        (user_id,)
    )
    items = cursor.fetchall()
    if not items:
        message = ('🕸️ В твоём гардеробе пока тихо…\n\n'
                   '🏝 Владивосток — город ветров и стиля. Самое время добавить первую вещь!\n\n'
                   '👇 Нажми кнопку ниже — я помогу внести всё, что нужно.')
        connection.close()
        return message, None

    builder = InlineKeyboardBuilder()
    outer_items = []
    base_items = []
    bottom_items = []
    shoes = []
    accessory_items = []
    hat_items = []

    for item in items:

        category = item[2]
        if category == 'верхняя одежда':
            outer_items.append(item)
        elif category == 'Верх(База)':
            base_items.append(item)
        elif category == 'Низ':
            bottom_items.append(item)
        elif category == 'Обувь':
            shoes.append(item)
        elif category == 'Аксессуар':
            accessory_items.append(item)
        elif category == 'Головной убор':
            hat_items.append(item)

    message = f'Твой гардероб:\n'

    if outer_items:
        message += '🧥 Верхняя одежда:\n'
        for item in outer_items:
            # item[1] - название, item[3] - цвет
            message += f' • {item[1]} ({item[3]})\n'
            builder.row(
                InlineKeyboardButton(
                    text=f"🗑 Удалить: {item[1][:15]}…",
                    callback_data=f"del_{item[0]}_{item[1][:13]}"
                )
            )
    if base_items:
        message += '👕 Верх:\n'
        for item in base_items:
            message += f' • {item[1]} ({item[3]})\n'
            builder.row(
                InlineKeyboardButton(
                    text=f"🗑 Удалить: {item[1][:15]}…",
                    callback_data=f"del_{item[0]}_{item[1][:13]}"
                )
            )
    if bottom_items:
        message += '👖 Низ:\n'
        for item in bottom_items:
            message += f' • {item[1]} ({item[3]})\n'
            builder.row(
                InlineKeyboardButton(
                    text=f"🗑 Удалить: {item[1][:15]}…",
                    callback_data=f"del_{item[0]}_{item[1][:13]}"
                )
            )
    if shoes:
        message += '👟 Обувь:\n'
        for item in shoes:
            message += f' • {item[1]} ({item[3]})\n'
            builder.row(
                InlineKeyboardButton(
                    text=f"🗑 Удалить: {item[1][:15]}…",
                    callback_data=f"del_{item[0]}_{item[1][:13]}"
                )
            )
    if accessory_items:
        message += '🕶️ Аксессуары:\n'
        for item in accessory_items:
            message += f' • {item[1]} ({item[3]})\n'
            builder.row(
                InlineKeyboardButton(
                    text=f"🗑 Удалить: {item[1][:15]}…",
                    callback_data=f"del_{item[0]}_{item[1][:13]}"
                )
            )
    if hat_items:
        message += '🎩 Головные уборы:\n'
        for item in hat_items:
            message += f' • {item[1]} ({item[3]})\n'
            builder.row(
                InlineKeyboardButton(
                    text=f"🗑 Удалить: {item[1][:15]}…",
                    callback_data=f"del_{item[0]}_{item[1][:13]}"
                )
            )
    message += '━━━━━━━━━━━━━━━━'
    builder.row(InlineKeyboardButton(text='🔙 Назад', callback_data="wardrobe"))

    connection.close()
    return message, builder

def delete_item(item_id):
    connection = sqlite3.connect('ward.db')
    cursor = connection.cursor()
    cursor.execute("""
                CREATE TABLE IF NOT EXISTS wardrobe (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INT,
                    username TEXT,
                    item_name TEXT,
                    category TEXT,
                    material TEXT,
                    season TEXT,
                    color TEXT,
                    style TEXT
                )
            """)

    cursor.execute("DELETE FROM wardrobe WHERE id = ?", (item_id,))
    connection.commit()
    connection.close()


def copy_wardrobe(user_id):
    connection = sqlite3.connect('ward.db')
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wardrobe (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INT,
            username TEXT,
            item_name TEXT,
            category TEXT,
            material TEXT,
            season TEXT,
            color TEXT,
            style TEXT
        )
    """)

    cursor.execute(
        "SELECT item_name, category, color, material FROM wardrobe WHERE user_id = ?;",
        (user_id,)
    )
    items = cursor.fetchall()

    categorized = {
        'верхняя одежда': [],
        'Верх(База)': [],
        'Низ': [],
        'Обувь': [],
        'Аксессуар': [],
        'Головной убор': []
    }

    for item in items:
        cat = item[1]
        if cat in categorized:
            categorized[cat].append(item)

    lines = []
    for cat_name in categorized.keys():
        cat_items = categorized[cat_name]
        if not cat_items:
            continue
        lines.append(f"\n{cat_name.upper()}:")

        for i in cat_items:
            name = i[0]
            color = i[2]
            material = i[3]

            attrs = []
            if color:
                attrs.append(f"цвет: {color}")
            if material:
                attrs.append(f"материал: {material}")
            attr_str = ", ".join(attrs)
            lines.append(f" • {name} — {attr_str}")

    connection.close()
    return "\n".join(lines)

import sqlite3

def init_bans():
    conn = sqlite3.connect('ward.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS banned (
            username TEXT PRIMARY KEY
        )
    ''')
    conn.close()

def is_banned(username: str) -> bool:
    conn = sqlite3.connect('ward.db')
    cur = conn.execute('SELECT 1 FROM banned WHERE username = ?', (username,))
    res = cur.fetchone() is not None
    conn.close()
    return res

def ban_user(username: str):
    conn = sqlite3.connect('ward.db')
    conn.execute('INSERT OR IGNORE INTO banned (username) VALUES (?)', (username,))
    conn.commit()
    conn.close()

def unban_user(username: str):
    conn = sqlite3.connect('ward.db')
    conn.execute('DELETE FROM banned WHERE username = ?', (username,))
    conn.commit()
    conn.close()




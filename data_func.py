from sheets import get_sheet
from config import PRICES

def get_inventory_summary():
    sheet = get_sheet()
    rows = sheet.get_all_records()
    inventory = {}

    def add_item(name, color_key, size_key=None):
        for row in rows:
            count = row.get(name)
            if count and str(count).isdigit():
                count = int(count)
                if count == 0:
                    continue
                item = name.replace('Количество ', '').strip()
                color = row.get(color_key, '').strip() if color_key else ''
                size = row.get(size_key, '').strip() if size_key else ''
                key = f"{item}, {color}, {size}".strip(', ')
                inventory[key] = inventory.get(key, 0) + count

    add_item('Количество футболок', 'Расцветка футболки', 'Размер футболки')
    add_item('Количество лонгсливов', 'Расцветка лонгслива', 'Размер лонгслива')
    add_item('Количество худи', 'Расцветка худи', 'Размер худи')
    add_item('Количество зип-худи', 'Расцветка зип-худи', 'Размер зип-худи')
    add_item('Шоппер белый', None)
    add_item('Шоппер черный', None)
    add_item('Кружка', None)
    add_item('Значок', None)
    add_item('Блокнот белый', None)
    add_item('Блокнот черный', None)

    result_lines = []
    for k, v in sorted(inventory.items()):
        base_item = k.split(',')[0]
        price = PRICES.get(base_item, '?')
        result_lines.append(f"{k} — {v} шт. (цена: {price} руб.)")

    return "\n".join(result_lines) if result_lines else "Нет данных."
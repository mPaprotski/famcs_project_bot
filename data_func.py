from sheets import get_sheet

def get_inventory_summary():
    sheet = get_sheet()
    rows = sheet.get_all_records()
    inventory = {}

    for row in rows:
        def add_item(name):
            if row.get(name) and str(row[name]).isdigit():
                key = name.replace('Количество ', '').strip()
                inventory[key] = inventory.get(key, 0) + int(row[name])

        add_item('Количество футболок')
        add_item('Количество лонгсливов')
        add_item('Количество худи')
        add_item('Количество худи.1')
        add_item('Шоппер белый')
        add_item('Шоппер черный')
        add_item('Кружка')
        add_item('Значок')
        add_item('Блокнот белый')
        add_item('Блокнот черный')

    result = "\n".join(f"{k} — {v}" for k, v in inventory.items())
    return result if result else "Нет данных."

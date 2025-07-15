from sheets import get_sheet
from config import PRICES, ITEMS

def get_inventory_summary():
    """
    Формирует сводку по остаткам товаров и их общей стоимости.
    Получает данные из Google Sheets, суммирует количество каждого товара с учетом цвета и размера,
    вычисляет стоимость на основе цен из конфигурации и возвращает отформатированную строку.
    
    Returns:
        str: Список товаров с количеством и общей стоимостью или сообщение "Нет данных", если товары отсутствуют.
    """
    main_price = 0
    sheet = get_sheet()
    rows = sheet.get_all_records()
    inventory = {}

    def add_item(item):
        """
        Суммирует количество товаров для инвентаря.
        Обрабатывает строки таблицы, группирует товары по названию, цвету и размеру, добавляет их в словарь inventory.
        
        Args:
            item (dict): Словарь с информацией о товаре из конфигурации ITEMS.
        """
        for row in rows:
            count = row.get(item['count_key'])
            if count and str(count).isdigit():
                count = int(count)
                if count == 0:
                    continue
                color = row.get(item['color_key'], '').strip() if item['color_key'] else ''
                size = row.get(item['size_key'], '').strip() if item['size_key'] else ''
                key = f"{item['name']} {color} {size}".strip()
                inventory[key] = inventory.get(key, 0) + count

    for item in ITEMS:
        add_item(item)

    result_lines = []
    for k, v in sorted(inventory.items()):
        price_per_item = None
        lower_k = k.lower()
        for item in ITEMS:
            if item['price_key'] in lower_k:
                price_per_item = PRICES.get(item['price_key'], 0)
                break

        total_price = price_per_item * v if price_per_item is not None else 0
        result_lines.append(f"<b>{k}</b> - <b>{v}</b> шт.\n")
        
        main_price += total_price
    
    result_lines.append(f"\n<code><b>Итоговая сумма:\n{main_price} руб.</b></code>")

    return "\n".join(result_lines) if result_lines else "Нет данных."
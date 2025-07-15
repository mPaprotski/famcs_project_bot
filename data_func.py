from sheets import get_sheet
from config import PRICES, ITEMS

def get_inventory_summary():
    """
    Формирует сводную информацию о текущих остатках товаров и их общей стоимости.
    
    Получает данные из Google Sheets, анализирует количество каждого товара,
    рассчитывает общую стоимость инвентаря и возвращает отформатированную строку
    с результатами.
    
    Returns:
        str: Отформатированная строка с перечнем товаров, их количеством 
             и общей стоимостью, либо сообщение "Нет данных", если товаров нет.
             
    Формат вывода:
        [Название товара] - [Количество] шт.
        ...
        Итоговая сумма: [Сумма] руб.
    """
    main_price = 0
    sheet = get_sheet()
    rows = sheet.get_all_records()
    inventory = {}

    def add_item(item):
        """
        Внутренняя функция для добавления товаров в инвентарь.
        
        Args:
            item (dict): Словарь с информацией о товаре из ITEMS
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

    # Обрабатываем все типы товаров из ITEMS
    for item in ITEMS:
        add_item(item)

    # Формируем результат
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
    
    # Добавляем итоговую сумму
    result_lines.append(f"\n<code><b>Итоговая сумма:\n{main_price} руб.</b></code>")

    return "\n".join(result_lines) if result_lines else "Нет данных."
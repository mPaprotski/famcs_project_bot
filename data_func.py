from sheets import get_sheet
from config import PRICES

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

    def add_item(name, color_key, size_key=None):
        """
        Внутренняя функция для добавления товаров в инвентарь.
        
        Args:
            name (str): Название поля с количеством товара
            color_key (str|None): Поле с цветом товара (если есть)
            size_key (str|None): Поле с размером товара (если есть)
            
        Действия:
            - Анализирует все строки таблицы
            - Суммирует количество товаров с одинаковыми характеристиками
            - Сохраняет результат в словарь inventory
        """
        for row in rows:
            count = row.get(name)
            if count and str(count).isdigit():
                count = int(count)
                if count == 0:
                    continue
                item = name.replace('Количество ', ' ').strip()
                color = row.get(color_key, '').strip() if color_key else ''
                size = row.get(size_key, '').strip() if size_key else ''
                key = f"{item} {color} {size}".strip(' ')
                inventory[key] = inventory.get(key, 0) + count

    # Обрабатываем все типы товаров
    add_item('Количество футболка', 'Расцветка футболки', 'Размер футболки')
    add_item('Количество лонгслив', 'Расцветка лонгслива', 'Размер лонгслива')
    add_item('Количество худи', 'Расцветка худи', 'Размер худи')
    add_item('Количество зип-худи', 'Расцветка зип-худи', 'Размер зип-худи')
    add_item('Шоппер белый', None)
    add_item('Шоппер черный', None)
    add_item('Кружка', None)
    add_item('Значок', None)
    add_item('Блокнот белый', None)
    add_item('Блокнот черный', None)

    # Формируем результат
    result_lines = []
    price_per_item = None
    for k, v in sorted(inventory.items()):
        lower_k = k.lower()
        for name, price in PRICES.items():
            if name in lower_k:
                price_per_item = price
                break

        if price_per_item is not None:
            total_price = price_per_item * v
            result_lines.append(f"<b>{k.capitalize()}</b> - <b>{v}</b> шт.\n")
        else:
            result_lines.append(f"{k} - {v} шт.\nцена: ? руб.")
        
        main_price += total_price
    
    # Добавляем итоговую сумму
    result_lines.append(f"\n<code><b>Итоговая сумма:\n{main_price} руб.</b></code>")

    return "\n".join(result_lines) if result_lines else "Нет данных."
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import SPREADSHEET_ID

def get_sheet():
    """
    Устанавливает соединение с Google Sheets API и возвращает объект рабочего листа.
    
    Функция выполняет аутентификацию с использованием сервисного аккаунта Google Cloud,
    авторизует клиент для работы с Google Sheets API и открывает конкретный рабочий лист
    в указанной таблице.
    
    Returns:
        gspread.Worksheet: Объект рабочего листа Google Sheets для дальнейшей работы
        
    Raises:
        gspread.exceptions.APIError: Если произошла ошибка при доступе к API
        gspread.exceptions.SpreadsheetNotFound: Если таблица с указанным ID не найдена
        gspread.exceptions.WorksheetNotFound: Если указанный рабочий лист не существует
        
    Требования:
        - Файл credentials.json с данными сервисного аккаунта должен существовать
        - У сервисного аккаунта должны быть права на доступ к таблице
        - В конфигурации должен быть указан корректный SPREADSHEET_ID
    """
    # Области доступа для работы с Google Sheets API
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # Создание учетных данных из файла сервисного аккаунта
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    
    # Авторизация клиента для работы с API
    client = gspread.authorize(creds)
    
    # Открытие конкретного рабочего листа в таблице
    return client.open_by_key(SPREADSHEET_ID).worksheet("Форма для выдачи")
import requests
from bs4 import BeautifulSoup
from serpapi import GoogleSearch
import gspread

# API-ключ SerpApi
API_KEY = "f73ed154c1d13673b73da5b3b60a16ca3982c8885b15c60afc80b2475219e7c9"

def get_search_results():
    """Получение результатов поиска из SerpApi."""
    params = {
        "engine": "google",
        "q": "купить холодильник в Москве",
        "hl": "ru",
        "gl": "ru",
        "num": 10,  # Количество результатов на странице
        "api_key": API_KEY
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    # Проверка наличия блока `organic_results`
    if "organic_results" in results:
        return results["organic_results"]
    else:
        print("Блок 'organic_results' отсутствует в результатах поиска.")
        return []

def extract_price_from_page(url):
    """Парсинг страницы для извлечения цены."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Попытка найти цену по популярным тегам
        price = soup.find('div', class_='ChPIuf YrbPuc')  # Пример div для цены
        if price:
            return price.get_text(strip=True)
        else:
            # Альтернативный поиск
            price_alt = soup.find(string=lambda t: t and ('₽' in t or 'руб' in t))
            if price_alt:
                return price_alt.strip()
            else:
                return "Цена не найдена"
    except requests.RequestException as e:
        return f"Ошибка при получении страницы: {e}"

def extract_keywords_from_page(url):
    """Парсинг страницы для извлечения ключевых слов из мета-тега keywords."""
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Извлекаем мета-тег keywords
        meta_keywords = soup.find("meta", attrs={"name": "keywords"})
        if meta_keywords:
            return meta_keywords.get("content", "Нет ключевых слов")
        else:
            return "Ключевые слова не найдены"
    except requests.RequestException as e:
        return f"Ошибка при получении страницы: {e}"

def write_to_google_sheets(data):
    """Добавляет данные в Google Таблицы."""
    # Авторизация с использованием JSON-ключа
    gc = gspread.service_account(filename="credentials.json")
    
    # Открываем таблицу
    spreadsheet = gc.open("SheetName")
    
    # Основной лист с результатами
    try:
        main_worksheet = spreadsheet.worksheet("Results")
    except gspread.exceptions.WorksheetNotFound:
        main_worksheet = spreadsheet.add_worksheet(title="Results", rows="100", cols="20")
    
    # Заголовки для основного листа
    headers = ["ID", "Заголовок", "Ссылка", "Описание", "Цена"]
    main_worksheet.clear()
    main_worksheet.append_row(headers)
    
    # Создаём лист для ключевых слов
    try:
        keywords_worksheet = spreadsheet.worksheet("Keywords")
    except gspread.exceptions.WorksheetNotFound:
        keywords_worksheet = spreadsheet.add_worksheet(title="Keywords", rows="100", cols="10")
    
    # Заголовки для листа с ключевыми словами
    keyword_headers = ["ID", "Ключевое слово"]
    keywords_worksheet.clear()
    keywords_worksheet.append_row(keyword_headers)
    
    # Счётчик ID для каждой записи
    record_id = 1
    keyword_rows = []  # Для массовой записи ключевых слов
    result_rows = []   # Для массовой записи в основной лист

    # Запись данных
    for result in data:
        title, link, snippet, keywords_snippet, price, keywords_meta = result

        # Добавляем данные для основного листа
        result_rows.append([record_id, title, link, snippet, price])
        
        # Обработка ключевых слов
        unique_keywords = set(keywords_snippet.split(", ") + keywords_meta.split(", "))
        for keyword in unique_keywords:
            keyword_rows.append([record_id, keyword.strip()])

        record_id += 1

    # Массовая запись в основной лист
    if result_rows:
        main_worksheet.update(f"A2:E{len(result_rows) + 1}", result_rows)

    # Массовая запись в лист ключевых слов
    if keyword_rows:
        keywords_worksheet.update(f"A2:B{len(keyword_rows) + 1}", keyword_rows)



def main():
    """Основная функция."""
    print("Получение результатов из SerpApi...")
    search_results = get_search_results()
    rows = []

    for result in search_results:
        title = result.get("title", "Нет названия")
        link = result.get("link", "Нет ссылки")
        snippet = result.get("snippet", "Нет описания")
        
        print(f"\nЗаголовок: {title}")
        print(f"Ссылка: {link}")
        print(f"Описание: {snippet}")
        
        # Извлечение ключевых слов из title и snippet
        keywords_from_snippet = set(title.split() + snippet.split())
        print(f"Ключевые слова (title + snippet): {', '.join(keywords_from_snippet)}")
        
        # Парсинг страницы для получения цены
        price = extract_price_from_page(link) if link != "Нет ссылки" else "Нет ссылки"
        print(f"Цена: {price}")
        
        # Извлечение ключевых слов из мета-тегов страницы
        keywords_from_meta = extract_keywords_from_page(link) if link != "Нет ссылки" else "Нет ссылки"
        print(f"Ключевые слова (meta): {keywords_from_meta}")
        
        # Добавляем данные в строки
        rows.append([
            title,
            link,
            snippet,
            ", ".join(keywords_from_snippet),
            price,
            keywords_from_meta,
        ])
    
    # Запись данных в Google Таблицы
    write_to_google_sheets(rows)

if __name__ == "__main__":
    main()

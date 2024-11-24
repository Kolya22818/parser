# import requests
# from bs4 import BeautifulSoup

# # Укажите ваш API-ключ и CX
# API_KEY = "AIzaSyCrpSmuHPU8uJT1e4A1PX_ODg_gGWquN_8"
# CX = "32b05b95271394d27"

# params = {
#     "key": API_KEY,
#     "cx": CX,
#     "q": "холодильник купить москва",
#     "hl": "ru",
#     "gl": "ru",
#     "num": 5  # Получаем 5 результатов
# }

# def get_search_results():
#     """Получение результатов поиска Google Custom Search API"""
#     url = "https://www.googleapis.com/customsearch/v1"
#     response = requests.get(url, params=params)
#     if response.status_code == 200:
#         try:
#             data = response.json()
#             return data.get("items", [])
#         except ValueError:
#             print("Ошибка преобразования JSON")
#             return []
#     else:
#         print(f"Ошибка запроса: {response.status_code}")
#         return []

# def extract_price_from_page(url):
#     """Парсинг страницы для извлечения цены"""
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
#     }
#     try:
#         response = requests.get(url, headers=headers, timeout=10)
#         response.raise_for_status()
#         soup = BeautifulSoup(response.text, 'html.parser')

#         # Ищем div с классами ChPIuf YrbPuc
#         price_div = soup.find('div', class_='ChPIuf YrbPuc')
#         if price_div:
#             return price_div.get_text(strip=True)
#         else:
#             return "Цена не найдена"
#     except requests.RequestException as e:
#         print(f"Ошибка при запросе {url}: {e}")
#         return "Ошибка при получении страницы"

# def main():
#     search_results = get_search_results()
#     for item in search_results:
#         title = item.get('title', 'Нет заголовка')
#         link = item.get('link', 'Нет ссылки')
#         print(f"Заголовок: {title}\nСсылка: {link}")
#         if link != 'Нет ссылки':
#             price = extract_price_from_page(link)
#             print(f"Цена: {price}\n")

# if __name__ == "__main__":
#     main()

import requests
from bs4 import BeautifulSoup
from serpapi import GoogleSearch

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

def main():
    """Основная функция."""
    print("Получение результатов из SerpApi...")
    search_results = get_search_results()

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
        if link != "Нет ссылки":
            print("Парсинг страницы для получения цены...")
            price = extract_price_from_page(link)
            print(f"Цена: {price}")
            
            # Извлечение ключевых слов из мета-тегов страницы
            print("Извлечение ключевых слов из мета-тегов...")
            keywords_from_meta = extract_keywords_from_page(link)
            print(f"Ключевые слова (meta): {keywords_from_meta}")

if __name__ == "__main__":
    main()
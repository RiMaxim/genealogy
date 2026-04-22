import os
import time
import requests
import urllib3
import argparse
import shutil
from bs4 import BeautifulSoup
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_last_page_number(base_url, search_params):
    """Определяет номер последней страницы результатов"""
    search_params["page"] = 1
    response = requests.get(base_url, params=search_params, verify=False)

    if response.status_code != 200:
        print("Ошибка при определении последней страницы")
        return 1

    soup = BeautifulSoup(response.text, 'html.parser')

    # Ищем все ссылки пагинации в <ul class="pagination">
    page_links = soup.select('ul.pagination li a')

    if not page_links:
        print("Пагинация не найдена, возвращаю 1")
        return 1

    last_page = 1
    for link in page_links:
        href = link.get('href', '')
        match = re.search(r'page=(\d+)', href)
        if match:
            page_num = int(match.group(1))
            if page_num > last_page:
                last_page = page_num

    return last_page

def download_pages(base_url, search_params, end_page, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    for page in range(1, end_page + 1):
        search_params["page"] = page
        response = requests.get(base_url, params=search_params, verify=False)
        if response.status_code == 200:
            file_path = os.path.join(output_dir, f"page_{page}.html")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"Скачана страница {page}/{end_page}")
            time.sleep(1)
        else:
            print(f"Ошибка при скачивании страницы {page}: {response.status_code}")

def process_files(output_dir, end_page, output_filename):
    all_results = []

    for page in range(1, end_page + 1):
        input_file = os.path.join(output_dir, f"page_{page}.html")
        if not os.path.exists(input_file):
            print(f"Файл не найден: {input_file}")
            continue

        with open(input_file, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')

        for img in soup.find_all('img'):
            src = img.get('src', '')
            alt = img.get('alt', '').strip()

            if 'jpg' in src:

                # Пропускаем строку с категорией (иконка)
                if 'sb_category_dot1.jpg' in src:
                    continue

                # Если относительный путь - преобразуем в абсолютный
                if src.startswith('/'):
                    src = f"https://genealogy.inje.ac.kr{src}"

                # Заменяем имя файла на OPS/000, если ссылка в /data/
                if src.startswith("https://genealogy.inje.ac.kr/data/") and src.endswith(".jpg"):
                    parts = src.rstrip('/').split('/')
                    src = '/'.join(parts[:-1]) + '/OPS/000'

                if alt and src:
                    # Используем табуляцию между alt и src
                    all_results.append(f"{alt}\t{src}")

        print(f"Обработана страница {page}/{end_page}")

    # Удаляем дубликаты, сохраняя порядок
    seen = set()
    unique_results = []
    for item in all_results:
        if item not in seen:
            seen.add(item)
            unique_results.append(item)

    with open(output_filename, 'w', encoding='utf-8') as f:
        for line in unique_results:
            f.write(line + '\n')

    print(f"Сохранено {len(unique_results)} результатов в файл {output_filename}")

def main():
    parser = argparse.ArgumentParser(description='Скачивание и парсинг сайта Inje Genealogy')
    parser.add_argument('--surname', type=str, required=True, help='Фамилия для поиска (на корейском)')
    parser.add_argument('--output-dir', type=str, default="inje_pages", help='Папка для HTML-страниц')
    parser.add_argument('--output-file', type=str, required=True, help='Финальный TSV-файл')
    parser.add_argument('--keep-html', action='store_true', help='Не удалять HTML-файлы после обработки')
    args = parser.parse_args()

    base_url = "https://genealogy.inje.ac.kr/search/index.php"
    search_params = {
        "c": "통합검색",
        "w": args.surname,
        "o": "REGISTER",
        "s": "desc",
        "set_search_cate": "",
        "set_u": "",
        "set_u2": "",
        "set_u3": ""
    }

    print(f"Поиск по фамилии: {args.surname}")
    end_page = get_last_page_number(base_url, search_params)
    print(f"Найдено страниц: {end_page}")

    download_pages(base_url, search_params, end_page, args.output_dir)
    process_files(args.output_dir, end_page, args.output_file)

    if not args.keep_html:
        try:
            shutil.rmtree(args.output_dir)
            print(f"Удалена папка с HTML: {args.output_dir}")
        except Exception as e:
            print(f"Ошибка при удалении папки: {e}")

if __name__ == "__main__":
    main()

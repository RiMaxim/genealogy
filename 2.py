import os
import sys
import requests
from urllib.parse import urlparse
import urllib3

# Отключаем предупреждения о небезопасном HTTPS
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def process_file(input_file):
    with open(input_file, 'r') as f, open('tmp3', 'w') as out:
        for line in f:
            if line.strip().startswith('#') or not line.strip():
                continue
            
            parts = line.strip().split('\t')
            if len(parts) < 2:
                parts = line.strip().split()
                if len(parts) < 2:
                    continue
            
            base_url = parts[1]
            folder = urlparse(base_url).path.split('/')[5] if len(urlparse(base_url).path.split('/')) > 5 else "unknown"
            out.write(f"{line.strip()}\t{folder}\n")

def download_images():
    with open('tmp3', 'r') as f:
        for line in f:
            if line.strip().startswith('#') or not line.strip():
                continue
            
            parts = line.strip().split('\t')
            if len(parts) < 3:
                continue
            
            _, base_url, folder = parts[0], parts[1], parts[2]
            
            print(f"Работаю с папкой: {folder}")
            os.makedirs(folder, exist_ok=True)
            
            i = 0
            while True:
                filename = f"page-{i:05d}.jpg"
                url = f"{base_url}/{filename}"
                filepath = os.path.join(folder, filename)
                
                if os.path.exists(filepath):
                    print(f"Пропускаю {filename} (уже существует)")
                else:
                    print(f"Пробую скачать {filename}...")
                    try:
                        # Проверяем, существует ли файл
                        response = requests.head(url, verify=False, timeout=10)
                        if response.status_code != 200:
                            print(f"Файл {filename} не найден. Завершаю загрузку.")
                            break
                        
                        # Скачиваем файл
                        response = requests.get(url, verify=False, timeout=30)
                        response.raise_for_status()  # Проверка на ошибки HTTP
                        with open(filepath, 'wb') as img_file:
                            img_file.write(response.content)
                    except requests.exceptions.RequestException as e:
                        print(f"Ошибка при загрузке {url}: {e}")
                        break
                
                i += 1

def main():
    if len(sys.argv) < 2:
        print("Использование: python script.py <input_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    process_file(input_file)
    download_images()

    # Удаляем временные файлы
    for tmp_file in ['tmp', 'tmp2', 'tmp3']:
        if os.path.exists(tmp_file):
            os.remove(tmp_file)

if __name__ == "__main__":
    main()

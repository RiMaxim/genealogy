import os
from PIL import Image
import sys

def jpg_to_pdf(subfolder_name):
    # Базовый путь, где лежат подпапки
    base_path = r"/home/lam2/scripts/download_book2/이씨"

    # Полный путь к подпапке
    folder_path = os.path.join(base_path, subfolder_name)

    # Получаем список JPG-файлов в папке
    jpg_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.jpg')]

    if not jpg_files:
        print("В папке нет JPG-файлов!")
        return

    # Сортируем файлы по имени (чтобы 1, 2, 10 шли правильно — можно улучшить через key=int)
    jpg_files.sort()

    # Создаем список изображений
    images = [Image.open(os.path.join(folder_path, jpg)).convert("RGB") for jpg in jpg_files]

    # Имя PDF = имя папки + .pdf
    pdf_name = subfolder_name + ".pdf"
    pdf_path = os.path.join(folder_path, pdf_name)

    # Сохраняем PDF
    if images:
        images[0].save(
            pdf_path,
            "PDF",
            resolution=100.0,
            save_all=True,
            append_images=images[1:]
        )
        print(f"PDF создан: {pdf_path}")
    else:
        print("Не удалось загрузить изображения!")

# если запускать так: python 4.py 6BC2A48B-BF23-FE74-2FD8-1363494BC5A4
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Укажите подпапку как аргумент!")
    else:
        jpg_to_pdf(sys.argv[1])

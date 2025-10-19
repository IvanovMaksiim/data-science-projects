from pdf2image import convert_from_path
import os
"""
Конвертация PDF в PNG-изображения (по одной странице на файл).
Используется poppler для рендеринга страниц.
"""

pdf_path = r"C:\Users\Максим\PycharmProjects\Progect_test\p&id_project\pythonProject1\.venv\scan\Итог1.pdf"
os.makedirs('pages', exist_ok=True)

poppler_path = r'C:\Program Files\poppler-25.07.0\poppler-25.07.0\Library\bin'

pages = convert_from_path(pdf_path,
                          dpi=600,
                          fmt="png",
                          output_folder="pages",
                          poppler_path=poppler_path)

print(f"Сохранено {len(pages)} страниц в папку 'pages'")
"""
Создание базовых бакетов
models - для сохранение последней и архивации предудущих моделей
patients-data - для сохранения предсказания delta
data - данны и метаданные о исследовании delta
"""

from minio import Minio
from minio.error import S3Error


minio_client = Minio(
    "minio:9000",  #
    access_key="minioadmin",
    secret_key="minioadmin123",
    secure=False  
)

buckets = ["patients-data", "data", "models"]

for bucket in buckets:
    try:
        if not minio_client.bucket_exists(bucket):
            minio_client.make_bucket(bucket)
            print(f"Бакет {bucket} создан.")
        else:
            print(f"Бакет {bucket} уже существует.")
    except S3Error as err:
        print(f"Ошибка при создании бакета {bucket}: {err}")

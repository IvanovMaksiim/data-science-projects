"""
Определяет последний id чтобы не читать все данные
Читает новые строки из минио
Разделяет данные по колонкам для разных таблиц
Загружает модели из минио
Прдсказанния, отправка сообщения в случае диашноза 1
Запись разделенных данных по таблицам в постгрес и delta предсказаний сырых в minio
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, expr, udf, first
from pyspark.sql.types import TimestampType, ArrayType, DoubleType
from pyspark.ml.linalg import VectorUDT
from pyspark.ml import PipelineModel
import pyspark.sql.functions as F
import requests


postgres_url = "jdbc:postgresql://postgres:5432/sensors"
postgres_properties = {"user": "admin", "password": "admin", "driver": "org.postgresql.Driver"}

TELEGRAM_BOT_TOKEN = "8421305977:AAGf3ZiiD9hXB8muBt2bnhzwCRtKPXBi0B8"
TELEGRAM_CHAT_ID = "1442715436"


def send_telegram_message(text: str):
    """
    отпарвка сообщения в бот телеграма
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    try:
        requests.post(url, json=payload)
        print(f"Telegram уведомление отправлено: {text}")
    except Exception as e:
        print("Ошибка при отправке в Telegram:", e)


spark = (
    SparkSession.builder.appName("MinioToPostgresPatientsML")
    .master("spark://spark-master:7077")
    .config(
        "spark.jars",
        "/opt/jars/hadoop-aws-3.3.4.jar,"
        "/opt/jars/aws-java-sdk-bundle-1.12.262.jar,"
        "/opt/jars/commons-pool2-2.11.1.jar,"
        "/opt/jars/postgresql-42.6.0.jar,"
        "/opt/jars/delta-core_2.12-2.4.0.jar,"
        "/opt/jars/delta-storage-2.4.0.jar"
    )
    .config("spark.executor.cores", "1")
    .config("spark.executor.memory", "2g")
    .config("spark.executor.instances", "2")
    .config("spark.driver.cores", "1")
    .config("spark.cores.max", "2")
    .config("spark.driver.memory", "2g")
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000")
    .config("spark.hadoop.fs.s3a.access.key", "minioadmin")
    .config("spark.hadoop.fs.s3a.secret.key", "minioadmin123")
    .config("spark.hadoop.fs.s3a.path.style.access", "true")
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("WARN")


existing_max_id_df = spark.read.jdbc(
    postgres_url,
    "diagnosis_2",
    properties=postgres_properties
).agg(F.max("id").alias("max_id"))

max_id = existing_max_id_df.collect()[0]["max_id"] or 0
print(f"Max existing ID in diagnosis_2: {max_id}")


df_new = spark.read.format("delta") \
    .load("s3a://patients-data/delta/patients/") \
    .filter(F.col("id") > max_id)
print(f"New rows to process: {df_new.count()}")

if df_new.count() == 0:
    print("Нет новых данных для обработки. Выход.")
    exit(0)


meta_df = df_new.select(
    col("id"),
    col("exam_date").cast(TimestampType()),
    col("diagnosis"),
    col("age"),
    col("region")
)
feature_cols = [
    "radius_mean", "texture_mean", "perimeter_mean", "area_mean", "smoothness_mean",
    "compactness_mean", "concavity_mean", "concave_points_mean", "symmetry_mean", "fractal_dimension_mean",
    "radius_se", "texture_se", "perimeter_se", "area_se", "smoothness_se",
    "compactness_se", "concavity_se", "concave_points_se", "symmetry_se", "fractal_dimension_se",
    "radius_worst", "texture_worst", "perimeter_worst", "area_worst", "smoothness_worst",
    "compactness_worst", "concavity_worst", "concave_points_worst", "symmetry_worst", "fractal_dimension_worst"
]
features_df = df_new.select(col("id"), *feature_cols)

diagnosis_df = df_new.select(
    col("id"),
    when(col("diagnosis") == "M", 1).otherwise(0).alias("diagnosis")
)


try:
    rf_model = PipelineModel.load("s3a://models/rf/latest")
    lr_model = PipelineModel.load("s3a://models/logreg/latest")
    print("Модели успешно загружены")
except Exception as e:
    print(f"Ошибка загрузки моделей: {e}")


df_flat = df_new.select("id", *feature_cols)
print(f"df_flat: {df_flat.count()} строк")

rf_preds = rf_model.transform(df_flat).select("id", col("prediction").alias("rf_pred"),
                                              col("probability").alias("rf_prob"))
print(f"rf_preds: {rf_preds.count()} строк")

lr_features = [
    'texture_mean', 'area_mean',
    'smoothness_mean', 'concave_points_mean',
    'symmetry_mean', 'fractal_dimension_mean',
    'texture_se', 'perimeter_se',
    'smoothness_se', 'symmetry_se',
    'symmetry_worst', 'compactness_se',
    'concave_points_se',
    'smoothness_worst',
    'concavity_worst'
]
df_lr = df_flat.select(["id"] + lr_features)
lr_preds = lr_model.transform(df_lr).select("id", col("prediction").alias("lr_pred"),
                                            col("probability").alias("lr_prob"))
print(f"lr_preds: {lr_preds.count()} строк")

vector_to_array_udf = udf(lambda v: v.toArray().tolist(), ArrayType(DoubleType()))
rf_probs = rf_preds.withColumn("rf_probs", vector_to_array_udf("rf_prob"))
lr_probs = lr_preds.withColumn("lr_probs", vector_to_array_udf("lr_prob"))
print(f"rf_probs: {rf_probs.count()} строк")
print(f"lr_probs: {lr_probs.count()} строк")


joined = rf_probs.join(lr_probs, on="id")
print(f"joined: {joined.count()} строк")

final = joined.withColumn(
    "avg_probs",
    expr("transform(sequence(0, size(rf_probs)-1), i -> (rf_probs[i] + lr_probs[i]) / 2.0)")
).withColumn(
    "final_prediction",
    expr(
        "aggregate(sequence(0, size(avg_probs)-1), 0, (acc, i) -> CASE WHEN avg_probs[i] > avg_probs[acc] THEN i ELSE acc END)")
)


final_unique = final.groupBy("id").agg(
    F.first("rf_probs").alias("rf_probs"),
    F.first("lr_probs").alias("lr_probs"),
    F.first("avg_probs").alias("avg_probs"),
    F.first("final_prediction").alias("final_prediction")
)
print(f"final_unique: {final_unique.count()} строк")


try:
    meta_df.write.jdbc(
        url=postgres_url,
        table="patients_meta_2",
        mode="append",
        properties=postgres_properties
    )
    print("patients_meta_2 записана")

    features_df.write.jdbc(
        url=postgres_url,
        table="patients_info_2",
        mode="append",
        properties=postgres_properties
    )
    print("patients_info_2 записана")

    diagnosis_df.write.jdbc(
        url=postgres_url,
        table="diagnosis_2",
        mode="append",
        properties=postgres_properties
    )
    print("diagnosis_2 записана")

    predictions_df = final_unique.select(
        "id",
        "final_prediction"
    )

    predictions_df.write.jdbc(
        url=postgres_url,
        table="predictions_table_2",
        mode="append",
        properties=postgres_properties
    )
    print("predictions_table_2 записана")

    alert_ids = [row["id"] for row in final_unique.filter(col("final_prediction") == 1).select("id").collect()]
    if alert_ids:
        send_telegram_message(
            f"Обнаружены положительные предсказания!\nID пациентов: {', '.join(map(str, alert_ids))}")

except Exception as e:
    print(f"Ошибка при записи в PostgreSQL: {e}")
    raise

final_unique.select("id", "rf_probs", "lr_probs", "avg_probs", "final_prediction") \
    .write.format("delta").mode("append").option("mergeSchema", "true") \
    .save("s3a://data/predictions_delta")

print("Batch job успешно выполнена: данные и ML предсказания сохранены в PostgreSQL и MinIO")

spark.stop()
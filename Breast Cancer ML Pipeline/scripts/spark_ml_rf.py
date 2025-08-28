"""
Обучение модели RandomForestClassifier с фиксированными параметраи взятыми из sklearn
"""

from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import RandomForestClassifier
from datetime import datetime
from pyspark.sql.functions import col, when

spark = (
    SparkSession.builder.appName("KafkaToMinioPatients")
    .master("spark://spark-master:7077")
    .config(
        "spark.jars",
        "/opt/jars/spark-sql-kafka-0-10_2.12-3.4.1.jar,"
        "/opt/jars/kafka-clients-3.5.1.jar,"
        "/opt/jars/spark-token-provider-kafka-0-10_2.12-3.4.1.jar,"
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
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")


pg_url = "jdbc:postgresql://postgres:5432/sensors"
pg_properties = {
    "user": "admin",
    "password": "admin",
    "driver": "org.postgresql.Driver"
}
X1 = spark.read.jdbc(
    url=pg_url,
    table="patients_info_2",
    properties=pg_properties
)
y1 = spark.read.jdbc(
    url=pg_url,
    table="diagnosis_2",
    properties=pg_properties
)
data = X1.join(y1, on="id").drop("id").withColumnRenamed("diagnosis", "label")

feature_cols = [c for c in data.columns if c not in ("label", "id")]

assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")

rf = RandomForestClassifier(
    labelCol="label",
    featuresCol="features",
    predictionCol="prediction",
    probabilityCol="probability",
    rawPredictionCol="rawPrediction",
    maxDepth=5,
    numTrees=50,
    seed=42
)

pipeline = Pipeline(stages=[assembler, rf])

full_model = pipeline.fit(data)

bucket_name = "models"
latest_dir = "rf/latest"
archived_dir = f"rf/model_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

latest_path_str = f"s3a://{bucket_name}/{latest_dir}"
archived_path_str = f"s3a://{bucket_name}/{archived_dir}"

uri = spark._jvm.java.net.URI(latest_path_str)
fs = spark._jvm.org.apache.hadoop.fs.FileSystem.get(uri, spark._jsc.hadoopConfiguration())

latest_path = spark._jvm.org.apache.hadoop.fs.Path(latest_path_str)
archived_path = spark._jvm.org.apache.hadoop.fs.Path(archived_path_str)

if fs.exists(latest_path):
    fs.rename(latest_path, archived_path)
    print(f"Старая модель перемещена в {archived_dir}")

full_model.write().overwrite().save(latest_path_str)
print(f"Новая модель сохранена в s3://{bucket_name}/{latest_dir}/")

spark.stop()

"""
Обечение модели LogisticRegression с подбором гиперпараметров с крос валидацией, сохранение лучшей модели в минио
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.ml import Pipeline
from pyspark.ml.feature import VectorAssembler, RobustScaler
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.mllib.evaluation import MulticlassMetrics
from pyspark.ml.classification import LogisticRegressionModel

import os
from tempfile import TemporaryDirectory
from datetime import datetime

from minio import Minio
from minio.error import S3Error
from minio.commonconfig import CopySource

# выбор колонок после EDA
# подбор параметров потому что перенос не очень из sklearn, крос-валидация, лучшую сохраняем
spark = (
    SparkSession.builder.appName("SparkMlLog")
    .config(
        "spark.jars",
        "/opt/jars/hadoop-aws-3.3.4.jar,"
        "/opt/jars/aws-java-sdk-bundle-1.12.262.jar,"
        "/opt/jars/commons-pool2-2.11.1.jar,"
        "/opt/jars/postgresql-42.6.0.jar,"
    )
    .config("spark.executor.cores", "2")
    .config("spark.executor.memory", "2g")
    .config("spark.executor.instances", "2")
    .config("spark.driver.cores", "2")
    .config("spark.cores.max", "2")
    .config("spark.driver.memory", "2g")
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000")
    .config("spark.hadoop.fs.s3a.access.key", "minioadmin")
    .config("spark.hadoop.fs.s3a.secret.key", "minioadmin123")
    .config("spark.hadoop.fs.s3a.path.style.access", "true")
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("WARN")

pg_url = "jdbc:postgresql://postgres:5432/sensors"
pg_properties = {
    "user": "admin",
    "password": "admin",
    "driver": "org.postgresql.Driver"
}

columns_filtered = [
    'id',
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
X2 = X1.select(*columns_filtered)

data = X2.join(y1, on="id").drop("id").withColumnRenamed("diagnosis", "label")

feature_cols = [c for c in data.columns if c not in ("label", "id")]
assembler_pipeline = VectorAssembler(inputCols=feature_cols, outputCol="features_vec")

scaler = RobustScaler(inputCol="features_vec", outputCol="features")
lr = LogisticRegression(featuresCol="features", labelCol="label")

pipeline = Pipeline(stages=[assembler_pipeline, scaler, lr])


paramGrid = ParamGridBuilder()\
    .addGrid(lr.regParam, [0.01, 0.1])\
    .addGrid(lr.elasticNetParam, [0.0, 0.5])\
    .build()

evaluator = BinaryClassificationEvaluator(labelCol="label", rawPredictionCol="rawPrediction", metricName="areaUnderROC")

cv = CrossValidator(estimator=pipeline,
                    estimatorParamMaps=paramGrid,
                    evaluator=evaluator,
                    numFolds=2,
                    parallelism=2)

train, test = data.randomSplit([0.8, 0.2], seed=42)

cv_model = cv.fit(train)

best_model = cv_model.bestModel
best_lr_model = None
for stage in best_model.stages:
    if isinstance(stage, LogisticRegressionModel):
        best_lr_model = stage
        break

final_lr = LogisticRegression(regParam=best_lr_model._java_obj.getRegParam(),
                               elasticNetParam=best_lr_model._java_obj.getElasticNetParam())

final_pipeline = Pipeline(stages=[assembler_pipeline, scaler, final_lr])

final_model = final_pipeline.fit(data)

client = Minio(
    endpoint="minio:9000",
    access_key="minioadmin",
    secret_key="minioadmin123",
    secure=False
)

bucket_name = "models"
latest_dir = "logreg/latest"
archived_dir = f"logreg/model_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


if not client.bucket_exists(bucket_name):
    client.make_bucket(bucket_name)

latest_path_str = f"s3a://{bucket_name}/{latest_dir}"
archived_path_str = f"s3a://{bucket_name}/{archived_dir}"

uri = spark._jvm.java.net.URI(latest_path_str)
fs = spark._jvm.org.apache.hadoop.fs.FileSystem.get(uri, spark._jsc.hadoopConfiguration())

latest_path = spark._jvm.org.apache.hadoop.fs.Path(latest_path_str)
archived_path = spark._jvm.org.apache.hadoop.fs.Path(archived_path_str)


if fs.exists(latest_path):
    fs.rename(latest_path, archived_path)
    print(f"Старая модель перемещена в {archived_dir}")

final_model.write().overwrite().save(latest_path_str)
print(f"Новая модель сохранена в s3://{bucket_name}/{latest_dir}/")

spark.stop()


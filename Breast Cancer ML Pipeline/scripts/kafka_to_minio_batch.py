"""
Читает из топика кафка сохраняет в минио в бакете patients сырые данные
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType

spark = (
    SparkSession.builder.appName("KafkaToMinioPatientsBatch")
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

raw_df = (
    spark.read
    .format("kafka")
    .option("kafka.bootstrap.servers", "kafka:9092")
    .option("subscribe", "patients")
    .option("startingOffsets", "earliest")
    .option("endingOffsets", "latest")
    .load()
)

json_df = raw_df.selectExpr("CAST(value AS STRING) as json_str")

# Схемы
features_schema = StructType([
    StructField("radius_mean", DoubleType()),
    StructField("texture_mean", DoubleType()),
    StructField("perimeter_mean", DoubleType()),
    StructField("area_mean", DoubleType()),
    StructField("smoothness_mean", DoubleType()),
    StructField("compactness_mean", DoubleType()),
    StructField("concavity_mean", DoubleType()),
    StructField("concave_points_mean", DoubleType()),
    StructField("symmetry_mean", DoubleType()),
    StructField("fractal_dimension_mean", DoubleType()),
    StructField("radius_se", DoubleType()),
    StructField("texture_se", DoubleType()),
    StructField("perimeter_se", DoubleType()),
    StructField("area_se", DoubleType()),
    StructField("smoothness_se", DoubleType()),
    StructField("compactness_se", DoubleType()),
    StructField("concavity_se", DoubleType()),
    StructField("concave_points_se", DoubleType()),
    StructField("symmetry_se", DoubleType()),
    StructField("fractal_dimension_se", DoubleType()),
    StructField("radius_worst", DoubleType()),
    StructField("texture_worst", DoubleType()),
    StructField("perimeter_worst", DoubleType()),
    StructField("area_worst", DoubleType()),
    StructField("smoothness_worst", DoubleType()),
    StructField("compactness_worst", DoubleType()),
    StructField("concavity_worst", DoubleType()),
    StructField("concave_points_worst", DoubleType()),
    StructField("symmetry_worst", DoubleType()),
    StructField("fractal_dimension_worst", DoubleType()),
])

patient_schema = StructType([
    StructField("id", IntegerType()),
    StructField("age", IntegerType()),
    StructField("region", StringType())
])

schema = StructType([
    StructField("patient", patient_schema),
    StructField("diagnosis", StringType()),
    StructField("date", StringType()),
    StructField("features", features_schema)
])

parsed_df = json_df.select(from_json(col("json_str"), schema).alias("data"))

delta_df = parsed_df.select(
    col("data.patient.id").alias("id"),
    col("data.patient.age").alias("age"),
    col("data.patient.region").alias("region"),
    col("data.date").cast(TimestampType()).alias("exam_date"),
    col("data.diagnosis").alias("diagnosis"),
    *[col(f"data.features.{c.name}").alias(c.name) for c in schema["features"].dataType.fields]
)

(
    delta_df.write
    .format("delta")
    .mode("append")
    .save("s3a://patients-data/delta/patients/")
)

print(f"✅ Batch job finished, rows written: {delta_df.count()}")

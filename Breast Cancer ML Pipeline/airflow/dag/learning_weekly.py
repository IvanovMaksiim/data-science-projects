from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': False,
    'email_on_retry': False,
}

ALL_JARS = ",".join([
    "/opt/jars/postgresql-42.6.0.jar",
    "/opt/jars/commons-pool2-2.11.1.jar",
    "/opt/jars/delta-core_2.12-2.4.0.jar",
    "/opt/jars/delta-storage-2.4.0.jar",
    "/opt/jars/hadoop-aws-3.3.4.jar",
    "/opt/jars/aws-java-sdk-bundle-1.12.262.jar",
    "/opt/jars/spark-sql-kafka-0-10_2.12-3.4.1.jar",
    "/opt/jars/kafka-clients-3.5.1.jar",
    "/opt/jars/spark-token-provider-kafka-0-10_2.12-3.4.1.jar"
])

SPARK_CONF = {
    "spark.hadoop.fs.s3a.endpoint": "http://minio:9000",
    "spark.hadoop.fs.s3a.access.key": "minioadmin",
    "spark.hadoop.fs.s3a.secret.key": "minioadmin123",
    "spark.hadoop.fs.s3a.path.style.access": "true",
    "spark.hadoop.fs.s3a.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem",
    "spark.sql.extensions": "io.delta.sql.DeltaSparkSessionExtension",
    "spark.sql.catalog.spark_catalog": "org.apache.spark.sql.delta.catalog.DeltaCatalog",
    "spark.driver.cores": "1",
    "spark.driver.memory": "4g",
    "spark.executor.cores": "1",
    "spark.executor.memory": "4g",
    "spark.executor.instances": "1"
}

dag = DAG(
    'minio_to_postgres_ml_weekly',
    default_args=default_args,
    description='Переобучение модели — по воскресеньям',
    schedule_interval='0 0 * * 0',
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['spark', 'log', 'ml', 'rf']
)

task1 = SparkSubmitOperator(
    task_id="spark_postgres_to_minio_rf",
    application="/opt/airflow/scripts/spark_ml_rf.py",
    conn_id="spark_default",
    jars=ALL_JARS,
    conf=SPARK_CONF,
    dag=dag
)

task2 = SparkSubmitOperator(
    task_id="spark_postgres_to_minio_log",
    application="/opt/airflow/scripts/spark_ml_log.py",
    conn_id="spark_default",
    jars=ALL_JARS,
    conf=SPARK_CONF,
    dag=dag
)

task1 >> task2
"""
Создание и заполнение первичными данными  таблиц в PostgreSQL
"""

import time
import psycopg2
import pandas as pd
import numpy as np


DB_CONFIG = {
    'host': 'postgres',
    'port': 5432,
    'dbname': 'sensors',
    'user': 'admin',
    'password': 'admin'
}

def wait_for_postgres():
    """
    Попытка подключения к PostgreSQL с повторными попытками
    """
    while True:
        try:
            print("Trying to connect to PostgreSQL...")
            conn = psycopg2.connect(**DB_CONFIG)
            print("Connected to PostgreSQL!")
            return conn
        except psycopg2.OperationalError as e:
            print(f"Connection failed: {e}")
            print("Retrying in 5 seconds...")
            time.sleep(5)

def create_patients_info_table(conn):
    sql = """
        CREATE TABLE IF NOT EXISTS patients_info_2 (
            id BIGINT,
            radius_mean DOUBLE PRECISION,
            texture_mean DOUBLE PRECISION,
            perimeter_mean DOUBLE PRECISION,
            area_mean DOUBLE PRECISION,
            smoothness_mean DOUBLE PRECISION,
            compactness_mean DOUBLE PRECISION,
            concavity_mean DOUBLE PRECISION,
            concave_points_mean DOUBLE PRECISION,
            symmetry_mean DOUBLE PRECISION,
            fractal_dimension_mean DOUBLE PRECISION,
            radius_se DOUBLE PRECISION,
            texture_se DOUBLE PRECISION,
            perimeter_se DOUBLE PRECISION,
            area_se DOUBLE PRECISION,
            smoothness_se DOUBLE PRECISION,
            compactness_se DOUBLE PRECISION,
            concavity_se DOUBLE PRECISION,
            concave_points_se DOUBLE PRECISION,
            symmetry_se DOUBLE PRECISION,
            fractal_dimension_se DOUBLE PRECISION,
            radius_worst DOUBLE PRECISION,
            texture_worst DOUBLE PRECISION,
            perimeter_worst DOUBLE PRECISION,
            area_worst DOUBLE PRECISION,
            smoothness_worst DOUBLE PRECISION,
            compactness_worst DOUBLE PRECISION,
            concavity_worst DOUBLE PRECISION,
            concave_points_worst DOUBLE PRECISION,
            symmetry_worst DOUBLE PRECISION,
            fractal_dimension_worst DOUBLE PRECISION
        );
    """
    with conn.cursor() as cur:
        cur.execute(sql)
        conn.commit()

def create_patients_meta_table(conn):
    sql = """
    CREATE TABLE IF NOT EXISTS patients_meta_2 (
        id BIGINT,
        exam_date VARCHAR(30) NOT NULL,
        diagnosis CHAR(1) NOT NULL,
        age INT NOT NULL,
        region VARCHAR(20) NOT NULL
    );
    """
    with conn.cursor() as cur:
        cur.execute(sql)
        conn.commit()

def create_predictions_table(conn):
    sql = """
            CREATE TABLE IF NOT EXISTS predictions_table_2 (
                id BIGINT ,
                final_prediction INT
            );
    """
    with conn.cursor() as cur:
        cur.execute(sql)
        conn.commit()

def create_diagnosis(conn):
    sql = """
        CREATE TABLE IF NOT EXISTS diagnosis_2 (
            id BIGINT,
            diagnosis INT
        );
    """
    with conn.cursor() as cur:
        cur.execute(sql)
        conn.commit()

def load_data_from_csv(conn, table_name, file_path):
    try:
        print(f"Loading data into {table_name} from {file_path}...")
        df = pd.read_csv(file_path, encoding='utf-8', dtype={'id': 'int'})
        with conn.cursor() as cur:
            for index, row in df.iterrows():
                
                if table_name == 'patients_meta_2':
                    cur.execute("""
                        INSERT INTO patients_meta_2 (id, exam_date, diagnosis, age, region)
                        VALUES (%s, %s, %s, %s, %s)
                    """, tuple(row))

                elif table_name == 'patients_info_2':
                    cur.execute("""
                        INSERT INTO patients_info_2 (id, radius_mean, texture_mean, perimeter_mean, area_mean,
                        smoothness_mean, compactness_mean, concavity_mean, concave_points_mean, symmetry_mean,
                        fractal_dimension_mean, radius_se, texture_se, perimeter_se, area_se, smoothness_se,
                        compactness_se, concavity_se, concave_points_se, symmetry_se, fractal_dimension_se,
                        radius_worst, texture_worst, perimeter_worst, area_worst, smoothness_worst, compactness_worst,
                        concavity_worst, concave_points_worst, symmetry_worst, fractal_dimension_worst)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, tuple(row))

                elif table_name == 'diagnosis_2':
                    id_value = int(row['id']) # Явное преобразование в int (почему то без него падает загрузка)
                    diagnosis_value = int(row['diagnosis'])
                    sql = f"INSERT INTO {table_name} (id, diagnosis) VALUES (%s, %s)"
                    cur.execute(sql, (id_value, diagnosis_value))

                elif table_name == 'predictions_table_2':
                    id_value = int(row['id']) # Явное преобразование в int (почему то без него падает загрузка)
                    final_prediction = int(row['final_prediction'])
                    sql = f"INSERT INTO {table_name} (id, final_prediction) VALUES (%s, %s)"
                    cur.execute(sql, (id_value, final_prediction))

            conn.commit()
        print(f"Data loaded into {table_name} successfully.")

    except Exception as e:
        print(f"Error loading data into {table_name}: {e}")

def main():
    try:

        print("Connecting to PostgreSQL...")
        conn = wait_for_postgres()

        print("Creating tables if not exist...")
        create_patients_info_table(conn)
        create_patients_meta_table(conn)
        create_predictions_table(conn)
        create_diagnosis(conn)

        conn.commit()
        print("All tables created or already exist.")


        load_data_from_csv(conn, 'patients_info_2', '/opt/data/patients_info.csv')
        load_data_from_csv(conn, 'diagnosis_2', '/opt/data/diagnosis.csv')
        load_data_from_csv(conn, 'predictions_table_2', '/opt/data/soft_voting_predictions_full.csv')
        load_data_from_csv(conn, 'patients_meta_2', '/opt/data/patients_meta_2.csv')

    except Exception as e:
        print(f"Database initialization failed: {e}")

    finally:
        if 'conn' in locals():
            conn.close()
            print("Connection closed.")

if __name__ == "__main__":
    main()

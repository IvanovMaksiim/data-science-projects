"""
Скрипт генерации данных на основе классического датасета
Генерация файковых метаданных

Бесконечный цикл генерации в топик данных по исследованию в пропорции 60:40

"""

import json
import time
import numpy as np
from confluent_kafka import Producer
from datetime import datetime


M_stats = {
    "radius_mean": {"mean": 17.462830, "std": 3.203971, "min": 10.95, "max": 28.11},
    "texture_mean": {"mean": 21.604906, "std": 3.779470, "min": 10.38, "max": 39.28},
    "perimeter_mean": {"mean": 115.365377, "std": 21.854653, "min": 71.9, "max": 188.5},
    "area_mean": {"mean": 978.376415, "std": 367.937978, "min": 361.6, "max": 2501.0},
    "smoothness_mean": {"mean": 0.102898, "std": 0.012608, "min": 0.07371, "max": 0.1447},
    "compactness_mean": {"mean": 0.145188, "std": 0.053987, "min": 0.04605, "max": 0.3454},
    "concavity_mean": {"mean": 0.160775, "std": 0.075019, "min": 0.02398, "max": 0.4268},
    "concave_points_mean": {"mean": 0.08799, "std": 0.034374, "min": 0.02031, "max": 0.2012},
    "symmetry_mean": {"mean": 0.192909, "std": 0.027638, "min": 0.1308, "max": 0.304},
    "fractal_dimension_mean": {"mean": 0.062898, "std": 0.006702, "min": 0.04996, "max": 0.09744},
    "radius_se": {"mean": 0.726017, "std": 0.439329, "min": 0.1115, "max": 2.873},
    "texture_se": {"mean": 1.09453, "std": 0.672681, "min": 0.3602, "max": 4.885},
    "perimeter_se": {"mean": 5.434804, "std": 3.398956, "min": 0.757, "max": 21.98},
    "area_se": {"mean": 153.646698, "std": 93.971114, "min": 17.85, "max": 542.2},
    "smoothness_se": {"mean": 0.006399, "std": 0.002899, "min": 0.001713, "max": 0.03113},
    "compactness_se": {"mean": 0.049631, "std": 0.02629, "min": 0.004085, "max": 0.1354},
    "concavity_se": {"mean": 0.06402, "std": 0.035253, "min": 0.006248, "max": 0.396},
    "concave_points_se": {"mean": 0.025717, "std": 0.01526, "min": 0.001465, "max": 0.06877},
    "symmetry_se": {"mean": 0.020542, "std": 0.007811, "min": 0.008064, "max": 0.05279},
    "fractal_dimension_se": {"mean": 0.003794, "std": 0.002493, "min": 0.000894, "max": 0.02984},
    "radius_worst": {"mean": 21.134434, "std": 3.761743, "min": 13.01, "max": 36.04},
    "texture_worst": {"mean": 29.318208, "std": 5.434804, "min": 16.67, "max": 49.54},
    "perimeter_worst": {"mean": 141.37033, "std": 29.457055, "min": 85.1, "max": 251.2},
    "area_worst": {"mean": 1422.286321, "std": 597.967743, "min": 508.1, "max": 4254.0},
    "smoothness_worst": {"mean": 0.144845, "std": 0.02187, "min": 0.08822, "max": 0.2226},
    "compactness_worst": {"mean": 0.374824, "std": 0.170372, "min": 0.05131, "max": 1.058},
    "concavity_worst": {"mean": 0.450606, "std": 0.181507, "min": 0.02398, "max": 1.17},
    "concave_points_worst": {"mean": 0.182237, "std": 0.046308, "min": 0.02899, "max": 0.291},
    "symmetry_worst": {"mean": 0.323468, "std": 0.074685, "min": 0.1565, "max": 0.6638},
    "fractal_dimension_worst": {"mean": 0.09153, "std": 0.021553, "min": 0.05504, "max": 0.2075},
}

B_stats = {
    "radius_mean": {"mean": 12.146524, "std": 1.780512, "min": 6.981, "max": 17.85},
    "texture_mean": {"mean": 17.914762, "std": 3.995125, "min": 9.71, "max": 33.81},
    "perimeter_mean": {"mean": 78.075406, "std": 11.807438, "min": 43.79, "max": 114.6},
    "area_mean": {"mean": 462.790196, "std": 134.287118, "min": 143.5, "max": 992.1},
    "smoothness_mean": {"mean": 0.092478, "std": 0.013446, "min": 0.05263, "max": 0.1634},
    "compactness_mean": {"mean": 0.080085, "std": 0.03375, "min": 0.01938, "max": 0.2239},
    "concavity_mean": {"mean": 0.046058, "std": 0.043442, "min": 0.0, "max": 0.4108},
    "concave_points_mean": {"mean": 0.025717, "std": 0.015909, "min": 0.0, "max": 0.08534},
    "symmetry_mean": {"mean": 0.174186, "std": 0.024807, "min": 0.106, "max": 0.2743},
    "fractal_dimension_mean": {"mean": 0.063351, "std": 0.007271, "min": 0.04996, "max": 0.09744},
    "radius_se": {"mean": 0.271, "std": 0.197, "min": 0.02, "max": 1.0},
    "texture_se": {"mean": 0.92, "std": 0.45, "min": 0.2, "max": 2.5},
    "perimeter_se": {"mean": 2.4, "std": 1.5, "min": 0.3, "max": 8.0},
    "area_se": {"mean": 40.0, "std": 20.0, "min": 6.0, "max": 100.0},
    "smoothness_se": {"mean": 0.005, "std": 0.002, "min": 0.001, "max": 0.02},
    "compactness_se": {"mean": 0.02, "std": 0.01, "min": 0.002, "max": 0.06},
    "concavity_se": {"mean": 0.02, "std": 0.01, "min": 0.0, "max": 0.05},
    "concave_points_se": {"mean": 0.01, "std": 0.005, "min": 0.0, "max": 0.03},
    "symmetry_se": {"mean": 0.015, "std": 0.005, "min": 0.005, "max": 0.03},
    "fractal_dimension_se": {"mean": 0.002, "std": 0.001, "min": 0.0005, "max": 0.01},
    "radius_worst": {"mean": 13.3, "std": 2.0, "min": 7.9, "max": 20.0},
    "texture_worst": {"mean": 23.51507, "std": 5.493955, "min": 12.02, "max": 41.78},
    "perimeter_worst": {"mean": 87.005938, "std": 13.527091, "min": 50.41, "max": 127.1},
    "area_worst": {"mean": 558.89944, "std": 163.601424, "min": 185.2, "max": 1210.0},
    "smoothness_worst": {"mean": 0.124959, "std": 0.020013, "min": 0.07117, "max": 0.2006},
    "compactness_worst": {"mean": 0.182673, "std": 0.09218, "min": 0.02729, "max": 0.5849},
    "concavity_worst": {"mean": 0.166238, "std": 0.140368, "min": 0.0, "max": 1.252},
    "concave_points_worst": {"mean": 0.074444, "std": 0.035797, "min": 0.0, "max": 0.175},
    "symmetry_worst": {"mean": 0.270246, "std": 0.041745, "min": 0.1566, "max": 0.4228},
    "fractal_dimension_worst": {"mean": 0.079442, "std": 0.013804, "min": 0.05521, "max": 0.1486},
}


TOPIC = "patients"

producer = Producer({"bootstrap.servers": "kafka:9092"})

set_id = set()

REGIONS = ["North", "South", "East", "West", "Central"]

current_id = 700

def generate_one(stats, label="M"):
    """
    Генерация одной строки для продюсера в ввиде json
    """

    global current_id
    
    features = {}
    for feature, values in stats.items():
        mean, std, min_val, max_val = values["mean"], values["std"], values["min"], values["max"]
        val = np.random.normal(mean, std)
        val = np.clip(val, min_val, max_val)
        features[feature] = float(val)

    id_ = current_id
    current_id += 1

    age = np.random.randint(30, 91)
    region = np.random.choice(REGIONS)
    exam_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    row = {
        "patient": {
            "id": int(id_),
            "age": int(age),
            "region": region
        },
        "diagnosis": label,
        "date": exam_date,
        "features": features
    }
    return row


def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")


if __name__ == "__main__":
    try:
        while True:
            if np.random.choice(["M", "B"]) == "M":
                event = generate_one(M_stats, "M")
            else:
                event = generate_one(B_stats, "B")
            print("Message delivered")
            producer.produce(
                TOPIC,
                json.dumps(event).encode("utf-8"),
                callback=delivery_report
            )
            producer.poll(0)
            time.sleep(5)
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        producer.flush()






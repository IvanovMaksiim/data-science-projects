# Adaptive KNN KD-Tree Classifier

Кастомная реализация алгоритма K ближайших соседей (kNN) с адаптивным выбором количества соседей на основе плотности данных и использованием KD-дерева.

## Особенности

- KD-дерево для быстрого поиска ближайших соседей
- Адаптация `k` в зависимости от локальной плотности
- Взвешенное голосование по расстоянию
- Сравнение с `scikit-learn` `KNeighborsClassifier`
## Установка

pip install .


## Использование

from adaptive_knn_kdtree import AdaptiveKNN_KDTree
import numpy as np

X = np.random.rand(100, 2)
y = np.random.choice(['A', 'B'], 100)

model = AdaptiveKNN_KDTree(base_k=3, max_k=10)
model.fit(X, y)

X_test = np.random.rand(5, 2)
print(model.predict(X_test))

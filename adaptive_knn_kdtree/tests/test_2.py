import numpy as np
from adaptive_knn_kdtree import AdaptiveKNN_KDTree
# проверка на количество меток == количеству примеров
def test_adaptive_knn():
    X = np.random.rand(50, 2)
    y = np.random.choice([0, 1], 50)

    model = AdaptiveKNN_KDTree()
    model.fit(X, y)

    X_test = np.random.rand(3, 2)
    y_pred = model.predict(X_test)

    assert len(y_pred) == 3

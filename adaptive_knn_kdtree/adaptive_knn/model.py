import numpy as np
from .core import build_kdtree, knn
from .utils import adapt_knn


class AdaptiveKNN_KDTree:
    def __init__(self, base_k: int = 3, max_k: int = 20):
        self.base_k = base_k
        self.max_k = max_k
        self.tree = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        self.tree = build_kdtree(X, y)

    def predict(self, X_test: np.ndarray) -> np.ndarray:
        if self.tree is None:
            raise RuntimeError("Модель не обучена. Вызовите fit() перед predict().")

        predictions = []

        for x in X_test:
            neighbors = knn(self.tree, x, self.max_k)
            dists = np.array([d for d, _ in neighbors])
            labels = np.array([l for _, l in neighbors])

            all_plotn = 1 / (dists[:self.base_k] + 1e-5)
            local_plotn = np.mean(all_plotn)

            k = adapt_knn(self.base_k, local_plotn, self.max_k)
            k = min(k, len(labels))

            select_labels = labels[:k]
            select_dists = dists[:k]
            weights = 1 / (select_dists + 1e-5)

            counter = {}
            for l, w in zip(select_labels, weights):
                counter[l] = counter.get(l, 0) + w

            pred = max(counter.items(), key=lambda x: x[1])[0]
            predictions.append(pred)

        return np.array(predictions)

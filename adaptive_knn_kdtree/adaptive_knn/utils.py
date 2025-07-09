import numpy as np

def adapt_knn(base_k: int, plotn: np.floating, max_k: int) -> int:
    scaling = 1 + np.log1p(1.0 / (plotn + 1e-5))
    k = int(base_k * scaling)
    return int(np.clip(k, base_k, max_k))

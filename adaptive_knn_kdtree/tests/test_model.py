import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.neighbors import KNeighborsClassifier
from adaptive_knn_kdtree import AdaptiveKNN_KDTree
# проверка работоспособности методов .fit and .predict. Сравнение с knn kdtree sklearn по accuracy

X = np.random.rand(100, 2)
y = np.random.choice(['A', 'B'], 100)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)


model = AdaptiveKNN_KDTree(base_k=3, max_k=20)
model.fit(X_train, y_train)


y_pred_adapt = model.predict(X_test)

accuracy_custom = accuracy_score(y_test, y_pred_adapt)
print(f"Accuracy of AdaptiveKNN_KDTree: {accuracy_custom:.2f}")


knn_model = KNeighborsClassifier( algorithm='kd_tree')
knn_model.fit(X_train, y_train)


y_pred_sklearn = knn_model.predict(X_test)


accuracy_sklearn = accuracy_score(y_test, y_pred_sklearn)
print(f"Accuracy of sklearn: {accuracy_sklearn:.2f}")

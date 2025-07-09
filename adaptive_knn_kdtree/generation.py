def generate_advanced_data(n_samples=3000, n_features=20, random_state=42):


     X_dense, y_dense = make_classification(
         n_samples=int(n_samples * 0.4), n_features=n_features,
         n_redundant=0, n_informative=n_features, n_clusters_per_class=1,
         class_sep=2.5, random_state=random_state
     )
     groups_dense = np.full(len(X_dense), fill_value='dense')

     X_sparse, y_sparse = make_classification(
         n_samples=int(n_samples * 0.4), n_features=n_features,
         n_redundant=0, n_informative=n_features, n_clusters_per_class=1,
         class_sep=0.5, random_state=random_state
     )
     groups_sparse = np.full(len(X_sparse), fill_value='sparse')

     X_cross, y_cross = make_classification(
         n_samples=int(n_samples * 0.2), n_features=n_features,
         n_redundant=0, n_informative=n_features, n_clusters_per_class=2,
         class_sep=0.3, random_state=random_state
     )
     groups_cross = np.full(len(X_cross), fill_value='cross')

     X = np.vstack((X_dense, X_sparse, X_cross))
     y = np.concatenate((y_dense, y_sparse, y_cross))
     groups = np.concatenate((groups_dense, groups_sparse, groups_cross))

     return X, y, groups

def generate_advanced_data(n_samples=3000, n_features=20, random_state=42):

    np.random.seed(random_state)


    X_dense, y_dense = make_classification(
        n_samples=int(n_samples * 0.4), n_features=n_features,
        n_redundant=0, n_informative=n_features, n_clusters_per_class=1,
        class_sep=2.5, random_state=random_state
    )


    X_sparse, y_sparse = make_classification(
        n_samples=int(n_samples * 0.4), n_features=n_features,
        n_redundant=0, n_informative=n_features, n_clusters_per_class=1,
        class_sep=0.5, random_state=random_state + 1
    )


    X_cross, y_cross = make_classification(
        n_samples=int(n_samples * 0.2), n_features=n_features,
        n_redundant=0, n_informative=n_features, n_clusters_per_class=2,
        class_sep=0.3, random_state=random_state + 2
    )

    X = np.vstack((X_dense, X_sparse, X_cross))
    y = np.concatenate((y_dense, y_sparse, y_cross))

    return X, y

import numpy as np
from sklearn.model_selection import RandomizedSearchCV, GridSearchCV# Number of trees in random forest
from sklearn.ensemble import RandomForestRegressor

def evaluate(model, test_features, test_labels):
    predictions = model.predict(test_features)
    errors = abs(predictions - test_labels)
    mape = 100 * np.mean(errors / test_labels)
    accuracy = 100 - mape
    print('Model Performance')
    print('Average Error: {} degrees.'.format(np.mean(errors)))
    print('Accuracy = {}'.format(accuracy))

    return accuracy

def random_search_train(rf, train_features, train_labels, test_features, test_labels):
    n_estimators = [int(x) for x in np.linspace(start = 200, stop = 2000, num = 10)]
    # Number of features to consider at every split
    max_features = ['auto', 'sqrt']
    # Maximum number of levels in tree
    max_depth = [int(x) for x in np.linspace(10, 110, num = 11)]
    max_depth.append(None)
    # Minimum number of samples required to split a node
    min_samples_split = [2, 5, 10]
    # Minimum number of samples required at each leaf node
    min_samples_leaf = [1, 2, 4]
    # Method of selecting samples for training each tree
    bootstrap = [True, False]# Create the random grid
    random_grid = {'n_estimators': n_estimators,
                   'max_features': max_features,
                   'max_depth': max_depth,
                   'min_samples_split': min_samples_split,
                   'min_samples_leaf': min_samples_leaf,
                   'bootstrap': bootstrap}
    # Use the random grid to search for best hyperparameters

    # Random search of parameters, using 3 fold cross validation,
    # search across 100 different combinations, and use all available cores
    rf_random = RandomizedSearchCV(estimator = rf, param_distributions = random_grid, n_iter = 100, cv = 3, verbose=0, random_state=42, n_jobs = -1)
    # Fit the random search model
    rf_random.fit(train_features, train_labels)

    print(rf_random.best_params_)

    base_model = RandomForestRegressor(n_estimators=10, random_state=42)

    base_model.fit(train_features, train_labels)
    base_accuracy = evaluate(base_model, test_features, test_labels)
    best_random = rf_random.best_estimator_
    random_accuracy = evaluate(best_random, test_features, test_labels)
    print('Improvement of {}%.'.format(100 * (random_accuracy - base_accuracy) / base_accuracy))
    if random_accuracy > base_accuracy:
        return rf_random.best_params_,random_accuracy
    else:
        return base_model.get_params(),base_accuracy

def grid_search(rf, train_features, train_labels, test_features, test_labels, base_accuracy,best_params):
    # Create the parameter grid based on the results of random search
    param_grid = {
        'bootstrap': [best_params['bootstrap']],
        'max_depth': [best_params['max_depth']],
        'max_features': ['auto']+[best_params['max_features']],
        'min_samples_leaf': range(max(1,best_params['min_samples_leaf']-2),best_params['min_samples_leaf']+2,1),
        'min_samples_split': np.arange(0.05,1,0.1),
        'n_estimators': range(max(1,best_params['n_estimators']-20),best_params['n_estimators']+20,5)
    }
    # Instantiate the grid search model
    grid_search = GridSearchCV(estimator=rf, param_grid=param_grid,
                               cv=3, n_jobs=-1, verbose=0)
    grid_search.fit(train_features, train_labels)
    print(grid_search.best_params_)
    best_grid = grid_search.best_estimator_
    grid_accuracy = evaluate(best_grid, test_features, test_labels)
    print('Improvement of {}%.'.format(100 * (grid_accuracy - base_accuracy) / base_accuracy))
    if grid_accuracy > base_accuracy:
        return grid_search.best_params_, grid_accuracy
    else:
        return best_params, base_accuracy
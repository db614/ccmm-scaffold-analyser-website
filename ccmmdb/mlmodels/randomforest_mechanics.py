import numpy as np
import pandas as pd
import plotly
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error
import pickle
from ccmmdb import app
from ccmmdb.core.db import db
from ccmmdb.utils.dbterms import inverted_db_terms, total_db_terms
from ccmmdb.mlmodels.hyperparametertuning import random_search_train, grid_search

x_options = ['Collagen Concentration (%)', 'Collagen Freezing Temperature (\xb0C)',
                      'Collagen Cooling Rate (\xb0C/min)', 'Collagen Drying Temperature (\xb0C)',
                      'Collagen Drying Pressure (mTorr)', 'Crosslinking Concentration (%)',
                      'Mechanical Testing Temperature (\xb0C)', 'Construct Type', 'Additives','Collagen Source',
                      'Crosslinker', 'Collagen Hydration Solvent','Collagen Dialysis', 'Mechanical Loading Type',
                      'Hydration State at Mechanical Testing']

y_options = ['Modulus (Pa)', 'Failure Strength (Pa)', 'Failure Strain']


mechanics_regressor,mechanicsfeatimportance, mechanics_MSE, x_scaler, y_scaler = {},{},{},{},{}

for y_option in y_options:
    alloptions = x_options + [y_option]

    # load dataset
    with app.app_context():
        dataset = pd.read_sql('SELECT * FROM results WHERE deleted= 0', db.engine)
    dataset = dataset.rename(columns=total_db_terms)
    dataset = dataset[alloptions]
    #remove y options that aren't related to mechanics
    dataset.dropna(subset=[y_option], how ='all', inplace=True)
    #remove any columns that are completely identical for all measurements
    nunique = dataset.apply(pd.Series.nunique)
    cols_to_drop = nunique[nunique == 1].index
    dataset = dataset.drop(cols_to_drop, axis=1)
    dataset.fillna(np.NaN, inplace=True)
    dataset = dataset.apply(pd.to_numeric, errors = 'ignore')
    dataset.dropna(axis = 1, how = 'all', inplace=True)

    # pre-process data
    # one-hot encode categorical data
    dataset = pd.get_dummies(dataset, drop_first=True)
    #split into test and train data
    dataset_train, dataset_test = train_test_split(dataset, test_size = 0.2, random_state = 0)

    # data imputation
    imp_mean = IterativeImputer(estimator=DecisionTreeRegressor(max_features='sqrt'),missing_values=np.nan)
    dataset_train = imp_mean.fit_transform(dataset_train)
    dataset_test = imp_mean.transform(dataset_test)

    # convert the numpy arrays back into dataframes
    dataset_train = pd.DataFrame(dataset_train, columns=dataset.columns)
    dataset_test = pd.DataFrame(dataset_test, columns=dataset.columns)
    x_train = dataset_train.drop(y_option, axis=1)
    y_train = dataset_train[y_option]
    x_test = dataset_test.drop(y_option, axis=1)
    y_test = dataset_test[y_option]

    # data normalisation
    x_scaler[y_option] = MinMaxScaler()
    x_train = pd.DataFrame(x_scaler[y_option].fit_transform(x_train), columns=dataset.drop(y_option, axis=1).columns)
    x_test = pd.DataFrame(x_scaler[y_option].transform(x_test), columns=dataset.drop(y_option, axis=1).columns)

    y_scaler[y_option] = MinMaxScaler()
    y_train = y_scaler[y_option].fit_transform(y_train.values.reshape(-1, 1)).ravel()
    y_test = y_scaler[y_option].transform(y_test.values.reshape(-1, 1)).ravel()

    # define the models
    mechanics_regressor_trial = RandomForestRegressor()

    # random search train
    best_params, base_accuracy = random_search_train(mechanics_regressor_trial, x_train, y_train, x_test, y_test)

    # grid search train
    best_params_refined = grid_search(mechanics_regressor_trial, x_train, y_train, x_test, y_test, base_accuracy,
                                      best_params)

    # fit final model
    mechanics_regressor[y_option] = RandomForestRegressor(**best_params_refined[0])

    #kfold = KFold(n_splits=10, random_state=None, shuffle=True)

    mechanics_regressor[y_option].fit(x_train, y_train)
    y_predict = mechanics_regressor[y_option].predict(x_test).clip(0, 2).reshape(-1, 1)
    y_test = y_scaler[y_option].inverse_transform(y_test.reshape(-1, 1))
    y_predict = y_scaler[y_option].inverse_transform(y_predict.reshape(-1, 1))
    mechanics_MSE[y_option] = mean_squared_error(y_test, y_predict)

    col_sorted_by_importance=mechanics_regressor[y_option].feature_importances_.argsort()
    meanimportance = mechanics_regressor[y_option].feature_importances_[col_sorted_by_importance].mean()
    feat_imp=pd.DataFrame({
        'Features':x_train.columns[col_sorted_by_importance],
        'Feature Importance':mechanics_regressor[y_option].feature_importances_[col_sorted_by_importance]
    })
    mechanicsfeatimportance[y_option] = px.bar(feat_imp, x='Features', y='Feature Importance', title=y_option)
    mechanicsfeatimportance[y_option].add_shape(
            # Line Horizontal
                name="Mean Importance",
                type="line",
                x0=-.5,
                y0=meanimportance,
                x1=len(x_train.columns)-.5,
                y1=meanimportance,
                line=dict(
                    color="red",
                    width=4,
                    dash="dash",
                ))
    mechanicsfeatimportance[y_option].update_layout(title_x=0.5)
    plotly.io.write_json(mechanicsfeatimportance[y_option], '../core/dashapp/mechanics-feature-importance-'+y_option+'.json')

mechanicsmodel = '../core/dashapp/finalized_mechanics_model.sav'
mechanicsxscaler = '../core/dashapp/finalized_mechanics_xscaler.sav'
mechanicsyscaler = '../core/dashapp/finalized_mechanics_yscaler.sav'
mechanicsMSE = '../core/dashapp/finalized_mechanics_MSE.sav'
pickle.dump(mechanics_regressor, open(mechanicsmodel, 'wb'))
pickle.dump(x_scaler, open(mechanicsxscaler, 'wb'))
pickle.dump(y_scaler, open(mechanicsyscaler, 'wb'))
pickle.dump(mechanics_MSE, open(mechanicsMSE, 'wb'))
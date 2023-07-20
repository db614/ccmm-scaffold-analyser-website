import pandas as pd
import numpy as np
from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasRegressor
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold
from sklearn.preprocessing import MinMaxScaler
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn import metrics
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.tree import DecisionTreeRegressor
from sklearn.pipeline import Pipeline
from ccmmdb import app
from ccmmdb.core.db import db
from ccmmdb.utils.dbterms import inverted_db_terms
from keras.optimizers import Adam
x_options = ['Collagen Concentration (%)', 'Collagen Freezing Temperature (\xb0C)',
                  'Collagen Cooling Rate (\xb0C/min)', 'Collagen Drying Temperature (\xb0C)', 'Collagen Drying Pressure (mTorr)',
                  'Crosslinking Concentration (%)', 'Mechanical Testing Temperature (\xb0C)', 'Construct Type', 'Additives',
			 'Collagen Source', 'User ID', 'Crosslinker', 'Collagen Hydration Solvent',
                  'Collagen Dialysis', 'Mechanical Loading Type', 'Hydration State at Mechanical Testing']

y_options = ['Pore Size (\u03BCm)', 'Median Interconnection Diameter (\u03BCm)', 'Percolation Diameter (\u03BCm)', #'Porosity (%)',
                  'Modulus (Pa)', 'Failure Strength (Pa)', 'Failure Strain']

categorical_options = ['Construct Type', 'Additives', 'Collagen Source', 'User ID', 'Crosslinker', 'Collagen Hydration Solvent',
                  'Collagen Dialysis', 'Mechanical Loading Type', 'Hydration State at Mechanical Testing']

x_options = [inverted_db_terms[x] for x in x_options]
y_options = [inverted_db_terms[y] for y in y_options]
categorical_options = [inverted_db_terms[option] for option in categorical_options]
alloptions = x_options+y_options

# load dataset
with app.app_context():
	dataset = pd.read_sql('SELECT * FROM results WHERE deleted= 0', db.engine)
dataset = dataset[alloptions]
dataset.fillna(np.NaN, inplace=True)
dataset = dataset.apply(pd.to_numeric, errors = 'ignore')

# pre-process data
# one-hot encode categorical data
dataset = pd.get_dummies(dataset, drop_first=True)

# define base model
def baseline_model():
	# create model
	model = Sequential()
	model.add(Dense(32, input_dim= x_train.shape[1], kernel_initializer='normal', activation='relu'))
	model.add(Dense(32, kernel_initializer='normal', activation='relu'))
	model.add(Dense(3, activation='linear'))

	# Compile model
	model.compile(loss='mean_squared_error', optimizer=Adam(lr=0.001))
	return model

#split into test and train data
dataset_train, dataset_test = train_test_split(dataset, test_size = 0.2, random_state = 0)

# data imputation
imp_mean = IterativeImputer(estimator=DecisionTreeRegressor(max_features='sqrt'),missing_values=np.nan)
dataset_train = imp_mean.fit_transform(dataset_train)
dataset_test = imp_mean.transform(dataset_test)

# convert the numpy arrays back into dataframes
dataset_train = pd.DataFrame(dataset_train, columns=dataset.columns)
dataset_test = pd.DataFrame(dataset_test, columns=dataset.columns)
x_train = dataset_train.drop(y_options, axis=1)
y_train = dataset_train[y_options[3:6]]
x_test = dataset_test.drop(y_options, axis=1)
y_test = dataset_test[y_options[3:6]]

# data normalisation
x_scaler = MinMaxScaler()
x_train = x_scaler.fit_transform(x_train)
x_test = x_scaler.transform(x_test)

y_scaler = MinMaxScaler()
y_train = y_scaler.fit_transform(y_train)
y_test = y_scaler.transform(y_test)

regressor = KerasRegressor(build_fn=baseline_model, epochs=50, batch_size=32, verbose=2)

kfold = KFold(n_splits=10, random_state=None, shuffle=True)
#print(cross_val_score(regressor, x_train, y_train, cv=kfold, scoring='neg_mean_squared_error'))

#split into validation and train
x_train, x_val, y_train, y_val = train_test_split(x_train, y_train, test_size=0.2, random_state=0)

regressor.fit(x_train, y_train, validation_data = (x_val,y_val))
y_predict = regressor.predict(x_test).clip(0,2)
print(mean_squared_error(y_test,y_predict))
y_test = y_scaler.inverse_transform(y_test)
y_predict = y_scaler.inverse_transform(y_predict)

#print(r2_score(y_test,y_predict))
print(np.sqrt(mean_squared_error(y_test,y_predict)))

'''
# evaluate model with standardized dataset
estimators = []
estimators.append(('standardise', MinMaxScaler()))
estimators.append(('impute', IterativeImputer()))
estimators.append(('mlp', regressor))
pipeline = Pipeline(estimators)
results = cross_val_score(regressor, x_data, y_data, cv=kfold)
print("Standardized: %.2f (%.2f) MSE" % (results.mean(), results.std()))
'''
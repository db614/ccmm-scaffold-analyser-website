from dash.dependencies import Input, Output, State
import ccmmdb.utils.dbterms as dbterms
import pickle
import pandas as pd
import json
import os
import numpy as np
terms = dbterms.total_db_terms
ROOT = os.path.dirname(os.path.abspath(__file__))

structurey= ['Pore Size (\u03BCm)', 'Median Interconnection Diameter (\u03BCm)', 'Percolation Diameter (\u03BCm)']

mechanicsy= ['Modulus (Pa)', 'Failure Strength (Pa)', 'Failure Strain']

structureInputVars = {i : json.load(open(os.path.join(ROOT, 'structure-feature-importance-'+i+'.json')))['data'][0]['x'] for i in structurey}
mechanicsInputVars = {i : json.load(open(os.path.join(ROOT, 'mechanics-feature-importance-'+i+'.json')))['data'][0]['x'] for i in mechanicsy}
structure_regressor = pickle.load(
            open(os.path.join(ROOT, 'finalized_structure_model.sav'), 'rb'))
mechanics_regressor = pickle.load(
            open(os.path.join(ROOT, 'finalized_mechanics_model.sav'), 'rb'))
structure_x_scaler = pickle.load(
            open(os.path.join(ROOT, 'finalized_structure_xscaler.sav'), 'rb'))
structure_y_scaler = pickle.load(
            open(os.path.join(ROOT, 'finalized_structure_yscaler.sav'), 'rb'))
structure_MSE = pickle.load(
            open(os.path.join(ROOT, 'finalized_structure_MSE.sav'), 'rb'))
mechanics_x_scaler = pickle.load(
            open(os.path.join(ROOT, 'finalized_mechanics_xscaler.sav'), 'rb'))
mechanics_y_scaler = pickle.load(
            open(os.path.join(ROOT, 'finalized_mechanics_yscaler.sav'), 'rb'))
mechanics_MSE = pickle.load(
            open(os.path.join(ROOT, 'finalized_mechanics_MSE.sav'), 'rb'))
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

def register_callbacks(predictapp):
    @predictapp.callback(
        Output("mechanicsoutput", "children"),
        [Input("mechanicsinput_{}".format(_), "value") for _ in mechanicsInputVars[mechanicsy[0]]],
    )
    def update_mechanics_prediction(*vals):
        outputstring = ''
        for output in mechanicsy:
            inputVals = pd.DataFrame(
                {mechanicsInputVars[output][index]: vals[index] for index in range(len(mechanicsInputVars[output]))},
                index=[0])
            inputVals = mechanics_x_scaler[output].transform(inputVals)
            predictor = mechanics_regressor[output].predict(inputVals).reshape(-1, 1)
            predictor = mechanics_y_scaler[output].inverse_transform(predictor)
            error = np.array([np.sqrt(mechanics_MSE[output])]).reshape(-1, 1)
            #error = mechanics_y_scaler[output].inverse_transform(error)
            outputstring += output+': '+ f"{np.round(predictor[0][0],2):.2E}"+ ' \u00B1 '+ f"{np.round(error[0][0],2):.2E}" + '\n'
        return outputstring

    @predictapp.callback(
        Output("structureoutput", "children"),
        [Input("structureinput_{}".format(_), "value") for _ in structureInputVars[structurey[0]]],
    )
    def update_structure_prediction(*vals):
        outputstring = ''
        for output in structurey:
            inputVals = pd.DataFrame(
                {structureInputVars[output][index]: vals[index] for index in range(len(structureInputVars[output]))},
                index=[0])
            inputVals = structure_x_scaler[output].transform(inputVals)
            predictor = structure_regressor[output].predict(inputVals).reshape(-1,1)
            predictor = structure_y_scaler[output].inverse_transform(predictor)
            error = np.array([np.sqrt(structure_MSE[output])]).reshape(-1, 1)
            #error = structure_y_scaler[output].inverse_transform(error)
            outputstring += output+': '+ f"{np.round(predictor[0][0],2):.2E}"+ ' \u00B1 '+ f"{np.round(error[0][0],2):.2E}" + '\n'
        return outputstring


    predictapp.callback(
        Output("modal-featimportance-instructions", "is_open"),
        [
            Input("open-featimportance-instructions", "n_clicks"),
            Input("close-featimportance-instructions", "n_clicks"),
        ],
        [State("modal-featimportance-instructions", "is_open")],
    )(toggle_modal)

    predictapp.callback(
        Output("modal-predictor-instructions", "is_open"),
        [
            Input("open-predictor-instructions", "n_clicks"),
            Input("close-predictor-instructions", "n_clicks"),
        ],
        [State("modal-predictor-instructions", "is_open")],
    )(toggle_modal)
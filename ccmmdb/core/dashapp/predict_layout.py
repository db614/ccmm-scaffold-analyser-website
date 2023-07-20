import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import os
import plotly
import time
import json
ROOT = os.path.dirname(os.path.abspath(__file__))
structure_graph,mechanics_graph={},{}
structurey = ['Pore Size (\u03BCm)', 'Median Interconnection Diameter (\u03BCm)', 'Percolation Diameter (\u03BCm)']

mechanicsy= ['Modulus (Pa)', 'Failure Strength (Pa)', 'Failure Strain']

structureInputVars = {i : json.load(open(os.path.join(ROOT, 'structure-feature-importance-'+i+'.json')))['data'][0]['x'] for i in structurey}
mechanicsInputVars = {i : json.load(open(os.path.join(ROOT, 'mechanics-feature-importance-'+i+'.json')))['data'][0]['x'] for i in mechanicsy}
for i in structurey:
    with open(os.path.join(ROOT, 'structure-feature-importance-'+i+'.json'), "r") as myfile:
        data = myfile.read()
    structure_graph[i] = plotly.io.from_json(data)
for i in mechanicsy:
    with open(os.path.join(ROOT, 'mechanics-feature-importance-'+i+'.json'), "r") as myfile:
        data = myfile.read()
    mechanics_graph[i] = plotly.io.from_json(data)
structuretime = time.ctime(os.path.getmtime(os.path.join(ROOT,'structure-feature-importance-'+structurey[0]+'.json')))
mechanicstime = time.ctime(os.path.getmtime(os.path.join(ROOT,'mechanics-feature-importance-'+mechanicsy[0]+'.json')))
structureval = [
        dcc.Input(
            id="structureinput_{}".format(_),
            type='number',
            placeholder="Input Value:{}".format(_),
            name=format(_),
            value=0,
            style={"width":"100%"}
        )
        for _ in structureInputVars[structurey[0]]
    ]
structureinput = [val for pair in zip(structureInputVars[structurey[0]],structureval) for val in pair]

mechanicsval = [
        dcc.Input(
            id="mechanicsinput_{}".format(_),
            type='number',
            placeholder="Input Value:{}".format(_),
            name=format(_),
            value=0,
            style={"width":"100%"}
        )
        for _ in mechanicsInputVars[mechanicsy[0]]
    ]


mechanicsinput = [val for pair in zip(mechanicsInputVars[mechanicsy[0]],mechanicsval) for val in pair]


layout = \
    html.Div([
        html.Nav([
            html.A([
                html.Img(src='/static/logo.png', style={'height': '42px'}, className='d-inline-block align-top'),
                html.Span('CCMMdb', className="img")], className='navbar-brand', href='/'),
            html.Button([
                html.Span([], className='navbar-toggler-icon')
            ], className='navbar-toggler',
                **{'aria-expanded': 'false', 'aria-controls': 'navbarColor01', 'aria-label': 'Toggle navigation',
                   'data-target': '#navbarColor01', 'data-toggle': 'collapse'}, type='button'),
            html.Div([
                html.Ul([
                    html.Li([
                        html.A('Home', className='nav-link', href='/'),
                    ], className='nav-item'),
                    html.Li([
                        html.A('Submit', className='nav-link', href='/index')
                    ], className='nav-item'),
                    html.Li([
                        html.A('Graphs', className='nav-link', href='/graphapp/')
                    ], className='nav-item'),
                    html.Li([
                        html.A('Predictor', className='nav-link', href='/predictapp/')
                    ], className='nav-item active'),
                    html.Li([
                        html.A('Admin', className='nav-link', href='/admin')
                    ], className='nav-item'),
                    html.Li([
                        html.A('Privacy', className='nav-link', href='/privacy')
                    ], className='nav-item'),
                    html.Li([
                        html.A('Logout', className='nav-link', href='/logout')
                    ], className='nav-item'),
                ], className='navbar-nav mr-auto')
            ], className='collapse navbar-collapse', id='navbarColor01')
        ], className='navbar navbar-expand-lg navbar-dark bg-primary'),
        html.Div([
            html.P(),
            html.Div(
                [
                    dbc.Button("Information on prediction functionality", id="open-predictor-instructions",
                               color="primary", ),
                    dbc.Modal(
                        [
                            dbc.ModalHeader(dcc.Markdown('''    
    #### CCMMdb Random Forest Prediction Tool:''')),
                            dbc.ModalBody(dcc.Markdown('''    
    Two prediction tools are shown below:

    Structure Predictor: A random forest regression-based predictor for the pore size, percolation diameter and median interconnection diameter, based on values from the dataset with non-unique values

    Mechanics Predictor 2: A random forest regression-based predictor for the Young's modulus, failure strength and failure strain, based on values from the dataset with non-unique values
    
    Categorical variables should be entered based on the absence (0) or the presence (1) of the variable after the '_'. For example, if the solvent used is acetic acid (i.e., neither HCl nor Water, 
    then the corresponding values for Collagen Solvent_H and Collagen Solvent_W should both be 0. If the solvent used is water, then Collagen Solvent_H should be 0 while Collagen Solvent_W should be 1.
    
    Feature importance graphs for both predictors are also plotted below to identify the variables that most significantly affect the output predictions. 
    For comparison, the mean feature importance is plotted as a red vertical line. As a first estimate, the most influential features can be identified as those with importances above the mean. 
    
    To be efficient with computation time, the models are trained once every month on a cleaned version of the database at that point in time. 
    Further information on when the model shown below were last updated is provided next to each predictor. 
        ''')),
                            dbc.ModalFooter(
                                dbc.Button(
                                    "Close", id="close-predictor-instructions", className="ml-auto", color="primary",
                                )
                            ),
                        ],
                        id="modal-predictor-instructions",
                        scrollable=True,
                        centered=True,
                    ),
                    html.Hr(),]
            ),
            html.P(),
            html.Div(structureinput
    + [html.Div(id="structureoutput")], style={'padding': 10, 'whiteSpace': 'pre-wrap'}
),
            html.P(),
        html.Div(dcc.Markdown(f'''This predictor was last updated using the values in this database as of {structuretime}.''')),
        ], className='container'),

        html.Div([html.Hr(),
        html.Div(dcc.Graph(figure=structure_graph[structurey[0]]), style={'width': '75%','align':'center','margin': 'auto'}),
        html.Div(dcc.Graph(figure=structure_graph[structurey[1]]), style={'width': '75%','align':'center','margin': 'auto'}),
        html.Br(),
        html.Div(dcc.Graph(figure=structure_graph[structurey[2]]), style={'width': '75%','align':'center','margin': 'auto'}),

        html.Hr(),
        html.Div(mechanicsinput
            + [html.Div(id="mechanicsoutput")], style={'padding': 10, 'whiteSpace': 'pre-wrap'}
        ),
        html.Div(dcc.Markdown(f'''This predictor was last updated using the values in this database as of {mechanicstime}.''')),
        html.Hr(),

        html.Div(dcc.Graph(figure=mechanics_graph[mechanicsy[0]]), style={'width': '75','align':'center','margin': 'auto'}),
        html.Div(dcc.Graph(figure=mechanics_graph[mechanicsy[1]]), style={'width': '75%','align':'center','margin': 'auto'}),
        html.Div(dcc.Graph(figure=mechanics_graph[mechanicsy[2]]), style={'width': '75%','align':'center','margin': 'auto'}),

                  html.Hr(),], className='container')
    ])
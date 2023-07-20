import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table

x_axis_options = ['Collagen Concentration (%)', 'Collagen Freezing Temperature (\xb0C)',
                  'Collagen Cooling Rate (\xb0C/min)', 'Collagen Drying Temperature (\xb0C)', 'Collagen Drying Pressure (mTorr)',
                  'Crosslinking Concentration (%)', 'Pixel Size (\u03BCm)', 'Mechanical Testing Temperature (\xb0C)','Modulus (Pa)', 'Failure Strength (Pa)',
                  'Failure Strain', 'Porosity (%)', 'Pore Size (\u03BCm)', 'Internal Surface Area']

y_axis_options = ['Pore Size (\u03BCm)', 'Median Interconnection Diameter (\u03BCm)', 'Percolation Diameter (\u03BCm)', 'Porosity (%)',
                  'Internal Surface Area', 'Modulus (Pa)', 'Failure Strength (Pa)', 'Failure Strain', 'Pixel Size (\u03BCm)']
colour_options = ['Construct Type', 'Additives', 'Collagen Source', 'User ID', 'Crosslinker', 'Collagen Hydration Solvent',
                  'Collagen Dialysis', 'Mechanical Loading Type', 'Mechanical Testing Temperature (\xb0C)', 'Hydration State at Mechanical Testing']

table_options = ['User ID', 'Collagen Source',  'Construct Type','Hydration State at Mechanical Testing', 'Additives',
                 'Collagen Hydration Solvent', 'Collagen Concentration (%)','Collagen Freezing Temperature (\xb0C)',
                 'Collagen Cooling Rate (\xb0C/min)', 'Collagen Drying Temperature (\xb0C)', 'Collagen Drying Pressure (mTorr)',
                 'Crosslinker', 'Crosslinking Concentration (%)', 'Mechanical Testing Temperature (\xb0C)',
                 'Mechanical Loading Type', 'Modulus (Pa)', 'Failure Strain', 'Failure Strength (Pa)',
                 'Collagen Dialysis','Porosity (%)', 'Pore Size (\u03BCm)', 'Internal Surface Area','Pixel Size (\u03BCm)']

continuous_options = [('Raw Strain','Raw Stress (Pa)'), ('Time (s)','Thermocouple Temperature (\xb0C)')]

layout = \
    html.Div([
        dcc.Store(id='store'),
        html.Nav([
            html.A([
                html.Img(src='/static/logo.png', style={'height': '42px'}, className='d-inline-block align-top'),
                html.Span('CCMMdb', className ="img")], className='navbar-brand', href='/'),
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
                ], className='nav-item active'),
                html.Li([
                        html.A('Predictor', className='nav-link', href='/predictapp/')
                    ], className='nav-item'),
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
        dbc.Button("Information on graphing functionality", id="open-graph-instructions", color="primary",),
        dbc.Modal(
            [
                dbc.ModalHeader(dcc.Markdown('''    
    #### CCMMdb Graphical Interface:''')),
                dbc.ModalBody(dcc.Markdown('''    
    Three interactive graphs are shown below:
    
    Plot 1: A simple property-relationship graph 
    
    Plot 2: Continuous data plots of any data provided (e.g. stress-strain, time-temperature thermocouple data)
    
    Plot 3: A scatter matrix plot of key parameters in the database
    
    You can select the variables to place along the x and y axes for Plot 1. You can also select a categorical variable 
    by which the Plot 1, 2 and 3 are colour-coded. Once plotted, you can choose to zoom in and pan around the graph, and 
    view extra information by hovering your cursor over your data point of interest. You can also click on the legends 
    to deselect data points belonging to a particular category, or double click them to isolate their corresponding traces.
    You can also take a snapshot of the graphs as you view them using the toolbar at the top right of the graphs.    
    ''')),
                dbc.ModalFooter(
                    dbc.Button(
                        "Close", id="close-graph-instructions", className="ml-auto",color="primary",
                    )
                ),
            ],
            id="modal-graph-instructions",
            scrollable=True,
            centered=True,
        ),
    ]
),
        html.Div([
            html.P(),
            html.Div([
                html.Label('X axis:'),
                dcc.Dropdown(
                    id='xaxis-column',
                    options=[{'label': i, 'value': i} for i in x_axis_options],
                    value='Collagen Concentration (%)'
                ),
                dcc.RadioItems(
                    id='xaxis-type',
                    options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                    value='Linear',
                    labelStyle={'display': 'inline-block'}
                )
            ],
            style={'width': '48%', 'display': 'inline-block'}),
            html.Div([
                html.Label('Y axis:'),
                dcc.Dropdown(
                    id='yaxis-column',
                    options=[{'label': i, 'value': i} for i in y_axis_options],
                    value='Pore Size (\u03BCm)'
                ),
                dcc.RadioItems(
                    id='yaxis-type',
                    options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                    value='Linear',
                    labelStyle={'display': 'inline-block'},
                )
            ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
        ]),
        html.Div([
            html.Label('Continuous Plots:'),
            dcc.Dropdown(
                id='continuous-xaxis-column',
                options=[{'label': str(i[0]) + '-' + str(i[1]), 'value': i} for i in continuous_options],
                value=('Raw Strain','Raw Stress (Pa)')
            ),
        ],
            style={'width': '48%', 'display': 'inline-block'}),
        html.Div([
            html.Label('Colour categories:'),
            dcc.Dropdown(
                id='colour-name',
                options=[{'label': i, 'value': i} for i in colour_options],
                value='Additives'
            )
        ]),
        html.Div(dbc.Spinner(dcc.Graph(id='main-graph'),size='lg')),
        html.Hr(),
        html.Div(dbc.Spinner(dcc.Graph(id='secondary-graph'),size='lg')),
        html.Hr(),
        html.Div(dbc.Spinner(dcc.Graph(id='tertiary-graph', style={'overflowX': 'scroll', 'overflowY':'scroll', 'height':750}),size='lg')),
        html.Button('Refresh', id='refresh-button', className='btn btn-primary', n_clicks=1),
        html.P(),
        html.Hr(),
        html.Div(
            [
                dbc.Button("Information on table filtering", id="open-table-instructions", color="primary",),
                dbc.Modal(
                    [
                        dbc.ModalHeader(dcc.Markdown('''    
            #### Instructions for table filtering:''')),
                        dbc.ModalBody(dcc.Markdown('''        
        The table below accepts certain keywords to select a section of the entire dataset available to you based on 
        the criteria you choose. This graphs above will be updated accordingly to only display the data pertaining to the
        selection chosen. 
        
        The list of keywords to perform the filtering in each column are:
                
        `eq` or `=` : Equals
        
        `ne` or `!=`: Not Equals
        
        `ge` or `>=` : Greater than or equals
        
        `gt` or `>`: Greater than
        
        `le` or `<=`: Less than or equals
        
        `lt` or `<` : Less than
        
        
        ##### Example: 
        
        `ne Unknown` 
        entered in the freezing temperature column and
         `> 100` 
        entered into the pore size column selects for data where we have known information about the freezing temperature
        used, and require the pore size obtained to be greater than 1 MPa.
        ''')),
                        dbc.ModalFooter(
                            dbc.Button(
                                "Close", id="close-table-instructions", className="ml-auto", color="primary"
                            )
                        ),
                    ],
                    id="modal-table-instructions",
                    scrollable=True,
                    centered=True,
                ),
            ]
        ),
        html.P(),
        html.Div([
            dash_table.DataTable(id='dash-table',
                                 columns=[{"name": i, "id": i} for i in table_options],
                                 sort_action='native',
                                 filter_action='custom',
                                 filter_query='',
                                 fixed_rows={ 'headers': True, 'data': 0 },
                                 style_table={'overflowX': 'scroll', 'overflowY': 'scroll',  'maxHeight':'500px', 'maxWidth':'1000px'},
                                 style_cell={'padding': '10px','height': 'auto', 'minHeight':'20px',
                                            'minWidth': '50px', 'width': '150px', 'maxWidth': '500px',
                                            'whiteSpace': 'normal', 'page_size': '10',
                                        },
                                 # Removed for the moment as it breaks on filtering
                                 style_data_conditional=[
                                     {
                                         'if': {'row_index': 'odd'},
                                         'backgroundColor': 'rgb(248, 248, 248)'
                                     }],
                                 style_header={
                                     'backgroundColor': 'white',
                                     'fontWeight': 'bold'
                                 }
                                 )]),
        html.P()


    ], className='container')
])


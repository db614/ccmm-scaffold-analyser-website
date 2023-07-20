import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from dash.dependencies import Input, Output, State
import ccmmdb.utils.dbterms as dbterms
terms = dbterms.total_db_terms

def get_data():
    from ccmmdb import app
    from ccmmdb.core.db import db
    with app.app_context():
        # TODO: Later we'll keep the deleted data and add a switch for admins.
        df = pd.read_sql('SELECT * FROM results WHERE deleted= 0', db.engine)
    return df

operators = [['ge ', '>='],
             ['le ', '<='],
             ['lt ', '<'],
             ['gt ', '>'],
             ['ne ', '!='],
             ['eq ', '='],
             ['contains '],
             ['datestartswith ']]  # word operators need spaces after them in the filter string, but we don't want these later

def split_filter_part(filter_part):
    for operator_type in operators:
        for operator in operator_type:
            if operator in filter_part:
                name_part, value_part = filter_part.split(operator, 1)
                name = name_part[name_part.find('{') + 1: name_part.rfind('}')]

                value_part = value_part.strip()
                v0 = value_part[0]
                if (v0 == value_part[-1] and v0 in ("'", '"', '`')):
                    value = value_part[1: -1].replace('\\' + v0, v0)
                else:
                    try:
                        value = float(value_part)
                    except ValueError:
                        value = value_part

                # word operators need spaces after them in the filter string,
                # but we don't want these later
                return name, operator_type[0].strip(), value

    return [None] * 3
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open
def register_callbacks(graphapp):
    graphapp.callback(
        Output("modal-graph-instructions", "is_open"),
        [
            Input("open-graph-instructions", "n_clicks"),
            Input("close-graph-instructions", "n_clicks"),
        ],
        [State("modal-graph-instructions", "is_open")],
    )(toggle_modal)

    graphapp.callback(
        Output("modal-table-instructions", "is_open"),
        [
            Input("open-table-instructions", "n_clicks"),
            Input("close-table-instructions", "n_clicks"),
        ],
        [State("modal-table-instructions", "is_open")],
    )(toggle_modal)

    @graphapp.callback(
        Output('store', 'data'),
        [Input('refresh-button', 'n_clicks')])
    def update_data(n_clicks):
        '''
        Button that updates the dataframe and initialises the data for the graph/table.

        :param n_clicks:
        :return:
        '''
        data = get_data()

        return data.to_dict(orient='rows')

    @graphapp.callback(
        [Output('main-graph', 'figure'),
         Output('secondary-graph', 'figure'),
         Output('tertiary-graph', 'figure'),
         Output('dash-table', 'data')],
        [Input('xaxis-column', 'value'),
         Input('yaxis-column', 'value'),
         Input('xaxis-type', 'value'),
         Input('yaxis-type', 'value'),
         Input('continuous-xaxis-column', 'value'),
         Input('colour-name', 'value'),
         Input('dash-table', 'filter_query'),
         Input('store', 'data')])
    def multi_output(xaxis_column_name, yaxis_column_name, xaxis_type, yaxis_type, continuousoptions, colour_name, filter_query,
                     store_data):
        '''
        Function takes the selectable column types, along with the stored data from the db and any filters from the
        table. It then copies the df so that we can run any filters on a purely numerical version, while displaying the
        full unaltered df in the table. The numerical only, filtered df is used to plot the graph and to filter the
        dash table.

        :param xaxis_column_name:
        :param yaxis_column_name:
        :param colour_name:
        :param xaxis_type:
        :param yaxis_type:
        :param filter_query:
        :param store_data:
        :return:
        '''
        df = pd.DataFrame(store_data)
        # Make a copy so that when we do the to_numeric we don't mess up the original df

        dff = df.copy(deep=True)
        filtering_expressions = filter_query.split(' && ')
        for filter_part in filtering_expressions:
            attr_name, operator, filter_value = split_filter_part(filter_part)
            if filter_part:
                col_name = dbterms.inverted_db_terms[attr_name]
                # legend for operators
                if operator in ('eq', 'ne') and isinstance(filter_value, str):
                    dff = dff.loc[getattr(dff[col_name].str.casefold(), operator)(filter_value.casefold())]
                elif operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
                    # these operators match pandas series operator method names
                    dff = dff.loc[getattr(dff[col_name].astype('float'), operator)(filter_value)]
                elif operator == 'contains':
                    dff = dff.loc[(dff[col_name].str.casefold()).str.contains(str(filter_value).casefold(), na=False)]
                elif operator == 'datestartswith':
                    # this is a simplification of the front-end filtering logic,
                    # only works with complete fields in standard format
                    dff = dff.loc[(dff[col_name].str.casefold()).str.startswith(str(filter_value).casefold())]
        # Get the Boolean in the df from the database id column if it matches one remaining in the filtered dff
        column_index_bool = df.isin({'id': dff['id']})
        # Return a list of the index column that was True in the Boolean above
        dataframe_bool_list = df.index[column_index_bool['id']].tolist()
        # Calculate the final df that contains non-numeric data for display in the DashTable
        df.fillna('Unknown', inplace=True)
        df = df.loc[dataframe_bool_list]
        data = df.rename(columns=terms)
        data = data.to_dict(orient="rows")  # DashTable data output
        df.apply(pd.to_numeric, errors='coerce')
        if len(df):
            figure = px.scatter(df, x=dbterms.inverted_db_terms[xaxis_column_name],
                                y=dbterms.inverted_db_terms[yaxis_column_name],
                                error_y='pore_sd' if yaxis_column_name == 'Pore Size (\u03BCm)' else None,
                                color=dbterms.inverted_db_terms[colour_name],
                                log_x=True if xaxis_type == 'Linear' else False,
                                log_y=True if yaxis_type == 'Linear' else False,
                                hover_name=dbterms.inverted_db_terms[colour_name], hover_data=['user_id'],
                                labels = dbterms.total_db_terms)
            figure.update_layout(
                xaxis={
                    'title': xaxis_column_name,
                    'type': 'linear' if xaxis_type == 'Linear' else 'log'
                },
                yaxis={
                    'title': yaxis_column_name,
                    'type': 'linear' if xaxis_type == 'Linear' else 'log'
                },
                hovermode='closest',  title = 'Property Relationships', title_x = 0.5)
            figure2 = go.Figure()
            category = []
            uniquevals = df[dbterms.inverted_db_terms[colour_name]].unique()
            mapped_colours = {uniquevals[i]  : px.colors.qualitative.Plotly[i] for i in range(len(uniquevals))}

            for index,row in df.iterrows():
                x_data = dbterms.inverted_db_terms[continuousoptions[0]]
                y_data = dbterms.inverted_db_terms[continuousoptions[1]]
                if row[x_data] != 'Unknown' or row[y_data] != 'Unknown':
                     x_vals =  np.fromstring(row[x_data], dtype=np.float, sep=',')
                     y_vals = np.fromstring(row[y_data], dtype=np.float, sep=',')
                     tracelabel = row[dbterms.inverted_db_terms[colour_name]]
                     if tracelabel in category:
                         visibility = False
                     else:
                         visibility = True
                         category.append(tracelabel)
                     figure2.add_trace(go.Scatter(x=x_vals,y=y_vals, legendgroup = tracelabel, name = tracelabel,
                                                  mode = 'lines+markers', marker = dict(color = mapped_colours[tracelabel]),
                                                  showlegend = visibility))
            figure2.update_layout(
                xaxis={
                    'title': continuousoptions[0],
                    'type': 'linear' if xaxis_type == 'Linear' else 'log'
                },
                yaxis={
                    'title': continuousoptions[1],
                    'type': 'linear' if yaxis_type == 'Linear' else 'log'
                },
                hovermode='closest', title = 'Raw Continuous Data Curves', title_x = 0.5)

            matrix_options = ['Collagen Concentration (%)', 'Collagen Dialysis',
             'Collagen Freezing Temperature (\xb0C)',
             'Collagen Cooling Rate (\xb0C/min)', 'Collagen Drying Temperature (\xb0C)', 'Collagen Drying Pressure (mTorr)',
             'Pore Size (\u03BCm)']
            figure3 = px.scatter_matrix(df, dimensions= [dbterms.inverted_db_terms[term] for term in matrix_options], color=dbterms.inverted_db_terms[colour_name],
                                       labels = dbterms.total_db_terms)
            figure3.update_traces(showupperhalf = False)
            figure3.update_layout(height = 1750, width = 1750,
                hovermode='closest', title = 'Scatter Matrix Plots', title_x = 0.25)
        else:
            figure = {
                        "layout": {
                            "height":150,
                            "xaxis": {
                                "visible": False
                            },
                            "yaxis": {
                                "visible": False
                            },
                            "annotations": [
                                {
                                    "text": "No (matching) data found to plot!",
                                    "xref": "paper",
                                    "yref": "paper",
                                    "showarrow": False,
                                    "font": {
                                        "size": 28
                                    }
                                }
                            ]
                        }
                    }
            figure2 = {
                        "layout": {
                        "height": 150,
                        "xaxis": {
                            "visible": False
                        },
                        "yaxis": {
                            "visible": False
                        },
                        "annotations": [
                            {
                                "text": "No (matching) data found to plot",
                                "xref": "paper",
                                "yref": "paper",
                                "showarrow": False,
                                "font": {
                                    "size": 28
                                }
                            }
                        ]
                    }
                }
            figure3 = {
                        "layout": {
                            "height": 150,
                            "xaxis": {
                                "visible": False
                            },
                            "yaxis": {
                                "visible": False
                            },
                            "annotations": [
                                {
                                    "text": "No (matching) data found to plot",
                                    "xref": "paper",
                                    "yref": "paper",
                                    "showarrow": False,
                                    "font": {
                                        "size": 28
                                    }
                                }
                            ]
                        }
                    }
        return figure, figure2, figure3, data

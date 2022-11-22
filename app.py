
#####################################################################################
#### Import Required packages
#####################################################################################

### import supporting packages
import os
import json

### Dash dependencies
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

import dash_bootstrap_components as dbc

### import functions from scripts
from processing import process_data, return_books
from plotly_visuals import ret_viz
from plotly_visuals import  viz_template
from plotly_visuals import  ret_timeline

#####################################################################################

#####################################################################################
#### Initialize Dash app
#####################################################################################

app = Dash(__name__,
    title="Good Reads",
    external_stylesheets=[dbc.themes.SOLAR]
)

#####################################################################################
#### Load data
#####################################################################################

WORK_DIR=os.getcwd()
ROOT_DIR=os.path.dirname(WORK_DIR)
DATA_DIR=os.path.join(WORK_DIR,"data")
DATA_FILE=os.path.join(DATA_DIR,"goodreads_dataset.csv")
df, df_awardsByYear=process_data(DATA_FILE)

#####################################################################################
#### Data Sturctures
#####################################################################################

### values to show data by
list_agg_columns=[
    'Author',
    'Book Series',
    'Book Title']
dict_agg_columns={
    'Author':'author',
    'Book Series':'series',
    'Book Title':'title'}

### values to sort data by
list_sort_columns=[
    'Number of awards',
    'Number of books',
    'Average rating',
    'Number of ratings']
dict_sort_columns={
    'Number of awards':'award_count',
    'Number of books':'book_count',
    'Average rating':'avg_rating',
    'Number of ratings':'no_ratings'}

### values to filter top N books
list_n_rows=['10 books','50 books','100 books']
dict_n_rows={'10 books':10,'50 books':50,'100 books':100}

#####################################################################################
#### Code for controls and filters
#####################################################################################

dropdown_agg=dcc.Dropdown(
                id='groupby-column',
                options=[{'label': i, 'value': i} for i in list_agg_columns],
                value='Book Series'
            )
dropdown_sort=dcc.Dropdown(
                id='sort-column',
                options=[{'label': i, 'value': i} for i in list_sort_columns],
                value='Number of awards'
            )
dropdown_sel=dcc.Dropdown(
                id='sel-rows',
                options=[{'label': i, 'value': i} for i in list_n_rows],
                value='10 books'
            )


#####################################################################################
#### Dash Application Layout
#####################################################################################

app.layout=dbc.Container([
    dbc.Row([
        dbc.Container([
            dbc.Row([

            ],style={'height':'5px'}),
            dbc.Row([
                dbc.Col([
                    html.Div(
                        "",id="appHeader"
                    ),
                    html.H2(children='Good Reads')
                ],width=12,className="glass-back", style={'width': '1320px'})

            ]),
            dbc.Row([

            ],style={'height':'10px'}),
            dbc.Row([

                    dbc.Col([
                            dbc.Row([
                                html.H6("Show data by: ")
                            ]),
                            dbc.Row([
                                    dropdown_agg
                            ]),
                            dbc.Row([

                            ],style={'height':'15px'}),
                            dbc.Row([
                                    html.H6("Sort data by: ")
                            ]),
                            dbc.Row([
                                    dropdown_sort
                            ]),
                            dbc.Row([

                            ],style={'height':'15px'}),
                            dbc.Row([
                                    html.H6("Show Top N: ")

                            ]),
                            dbc.Row([                            
                                dropdown_sel
                            ])
                    ],width=4,style={'width':'300px'},className="glass-back"),

                dbc.Col([

                ],width=1,style={'width':'10px'}),
                dbc.Col([
                    dbc.Row([
                        dbc.Col([html.Div(id="book-title")],width=11),
                        dbc.Col([
                            dbc.Button(
                                " ", id="clear-button", className="me-2",color="secondary", n_clicks=0
                            ),
                            html.Span(id="clear-output", style={"verticalAlign": "middle"})
                        ],width=1)
                    ],style={'height':'15px'}),
                    dbc.Row([
                                html.Pre(id='hover-plot',style={'color':'white'})
                    ])


                ],width=6,style={'width':'998px'},className="glass-back")

            ],style={'width':'1400px','height':'260px'}),
            dbc.Row([

            ],style={'height':'15px'})
        ],style={'width': '100%'})
    ],className="container-top"),
    dbc.Row([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='book-graph', style={'width': '100%'})
                ],width=12,className="glass-backdark")

            ])
        ],style={'width': '100%'})
    ],className="container-page")
],className="main-container")

#####################################################################################
#### Application Call back functions
#####################################################################################

@app.callback(
    Output('book-graph', 'figure'),
    Input('groupby-column', 'value'),
    Input('sort-column', 'value'),
    Input('sel-rows','value'))
def update_graph(groupby_column, sort_column,sel_rows):
    n_rows=dict_n_rows.get(sel_rows)
    show_by=dict_agg_columns.get(groupby_column)
    sort_by=dict_sort_columns.get(sort_column)

    fig = ret_viz(show_by,sort_by,df,df_awardsByYear,viz_template(),n_rows)

    return fig

@app.callback(
    Output('book-title','children'),
    Output('hover-plot', 'children'), 
    Output('clear-button', 'n_clicks'), 
    [Input("clear-button", "n_clicks"),
    Input('book-graph', 'clickData')])
def on_button_click(n,clickData):
    if n>0:
        clickData=None
    if clickData is not None:
        retText=clickData.get("points")[0].get("text")
        htmlString, param_list=return_books(retText)
        retText=ret_timeline(df,df_awardsByYear,viz_template(),param_list)
    else:
        retText=""
        htmlString=""
    return htmlString,retText, 0

#####################################################################################
#### Start Dash Application
#####################################################################################

if __name__ == '__main__':
    app.run_server(debug=False)
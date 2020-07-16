
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from data_source import *


app = dash.Dash(external_stylesheets=[dbc.themes.JOURNAL])

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "background-color": "#F2EFE4",
    "margin-right": "1rem",
    "border-color": "#73726B",
    "border-radius": '0'
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "0",
    "margin-right": "1rem"
}


metric = 'nef_auc'
split = 'rand'
selector = 'LR'
fig = line_plot_metrics(split, selector, metric)

controls = dbc.Card(
    [
        dbc.FormGroup(
            [
                dbc.Label("Train-Test split method:", className='font-weight-bold'),
                dbc.RadioItems(
                    id="split-value",
                    options=[
                        {'label': value, 'value': key} for key, value in split_names.items()
                    ],
                    value='rand',
                ),
            ],
        ),
        dbc.FormGroup(
            [
                dbc.Label("Conformational Selection method:", className='font-weight-bold'),
                dbc.RadioItems(
                    id="selector-value",
                    options=[
                        {'label': value, 'value': key} for key, value in selector_names.items()
                    ],
                    value='rand',
                ),
            ],
        ),
        dbc.FormGroup(
            [
                dbc.Label("Evaluation Metric:", className='font-weight-bold'),
                dcc.Dropdown(
                    id="metric-value",
                    options=[
                        {'label': value, 'value': key} for key, value in metric_names.items()
                    ],
                    value="roc_auc",
                ),
            ]
        )
    ],
    body=True,
    style=SIDEBAR_STYLE
)

line_plot = [
        html.H5('Título', className='text-center'),
        dcc.Graph(
                id='basic-interactions',
                figure=fig,
                config=plotly_conf
            )
    ]


app.layout = dbc.Container(
    [
        html.H1("CDK2 & FXa Results"),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(controls, md=3),
                dbc.Col(line_plot, md=9),
            ],
            align="center",
            style=CONTENT_STYLE
        ),
    ],
    fluid=True,
)


if __name__ == '__main__':
    app.run_server(debug=True)
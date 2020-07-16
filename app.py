
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
        html.H4('Input values:'),
        html.Hr(),
        dbc.FormGroup(
            [
                dbc.Label("Train-Test split method:", className='font-weight-bold'),
                dbc.RadioItems(
                    id="split-value",
                    options=[
                        {'label': value, 'value': key} for key, value in split_names.items()
                    ],
                    value='rand',
                    labelCheckedStyle={"color": "red"},
                ),
            ],
        ),
        html.Hr(),
        dbc.FormGroup(
            [
                dbc.Label("Conformational Selection method:", className='font-weight-bold'),
                dbc.RadioItems(
                    id="selector-value",
                    options=[
                        {'label': value, 'value': key} for key, value in selector_names.items()
                    ],
                    value='rand',
                    labelCheckedStyle={"color": "red"},
                ),
            ],
        ),
        html.Hr(),
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
        html.H5(id='plot-title', className='text-center'),
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
        html.Br(),
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

# Callbacks
@app.callback(
    Output(component_id='plot-title', component_property='children'),
    [
        Input("split-value", "value"),
        Input("selector-value", "value"),
        Input("metric-value", "value"),
    ]
)
def render_title(split, selector, metric):
    split_name = split_names[split]
    selector_name = selector_names[selector]
    metric_name = metric_names[metric]
    #title = f"<span class='font-weight-light'>Metric</span> {metric_name} - {split_name} Splitting - {selector_name} Selection"
    title = html.P(children=[
        html.Span('Metric ', className='font-weight-light font-italic'),
        html.Span(metric_name),
        html.Span(' - '),
        html.Span(split_name),
        html.Span(' Splitting', className='font-weight-light font-italic'),
        html.Span(' - '),
        html.Span(selector_name),
        html.Span(' Selection', className='font-weight-light font-italic'),
    ])
    return title


if __name__ == '__main__':
    app.run_server(debug=True)
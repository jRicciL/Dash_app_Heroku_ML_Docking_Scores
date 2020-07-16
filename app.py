
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from data_source import *


app = dash.Dash(external_stylesheets=[dbc.themes.JOURNAL])
app.title = 'JRL: Thesis'

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "background-color": "#444444",
    "margin-right": "1rem",
    "border-color": "#555555",
    "border-radius": '5',
    "color": "white"
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "0",
    "margin-right": "1rem"
}

FOOTER_STYLE = {
    "position": "absolute",
    "bottom": "0",
    "height": "100px"
}


controls = dbc.Card(
    [
        html.H4('Input values:', style={'color': '#FAB06E'}),
        html.Hr(style={'background-color': '#888888'}),
#        dbc.ButtonGroup(
#            [dbc.Button("CDK2"),
#             dbc.Button("FXa")]
#        ),
        dbc.FormGroup(
            [
                dbc.Label("Select a protein:", className='font-weight-bold'),
                dbc.RadioItems(
                    id="protein-value",
                    options=[
                        {'label': 'CDK2', 'value': 'CDK2'},
                        {'label': 'FXa', 'value': 'FXa'}
                    ],
                    value='CDK2',
                    labelCheckedStyle={"color": "#FF9191"},
                ),
            ],
        ),
        html.Hr(style={'background-color': '#666666'}),
        dbc.FormGroup(
            [
                dbc.Label("Train-Test split method:", className='font-weight-bold'),
                dbc.RadioItems(
                    id="split-value",
                    options=[
                        {'label': value, 'value': key} for key, value in split_names.items()
                    ],
                    value='rand',
                    labelCheckedStyle={"color": "#FF9191"},
                ),
            ],
        ),
        html.Hr(style={'background-color': '#666666'}),
        dbc.FormGroup(
            [
                dbc.Label("Conformational Selection method:", className='font-weight-bold'),
                dbc.RadioItems(
                    id="selector-value",
                    options=[
                        {'label': value, 'value': key} for key, value in selector_names.items()
                    ],
                    value='rand',
                    labelCheckedStyle={"color": "#FF9191"},
                ),
            ],
        ),
        html.Hr(style={'background-color': '#666666'}),
        dbc.FormGroup(
            [
                dbc.Label("Evaluation Metric:", className='font-weight-bold'),
                dcc.Dropdown(
                    id="metric-value",
                    options=[
                        {'label': value, 'value': key} for key, value in metric_names.items()
                    ],
                    value="roc_auc",
                    style = {"color": "#222222"}
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
                id='line-plot',
                #figure=fig,
                config=plotly_conf
            )
    ]

#***********
# APP LAYOUT
#***********
app.layout = dbc.Container(
    [
        html.Hr(),
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
        html.Footer([
            html.A('Ricci-López',
            href='https://github.com/jRicciL',
            target='_blank')
            ], 
        className='page-footer font-small blue',
        style=FOOTER_STYLE)
    ],
    fluid=True,
)

# Callbacks

# Title updater
@app.callback(
    Output(component_id='plot-title', component_property='children'),
    [
        Input("split-value", "value"),
        Input("selector-value", "value"),
        Input("metric-value", "value"),
        Input("protein-value", "value")
    ]
)
def render_title(split, selector, metric, protein_name):
    split_name = split_names[split]
    selector_name = selector_names[selector]
    metric_name = metric_names[metric]
    #title = f"<span class='font-weight-light'>Metric</span> {metric_name} - {split_name} Splitting - {selector_name} Selection"
    title = html.P(children=[
        html.Span(f"{protein_name}: ", className='font-weight-bold h3'),
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


# Line Plot Render
@app.callback(
    Output(component_id='line-plot', component_property='figure'),
    [
        Input("split-value", "value"),
        Input("selector-value", "value"),
        Input("metric-value", "value"),
        Input("protein-value", "value")
    ]
)
def render_plot(split, selector, metric, protein_name):
    fig = line_plot_metrics(split, selector, metric, protein_name)
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
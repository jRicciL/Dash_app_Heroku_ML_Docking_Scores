
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from data_source import *


app = dash.Dash(external_stylesheets=[dbc.themes.SANDSTONE])

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}


metric = 'nef_auc'
split = 'rand'
selector = 'LR'
fig = line_plot_metrics(split, selector, metric)

sidebar = html.Div([
        html.H2("Sidebar", className="display-4"),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(
    [
        dcc.Graph(
            id='basic-interactions',
            figure=fig,
            config=plotly_conf
        ),
    ],
    id="page-content",
    style=CONTENT_STYLE,
)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])



if __name__ == '__main__':
    app.run_server(debug=True)
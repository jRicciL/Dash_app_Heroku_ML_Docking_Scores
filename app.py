
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
from data_source import *


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.JOURNAL])
app.title = 'JRL: ML-Dk Scores'

server = app.server

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
    "position": "fixed",
    "bottom": "0",
    "height": "30px",
    "width": "100%",
    "background-color": "white"
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
        ),
        html.Hr(style={'background-color': '#666666'}),
        dbc.FormGroup(
            [
                dbc.Label("Violin plot:", className='font-weight-bold'),
                dbc.Checklist(
                    id="show-benchmarks",
                    options=[
                        {'label': 'Show benchmark sets', 'value': True}
                    ],
                    value=[],
                    switch=True,
                    labelCheckedStyle={"color": "#FFE1A6"},
                    style = {"color": "#fff"}
                ),
            ]
        ),
        html.Hr(style={'background-color': '#666666'}),
        dbc.FormGroup(
            [
                dbc.Label("Dimensionality Reduction (DR) method:", className='font-weight-bold'),
                dbc.RadioItems(
                    id="dr-method-value",
                    options=[
                        {'label': value, 'value': key} for key, value in dr_methods_names.items()
                    ],
                    value='mds',
                    labelCheckedStyle={"color": "#F5D5AB"},
                    inline=True
                ),
                html.Br(),
                dbc.Label("Protein atoms/region used for DR:", className='font-weight-bold'),
                dbc.RadioItems(
                    id="prot-section-value",
                    options=[
                        {'label': value, 'value': key} for key, value in prot_section_dr.items()
                    ],
                    value='sec',
                    labelCheckedStyle={"color": "#F5D5AB"}
                ),
                html.Br(),
                dbc.Label("Point's size by:", className='font-weight-bold'),
                dbc.RadioItems(
                    id="point-size-by",
                    options=[
                        {'label': value, 'value': key} for key, value in point_size_by.items()
                    ],
                    value='Pocket Volume (Pkt)',
                    labelCheckedStyle={"color": "#F5D5AB"}
                ),
            ],
        ),
        
    ],
    body=True,
    className="d-flex align-self-stretch",
    style=SIDEBAR_STYLE
)


# *****
# PLOTS
# *****
line_plot = [
        html.H5(id='plot-title', className='text-center'),
        dcc.Graph(
                id='line-plot',
                #figure=fig,
                config=plotly_conf
            )
    ]

# SLIDER
max_value = 402
marks = { i: str(i) for i in range(max_value) if i%10 == 0}
n_confs_slider = html.Div(
    id='slider-div',
    children=[
        dcc.Slider(
            id='n-confs-slider',
            min=1,
            max=max_value,
            step=1,
            value=50,
            marks=marks
        )   
    ],
    className='ml-5 pl-2 pr-1')

scatter_plot = [
    html.H5(id='mds-title', className='text-center'),
     dcc.Graph(
        id='scatter-plot',
        config=plotly_conf
    )
]

violin_plot = [
    html.H5(id='violin-title', className='text-center'),
    dcc.Graph(
        id='violin-plot',
        config=plotly_conf
    )
]

# Plot Sections
plot_section = [
    dbc.Row([
        dbc.Col(line_plot, md=12, className='mb-2'),
        dbc.Col(n_confs_slider, md=12, className='mb-5'),
        dbc.Col(violin_plot, md=7),
        dbc.Col(scatter_plot, md=5),
       ],
    className='mb-5'
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
                dbc.Col(controls, md=3, className='mb-5'),
                dbc.Col(plot_section, md=9),
            ],
            align="center",
            style=CONTENT_STYLE
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.H4('Table of Protein Conformations',
                        className='text-center', style={'color': 'black'}),
                    md=12, className='mt-5'
                ),
                dbc.Col(id='div-mtd-table',
                    md=12, className='mb-5 p-3'),
            ],
            align="center",
            style=CONTENT_STYLE
        ),
        html.Footer([
            html.A('@Ricci-López',
            href='https://github.com/jRicciL',
            target='_blank')
            ], 
        className='page-footer font-small blue',
        style=FOOTER_STYLE)
    ],
    fluid=True,
)

# Callbacks




# Slider callback
@app.callback(
    [
        Output(component_id='n-confs-slider', component_property='max'),
        Output(component_id='n-confs-slider', component_property='marks'),
    ],
    [
        Input("protein-value", "value"),
    ],
    [
        State('n-confs-slider', 'max'),
        State('n-confs-slider', 'marks'),
    ]
)
def set_slider(protein_name, max, marks):
    if protein_name == 'CDK2':
        max_value = 402
    elif protein_name == 'FXa':
        max_value = 136 

    marks = { i: str(i) for i in range(1, max_value) if i%10 == 0 or i == 1}

    return max_value, marks

# Title updater
@app.callback(
    [
        Output(component_id='plot-title', component_property='children'),
        Output(component_id='violin-title', component_property='children'),
        Output(component_id='mds-title', component_property='children'),
    ],
    [
        Input("split-value", "value"),
        Input("selector-value", "value"),
        Input("metric-value", "value"),
        Input("protein-value", "value"),
        Input("dr-method-value", "value"),
        Input("prot-section-value", "value"),
    ]
)
def render_title(split, selector, metric, protein_name, dr_method, protein_section):
    split_name = split_names[split]
    selector_name = selector_names[selector]
    metric_name = metric_names[metric]
    if protein_section == 'vol_pkt':
        dr_method = 'mds'
    dr_method_name = dr_methods_names[dr_method]
    prot_section = prot_section_dr[protein_section]

    #title = f"<span class='font-weight-light'>Metric</span> {metric_name} - {split_name} Splitting - {selector_name} Selection"
    line_title = html.P(children=[
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

    violin_title = html.P(children=[
        html.Span(f"Violin plot: ", className='font-weight-bold'),
        html.Span(f'{metric_name} score'),
        html.Span(' using ', className='font-weight-light'),
        html.Span('Docking Raw Scores', className='font-weight-light font-italic'),
    ])

    mds_title = html.P(children=[
        html.Span(f"{dr_method_name}", className='font-weight-bold'),
        html.Span(f' over Protein Conformations '),
        html.Span(f'({prot_section})', className='font-weight-light font-italic h6'),
    ]) 
    return line_title, violin_title, mds_title


# Plot Renders
@app.callback(
    [
        Output(component_id='line-plot', component_property='figure'),
        Output(component_id='violin-plot', component_property='figure'),
        Output(component_id='scatter-plot', component_property='figure'),
        Output(component_id='div-mtd-table', component_property='children')
    ],
    [
        Input("split-value", "value"),
        Input("selector-value", "value"),
        Input("metric-value", "value"),
        Input("protein-value", "value"),
        Input("show-benchmarks", "value"),
        Input("dr-method-value", "value"),
        Input("prot-section-value", "value"),
        Input("point-size-by", "value"),
        Input("n-confs-slider", "value"),
    ]
)
def render_plot(split, selector, metric, 
    protein_name, show_benchmarks, dr_method, 
    prot_section, point_size_by, n_confs):

    preselected_confs = get_preselected_confs(split, selector, n_confs, protein_name)

    line_plot = line_plot_metrics(split, selector, metric, protein_name, n_confs)

    violin_plot = violin_plot_metrics(metric, protein_name, show_benchmarks, preselected_confs)

    scatter_plot = mds_plot(protein_name, dr_method, prot_section, point_size_by, preselected_confs)
    
    mtd_table = render_mtd_table(protein_name, preselected_confs)
    
    return line_plot, violin_plot, scatter_plot, mtd_table

if __name__ == '__main__':
    app.run_server(debug=True)
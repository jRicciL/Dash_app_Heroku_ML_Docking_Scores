import plotly.graph_objects as go
import pandas as pd
import numpy as np
import pickle

# Read the pickle file
data_file_fxa = './FXA_dash_app_results.obj'
with open(data_file_fxa, 'rb') as f:
    FXA_DATA = pickle.load(f)

data_file_cdk2 = './CDK2_dash_app_results.obj'
with open(data_file_cdk2, 'rb') as f:
    CDK2_DATA = pickle.load(f)

# Assing values
ALL_RESULTS_FXa = FXA_DATA['dict_ML_RESULTS']
ALL_RESULTS_CDK2 = CDK2_DATA['dict_ML_RESULTS']

# Mol libraries info
fxa_mols = dict(num_mols=6233, num_actives=300)
cdk2_mols = dict(num_mols=3466, num_actives=415)
mos_info = {'CDK2': cdk2_mols,
            'FXa': fxa_mols}

# Parse the data from the dictionary
def get_data(protein_name, key):
    if protein_name == 'FXa':
        data = FXA_DATA[key]
    elif protein_name == 'CDK2':
        data = CDK2_DATA[key]
    return data 

# plotly configurations
mode_bar_buttons = ["toImage", "autoScale2d",
                    "toggleSpikelines", "hoverCompareCartesian", 
                    "hoverClosestCartesian"]
plotly_conf = dict(
    displaylogo=False,
    displayModeBar=True,
    scrollZoom= True,
    modeBarButtonsToRemove=mode_bar_buttons
)

# Data Dictionaries
cols_lines = {'LogReg'  : 'rgb(134, 102, 183)',
              'rbfSVC'  : 'rgb(229, 156, 48)',
              'XGB_tree': 'rgb(9, 153, 149)',
              '1NN'     : 'rgb(230, 73, 79)'}

cols_fill = {'LogReg'   : 'rgba(134, 102, 183, 0.25)',
             'rbfSVC'   : 'rgba(216, 143, 48, 0.25)',
             'XGB_tree' : 'rgba(9, 153, 149, 0.25)',
             '1NN'      : 'rgba(230, 73, 79, 0.25)'}

# Dictionary names
split_names = {'rand': 'Random',
               'scff': 'Scaffold'}

selector_names = {'rand' : 'Random',
                  'LR'   : 'RFE (Log. Reg.)',
                  'RF'   : 'RFE (Rand. Forest)',
                  'XGB'  : 'RFE (Grad. Boosting)'}

clf_names_dict = {'LogReg'  : 'Log. Regression',
                  'rbfSVC'  : 'RBF SVM',
                  'XGB_tree': 'Gradient Boosting',
                  '1NN'     : '1-NN Classifier'}

metric_names = {'roc_auc'   : 'ROC-AUC',
                'nef_auc'   : 'NEF-AUC',
                'pr_auc'    : 'Pr & Rcll-AUC',
                'bedroc_20' : 'BEDROC (a=20)',
                'bedroc_10' : 'BEDROC (a=10)',
                'bedroc_2'  : 'BEDROC (a=2)',
                'bedroc_0.5': 'BEDROC (a=0.5)',
                'ef_0.2'    : 'EF (chi=20.0%)',
                'ef_0.02'   : 'EF (chi=2.0%)',
                'ef_0.005'  : 'EF (chi=0.5%)',
                'ef_0.001'  : 'EF (chi=0.1%)',
               }

def get_y_axis_params(metric):
    if (metric == 'roc_auc'):
        y_axis_params = dict(range=[0.4, 1], tick0=0.00, dtick=0.05)
    elif (metric == 'nef_auc'):
        y_axis_params = dict(range=[0.2, 1], tick0=0.00, dtick=0.05)
    elif 'ef_' in metric:
        y_axis_params = dict()
    else:
        y_axis_params = dict(range=[0.0, 1], tick0=0.00, dtick=0.1)
    return y_axis_params


# VIOLIN PLOT FUNCTION
def violin_plot(metric, protein_name):
    
    df_DKSC_METRICS = get_data(protein_name, 'df_DKSC_METRICS')
    W = df_DKSC_METRICS.filter(regex=metric)
    
    y_axis_params = get_y_axis_params(metric)

    fig = go.Figure()

    for column in W:
        fig.add_trace(
            go.Violin(
                y = W[column],
                name = column.split()[0].upper(),
                jitter = 1, points = 'all', side = 'positive',
                box_visible = True,
                # selectedpoints = selected_points,
                marker = dict(
                    size = 5
                )
            )
        )
    
    return fig



# LINE PLOT FUNCTION
def line_plot_metrics(split, selector, metric, protein_name):
    query = f"split == '{split}' & selector == '{selector}' & metric == '{metric}'"

    #X_dksc, X = get_data(protein_name)

    dict_ML_RESULTS = get_data(protein_name, 'dict_ML_RESULTS')
    X_dksc = dict_ML_RESULTS['X_dksc']
    X = dict_ML_RESULTS['X_ml']

    # Mols info
    libs = mos_info[protein_name]
    n_mols = libs['num_mols']
    n_actives = libs['num_actives']

    # Ref score
    best_ref = X_dksc.query(query).max()['best_dksc']
    median_ref = X_dksc.query(query).median()['median_dksc']

    # Results
    X_subset = X.query(query)
    X_subset = X_subset.reset_index().drop(['split', 'selector',  'metric', 0], axis=1)
    X_subset = X_subset.set_index(['desc', 'classifier']).T
    X_mean = X_subset.loc[:, 'mean']
    X_std = X_subset.loc[:, 'std']

    # Número de conformaciones
    n_confs = X_mean.shape[0]

    y_axis_params = get_y_axis_params(metric)

    traces = []
    for col in X_mean.columns:
        # Create the upper and lower bounds
        upper = X_mean[col] + X_std[col]
        lower = X_mean[col] - X_std[col]

        upper = go.Scatter(x=X_mean.index, 
                           y=X_mean[col] + X_std[col],
                           mode='lines',
                           name=clf_names_dict[col], 
                           legendgroup=clf_names_dict[col], 
                           showlegend=False,
                           line=dict(width=0),
                           fillcolor=cols_fill[col],
                           hoverinfo='skip',
                           fill='tonexty')

        line = go.Scatter(x=X_mean.index, 
                           y=X_mean[col],
                           mode='lines',
                           name=clf_names_dict[col],
                           hovertemplate = 
                           f'<b style="color: {cols_lines[col]}">{clf_names_dict[col]}</b>' +
                           '<br>' +
                           '<b><i>k</i> confs:</b> %{x}' +
                           '<br>' +
                           f'<b><i>{metric_names[metric]}</i>:</b> ' + 
                           '%{y:.2f}' +
                           '<extra></extra>',
                           legendgroup=clf_names_dict[col], 
                           line=dict(width=2.5,
                                     color=cols_lines[col]),
                           fillcolor=cols_fill[col],
                           fill='tonexty')

        lower = go.Scatter(x=X_mean.index, 
                           y=X_mean[col] - X_std[col],
                           mode='lines',
                           name=clf_names_dict[col], 
                           legendgroup=clf_names_dict[col], 
                           showlegend=False,
                           hoverinfo='skip',
                           line=dict(width=0),
                          )

        traces = traces + [lower, line, upper]

    fig = go.Figure(data=traces)   

    # Add ref DkSc best score
    # Meadian raw score
    fig.add_shape(dict(type='line', x0=0, x1=n_confs, y0=median_ref, y1=median_ref),
                 line=dict(color="#689AA8", width=1.5, dash = 'dot'))
    fig.add_annotation(x=n_confs - n_confs*0.06, y=median_ref,
                       showarrow=False,
                       font=dict(size=12),
                       text='med Dksc: <b>{:.2f}</b>'.format(median_ref), 
                       bgcolor="#B5D3DC")

    # Best raw score
    fig.add_shape(dict(type='line', x0=0, x1=n_confs, y0=best_ref, y1=best_ref),
                 line=dict(color="#B7AF9E", width=1.5, dash = 'dot'))
    fig.add_annotation(x=n_confs - n_confs*0.06, y=best_ref,
                       showarrow=False,
                       font=dict(size=12),
                       text='max Dksc: <b>{:.2f}</b>'.format(best_ref), 
                       bgcolor="#CEC9BD")
    # Libraries annotations
    fig.add_annotation(xref='paper', yref='paper', x=0.01, y=0.98,
            xanchor='left', yanchor='top', showarrow=False,
            align="left",
            text=f'<b>Total mols:</b> {n_actives}/{n_mols}; Ra = {round(n_actives/n_mols, 2)}' +
            f'<br><b>Test set:</b> {int(n_actives/4)}/{int(n_mols/4)}; Ra = {round(n_actives/n_mols, 2)}'
    )
    # AXES
    fig.update_xaxes(ticks='outside', showline=True, linewidth=2.7, title_font=dict(size=22),
                       linecolor='#43494F', mirror = True)
    # Y axis changes
    fig.update_yaxes(y_axis_params)
    fig.update_yaxes(ticks='outside', showline=True, title_font=dict(size=22),
                     linewidth=2.5, linecolor='black', mirror = True)
    fig.update_layout(
        height=500,
        template='plotly_white',
                      hoverlabel=dict(
                         bgcolor = 'white',
                         font_size=14
                      ),
                      xaxis = dict(
                         title='Number of protein conformations used'
                      ),
                      yaxis = dict(
                         title=f'Metric Score:<br><b>{metric_names[metric]}</b>'
                      ),
                      legend=dict(
                         font=dict(size=15),
                         orientation="h",
                         yanchor="bottom",
                         y=0.02,
                         xanchor="center",
                         x=0.5,
                         bgcolor="#F5F3EF"
                        ),
                        dragmode='pan',
                        margin=dict(l=30, r=30, t=5, b=30),
                        modebar=dict(orientation='v', activecolor='#1d89ff'))
    return fig
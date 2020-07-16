import plotly.graph_objects as go
import pandas as pd
import numpy as np
import pickle

# Read the pickle file
data_file = './FXA_ML_results_conformational_selection.obj'
with open(data_file, 'rb') as f:
    ALL_RESULTS = pickle.load(f)

# Parse the data from the dictionary
X_dksc = ALL_RESULTS['X_dksc']
X = ALL_RESULTS['X_ml']

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
                  'XGB'  : 'RFE (Grad. Boost)'}

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
                'ef_0.001'  : 'EF (chi=0.1%)',
                'ef_0.005'  : 'EF (chi=0.5%)',
                'ef_0.02'   : 'EF (chi=2.0%)',
                'ef_0.2'    : 'EF (chi=20.0%)',
               }

# LINE PLOT FUNCTION
def line_plot_metrics(split, selector, metric):
    query = f"split == '{split}' & selector == '{selector}' & metric == '{metric}'"

    # Ref score
    best_ref = X_dksc.query(query).max()['best_dksc']
    median_ref = X_dksc.query(query).median()['mean_dksc']

    # Results
    X_subset = X.query(query)
    X_subset = X_subset.reset_index().drop(['split', 'selector',  'metric', 0], axis=1)
    X_subset = X_subset.set_index(['desc', 'classifier']).T
    X_mean = X_subset.loc[:, 'mean']
    X_std = X_subset.loc[:, 'std']

    # Número de conformaciones
    n_confs = X_mean.shape[0]

    if (metric == 'roc_auc'):
        y_axis_params = dict(range=[0.4, 1], tick0=0.00, dtick=0.05)
    elif (metric == 'nef_auc'):
        y_axis_params = dict(range=[0.2, 1], tick0=0.00, dtick=0.05)
    elif 'ef_' in metric:
        y_axis_params = dict()
    else:
        y_axis_params = dict(range=[0.0, 1], tick0=0.00, dtick=0.1)


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
    # Best raw score
    fig.add_shape(dict(type='line', x0=0, x1=n_confs, y0=best_ref, y1=best_ref),
                 line=dict(color="#B7AF9E", width=1.5, dash = 'dot'))
    fig.add_annotation(x=n_confs - 10, y=best_ref,
                       showarrow=False,
                       font=dict(size=10),
                       text='max Dksc: <b>{:.2f}</b>'.format(best_ref), 
                       bgcolor="#CEC9BD")
    # Meadian raw score
    fig.add_shape(dict(type='line', x0=0, x1=n_confs, y0=median_ref, y1=median_ref),
                 line=dict(color="#689AA8", width=1.5, dash = 'dot'))
    fig.add_annotation(x=n_confs - 10, y=median_ref,
                       showarrow=False,
                       font=dict(size=10),
                       text='med Dksc: <b>{:.2f}</b>'.format(median_ref), 
                       bgcolor="#B5D3DC")
    # AXES
    fig.update_xaxes(ticks='outside', showline=True, linewidth=2,
                       linecolor='#43494F', mirror = True)
    # Y axis changes
    fig.update_yaxes(y_axis_params)
    fig.update_yaxes(ticks='outside', showline=True, 
                     linewidth=2, linecolor='black', mirror = True)
    fig.update_layout(
        height=600,
        template='plotly_white',
                      hoverlabel=dict(
                         bgcolor = 'white',
                         font_size=12.5
                      ),
                      xaxis = dict(
                         title='Number of protein conformations used'
                      ),
                      yaxis = dict(
                         title=f'Metric Score:<br><b>{metric_names[metric]}</b>'
                      ),
                      legend=dict(
                         orientation="h",
                         yanchor="bottom",
                         y=0.02,
                         xanchor="center",
                         x=0.5,
                         bgcolor="#F5F3EF"
                        ),
                        dragmode='pan',
                        margin=dict(l=30, r=30, t=10, b=30),
                        modebar=dict(orientation='v', activecolor='#1d89ff'))
    return fig
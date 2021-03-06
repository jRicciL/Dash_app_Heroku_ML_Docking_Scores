import plotly.graph_objects as go
import pandas as pd
import numpy as np
import pickle
import dash_table
import dash_html_components as html

# Read the pickle file
app_data = './dash_app_data.pkl'
with open(app_data, 'rb') as f:
    APP_DATA = pickle.load(f)

# Assing protein data
FXA_DATA = APP_DATA['FXA']
CDK2_DATA = APP_DATA['CDK2']

# Assing values: ML Data
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
              '1NN'     : 'rgb(230, 73, 79)',
              
              'MEAN'    : 'rgb(60, 139, 190)',
              'MED'     : 'rgb(245, 145, 40)',
              'RANK'    : 'rgb(165, 200, 135)',
              'MIN'     : 'rgb(65, 0, 135)',
              'MAX'     : 'rgb(165, 50, 235)',
              'EUN'     : 'rgb(165, 100, 35)',
              'VOTE'    : 'rgb(165, 150, 135)',
              'ECR'     : 'rgb(191, 50, 135)'
              }

cols_fill = {'LogReg'   : 'rgba(134, 102, 183, 0.25)',
             'rbfSVC'   : 'rgba(216, 143, 48, 0.25)',
             'XGB_tree' : 'rgba(9, 153, 149, 0.25)',
             '1NN'      : 'rgba(230, 73, 79, 0.25)',

             'MEAN'     : 'rgba(60, 139, 190, 0.2)',
             'MED'      : 'rgba(218, 120, 20, 0.25)',
             'RANK'     : 'rgba(155, 190, 125, 0.35)',
             'MIN'      : 'rgba(65, 0, 135, 0.35)',
             'MAX'      : 'rgba(165, 50, 235, 0.35)',
             'EUN'      : 'rgba(165, 100, 35, 0.35)',
             'VOTE'     : 'rgba(165, 150, 135, 0.35)',
             'ECR'      : 'rgba(191, 50, 135, 0.2)'
             }

# Dictionary names
split_names = {'rand': 'Random',
               'scff': 'Scaffold'}

methodologies_dic = {
    'ml': 'Machine Learning',
    'cs': 'Consensus Scoring'
}

selector_names = {'rand' : 'Random',
                  'LR'   : 'RFE (Log. Reg.)',
                  'RF'   : 'RFE (Rand. Forest)',
                  'XGB'  : 'RFE (Grad. Boosting)'}

clf_names_dict = {'LogReg'  : 'Log. Regression',
                  'rbfSVC'  : 'RBF SVM',
                  'XGB_tree': 'Gradient Boosting',
                  '1NN'     : '1-NN Classifier'}

cs_names_dict = dict(zip(['MEAN', 'MED', 'RANK', 'MIN', 'MAX', 'EUN', 'VOTE', 'ECR'], 
                         ['MEAN', 'MED', 'RANK', 'MIN', 'MAX', 'EUN', 'VOTE', 'ECR']))

metric_names = {'roc_auc'   : 'ROC-AUC',
                # 'nef_auc'   : 'NEF-AUC',
                'pr_auc'    : 'Pr & Rcll-AUC',
                'bedroc_20' : 'BEDROC (a=20)',
                # 'bedroc_10' : 'BEDROC (a=10)',
                # 'bedroc_2'  : 'BEDROC (a=2)',
                'bedroc_0.5': 'BEDROC (a=0.5)',
                'ef_0.2'    : 'NEF (chi=20.0%)',
                'ef_0.02'   : 'NEF (chi=2.0%)',
                # 'ef_0.005'  : 'EF (chi=0.5%)',
                # 'ef_0.001'  : 'EF (chi=0.1%)',
               }

dr_methods_names = {
    'mds' : 'cMDS',
    'tsne': 't-SNE'
}

prot_section_dr = {
    'sec'    : 'Secondary Structure (Ca)',
    'pkt'    : 'Pocket Residues (Ca)',
    'vol_pkt': 'Pocket Shape (POVME) (cMDS)'
}

point_size_by = {
    'LigMass'            : 'Ligand MW',
    'Pocket Volume (Pkt)': 'Pocket Volume (A)',
    #'None': 'None'
}

conf_presel_selectors = {
    'LR'   : 'LogReg',
    'RF'   : 'RandomForest',
    'XGB'  : 'XGB_tree'
}

conf_presel_split = {
    'rand': 'random',
    'scff': 'scaffold'
}

def get_preselected_confs(split, selector, n_confs, protein_name):
    df_SELECTED_CONFS = get_data(protein_name, 'df_SELECTED_CONFS')

    # Get the selector-split set
    selected_confs = None
    if selector != 'rand':
        selected_confs = df_SELECTED_CONFS[
            f'RFE_{conf_presel_selectors[selector]}_{conf_presel_split[split]}'
            ]

        selected_confs = selected_confs[:n_confs]
    
    return selected_confs


def get_y_axis_params(metric, plot_type = 'line'):
    if (metric == 'roc_auc' and plot_type == 'line'):
        y_axis_params = dict(range=[0.4, 1], tick0=0.00, dtick=0.05)
    elif (metric == 'nef_auc' and plot_type == 'line'):
        y_axis_params = dict(range=[0.2, 1], tick0=0.00, dtick=0.05)
    elif 'ef_0' in metric:
        y_axis_params = dict()
    else:
        y_axis_params = dict(range=[0.0, 1], tick0=0.00, dtick=0.1)
    return y_axis_params


# DT Table
def render_mtd_table(protein_name, preselected_confs):
    df_PROT_METADATA = get_data(protein_name, 'df_PROT_METADATA')

    #df_PROT_METADATA.loc[:,'PDB-id'] = df_PROT_METADATA['PDB-id'].apply(lambda x: html.A(href=f'https://www.rcsb.org/structure/{x}', children=x, target='_blank'))
    # df_PROT_METADATA.loc[:,'Resolution'] = df_PROT_METADATA['Resolution'].apply(lambda x: round(x, 2))
    # df_PROT_METADATA.loc[:,'Coverage'] = df_PROT_METADATA['Coverage'].apply(lambda x: round(x, 2))
    # df_PROT_METADATA.loc[:,'Date'] = df_PROT_METADATA['Date'].dt.strftime('%m/%d/%Y')
    # df_PROT_METADATA = df_PROT_METADATA.drop(['Pocket Volume (Sec)'], axis=1)

    df_PROT_METADATA.colums = [
        'PDB id', 'Pub. Date', 'Resolution', 'Coverage',
        'Ligand', 'Ligand MW', 'Pocket Volume', 'Conformation'
    ]

    # Subset the dataframe
    if preselected_confs is not None:
        X = df_PROT_METADATA.iloc[preselected_confs]
    elif preselected_confs is  None:
        X = df_PROT_METADATA.iloc[:15]

    mtd_table = dash_table.DataTable(
        id='dt-table',
        data= X.to_dict('records'),
        columns=[{"name": i, "id": i} for i in X.columns],
        fixed_rows={'headers': True},
        sort_action="native",
        style_as_list_view=True,
        style_table={'height': '500px', 'overflowY': 'auto'},
        style_cell={
            'textAlign': 'center',
            'font-size': '0.8rem',
            'padding': '2px 8px 2px 8px',
            'color': '#333'
            },
        style_header={
                'color': 'white',
                'backgroundColor': '#444',
                'fontWeight': 'bold',
                'font-size': '1rem',
                'text-align': 'center'
            },
    )

    return mtd_table


# SCATTER PLOT
scatter_colors = ['#2a7885', '#5a8b59', '#f64a3b', 'grey', '#fecc6a', '#69d7c4']

def mds_plot(protein_name, dr_method, prot_section, point_size_by, preselected_confs):
    # Table of protein metadata
    df_PROT_METADATA = get_data(protein_name, 'df_PROT_METADATA')
    

    df_DIM_REDUCT = get_data(protein_name, 'df_DIM_REDUCT')

    # Temporal: if pocket volume
    if prot_section == 'vol_pkt':
        dr_method = 'mds'

    # Get the dimensions
    colname = f'{dr_method}_{prot_section}_'
    Z = df_DIM_REDUCT[[colname + 'x', colname + 'y']]
    Z.columns = ['x', 'y']

    # Add the columns to the metadata
    X_mtd = pd.concat([df_PROT_METADATA.set_index('PDB-id'),
                Z], axis=1)
    X_mtd.reset_index(inplace=True)
    X_mtd.LigMass = pd.to_numeric(X_mtd.LigMass).fillna(0)

    color_by='Conformation'
    labels_col = X_mtd[color_by]

    # Define colors
    if labels_col.dtype == 'object':
        labels = labels_col.unique()
        
        # Select the number of colors
        n_labels = len(labels)
        color_mapper = {i:j for i, j in 
                        zip(labels, scatter_colors[:n_labels])}
        
        X_mtd['color_col'] = labels_col.map(color_mapper)


    fig = go.Figure()


    for label in labels:
        subset = X_mtd.query(f'{color_by} == "{label}"')
        size = subset[point_size_by]

        formatted_text = [
            f'<b>Conf:</b> {idx}' + 
            f'<br><b>Ligand:</b> {lig}'+
            f'<br><b>Ligand MW:</b> {lig_mass} '  +
            f'<br><b>Pkt volume:</b> {pkt_vol} A<sup>3</sup>'  
            for idx, lig, lig_mass, pkt_vol in  
            zip(subset['PDB-id'], 
                subset.Ligand, 
                subset.LigMass,
                subset['Pocket Volume (Pkt)'])]
        fig.add_trace(
            go.Scatter(
                x = subset.x,
                y = subset.y,
                name=label,
                showlegend=False,
                mode='markers',
                marker=dict(
                    color=subset['color_col'],
                    size=size,
                    sizemode='diameter',
                    sizeref=2.*max(size)/(5.**2),
                    sizemin=1,
                    line_width=0
                ),           
                #selectedpoints = preselected_confs,
                selected=dict(
                    marker=dict(
                        opacity=1
                    )
                ),
                opacity=0.8,
                hoverinfo='text',
                hovertext=formatted_text
            )
        )
    
    if preselected_confs is not None:
        selected = X_mtd.iloc[preselected_confs]
        fig.add_trace(
            go.Scatter(
                x = selected.x,
                y = selected.y,
                name = 'Selected',
                mode='markers',
                hoverinfo='none',  
                marker=dict(
                    color='rgba(0, 0, 0, 0)',
                    size=selected[point_size_by],
                    sizemode='diameter',
                    sizeref=selected[point_size_by].max()/15,
                    line_width=2,
                    line_color='black'
                ),
            )
        )

    # AXES
    fig.update_xaxes(ticks='outside', showline=True, linewidth=2.7, title_font=dict(size=22),
                       linecolor='#43494F', mirror = True)
    fig.update_yaxes(ticks='outside', showline=True, title_font=dict(size=22),
                     linewidth=2.5, linecolor='black', mirror = True)
    fig.update_layout(
        height=450,
        template='plotly_white',
        hoverlabel=dict(
            bgcolor = 'white',
            font_size=14
        ),
        xaxis = dict(
            title='First Dimension',
            zeroline=True, zerolinecolor='#BBBBBB', zerolinewidth=2
        ),
        yaxis = dict(
            title=f'Second Dimension',
            zeroline=True, zerolinecolor='#BBBBBB', zerolinewidth=2
        ),
        legend=dict(
            font=dict(size=15),
            orientation="h",
            yanchor="top",
            y=1,
            xanchor="right",
            x=1,
            bgcolor="#F5F3EF"
        ),
        dragmode='pan',
        margin=dict(l=30, r=30, t=5, b=30),
        modebar=dict(orientation='v', activecolor='#1d89ff')
    )

    return fig


# VIOLIN PLOT FUNCTION
def violin_plot_metrics(metric, protein_name, show_benchmarks, preselected_confs):
    if 'bedroc' in metric or 'ef_0' in metric:
        metric_filter = metric.replace('_', '-')
    else:
        metric_filter = metric
    
    df_DKSC_METRICS = get_data(protein_name, 'df_DKSC_METRICS')
    W = df_DKSC_METRICS.filter(regex=metric_filter)
   
    if len(show_benchmarks) == 0:
        W = W.filter(regex='scff|merged')
    
    y_axis_params = get_y_axis_params(metric, 'violin')

    fig = go.Figure()

    for column in W:
        fig.add_trace(
            go.Violin(
                y = W[column],
                name = column.split('_')[0].upper(),
                jitter = 1, points = 'all', side = 'positive',
                box_visible = True,
                marker = dict(
                    size = 6,
                    opacity=0.3
                ),
                selectedpoints = preselected_confs,
                selected=dict(
                    marker=dict(
                        opacity=1
                    )
                ),
                opacity=0.8,
                hoverinfo='text',
                hovertext=[f'{i}: {str(j)}' for i, j in zip(W.index, W[column])]
            )
        )

    # AXES
    fig.update_xaxes(ticks='outside', showline=True, linewidth=2.7, title_font=dict(size=22),
                       linecolor='#43494F', mirror = True)
    # Y axis changes
    fig.update_yaxes(y_axis_params)
    fig.update_yaxes(ticks='outside', showline=True, title_font=dict(size=22),
                     linewidth=2.5, linecolor='black', mirror = True)
    fig.update_layout(
        height=450,
        template='plotly_white',
        hoverlabel=dict(
            bgcolor = 'white',
            font_size=14
        ),
        xaxis = dict(
            title='Molecular Data Sets'
        ),
        yaxis = dict(
            title=f'Metric Score:<br><b>{metric_names[metric]}</b>',
            zeroline=True, zerolinecolor='#999999'
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
        modebar=dict(orientation='v', activecolor='#1d89ff')
    )
    
    return fig



# LINE PLOT FUNCTION
def line_plot_metrics(split, 
                      selector, 
                      metric, 
                      protein_name, 
                      n_confs_sel,
                      methodology
                      ):

    query = f"split == '{split}' & selector == '{selector}' & metric == '{metric}'"

    dict_ML_RESULTS = get_data(protein_name, 'dict_ML_RESULTS')
    X = None
    if methodology == 'ml':
        X = dict_ML_RESULTS['X_ml']
        classifier = 'classifier'
        clf_names = clf_names_dict
    elif methodology == 'cs':
        X = get_data(protein_name, 'df_CS_RESULTS')
        classifier = 'consensus'
        clf_names = cs_names_dict

    # Mols info
    libs = mos_info[protein_name]
    n_mols = libs['num_mols']
    n_actives = libs['num_actives']

    # Ref score
    X_dksc = dict_ML_RESULTS['X_dksc']
    best_ref = X_dksc.query(query).max()['best_dksc']
    median_ref = X_dksc.query(query).median()['median_dksc']

    # Results
    X_subset = X.query(query)
    X_subset = X_subset.reset_index().drop(['split', 'selector',  'metric', 0], axis=1)
    X_subset = X_subset.set_index(['desc', classifier]).T
    X_mean = X_subset.loc[:, 'mean']
    X_std = X_subset.loc[:, 'std']

    # N??mero de conformaciones
    n_confs = X_mean.shape[0]

    y_axis_params = get_y_axis_params(metric, 'line')

    traces = []
    for col in X_mean.columns:
        # Create the upper and lower bounds
        upper = X_mean[col] + X_std[col]
        lower = X_mean[col] - X_std[col]

        upper = go.Scatter(x=X_mean.index, 
                           y=X_mean[col] + X_std[col],
                           mode='lines',
                           name=clf_names[col], 
                           legendgroup=clf_names[col], 
                           showlegend=False,
                           line=dict(width=0),
                           fillcolor=cols_fill[col],
                           hoverinfo='skip',
                           fill='tonexty')

        line = go.Scatter(x=X_mean.index, 
                           y=X_mean[col],
                           mode='lines',
                           name=clf_names[col],
                           hovertemplate = 
                           f'<b style="color: {cols_lines[col]}">{clf_names[col]}</b>' +
                           '<br>' +
                           '<b><i>k</i> confs:</b> %{x}' +
                           '<br>' +
                           f'<b><i>{metric_names[metric]}</i>:</b> ' + 
                           '%{y:.2f}' +
                           '<extra></extra>',
                           legendgroup=clf_names[col], 
                           line=dict(width=2.5,
                                     color=cols_lines[col]),
                           fillcolor=cols_fill[col],
                           fill='tonexty')

        lower = go.Scatter(x=X_mean.index, 
                           y=X_mean[col] - X_std[col],
                           mode='lines',
                           name=clf_names[col], 
                           legendgroup=clf_names[col], 
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

    # Slider trace
    fig.add_shape(dict(type='line', x0=n_confs_sel, x1=n_confs_sel,
                    yref='paper',
                    y0=0, y1=1),
                 line=dict(color="blue", width=1.5, dash = 'dot'))

    fig.add_annotation(x=n_confs - n_confs*0.06, y=best_ref,
                       showarrow=False,
                       font=dict(size=12),
                       text='max Dksc: <b>{:.2f}</b>'.format(best_ref), 
                       bgcolor="#CEC9BD")
    # Libraries annotations
    fig.add_annotation(xref='paper', yref='paper', x=0.01, y=0.98,
            xanchor='left', yanchor='top', showarrow=False,
            align="left",
            text=f'<b>Total mols:</b><br> {n_actives} <b>/</b> {n_mols}; Ra = {round(n_actives/n_mols, 2)}' +
            f'<br><b>Test set:</b><br> {int(n_actives/4)} <b>/</b> {int(n_mols/4)}; Ra = {round(n_actives/n_mols, 2)}'
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
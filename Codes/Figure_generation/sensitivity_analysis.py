# -*- coding: utf-8 -*-
"""
Created on Thu Nov 25 19:02:09 2021

@author: rfuchs
"""

import os
import json
import pandas as pd
import seaborn as sns
from rubaliz import rubaliz
import matplotlib.pyplot as plt

# Change it with your path
os.chdir('C:/Users/rfuchs/Documents/GitHub/rubaliz_paper/')

# Import campaigns metadata and importation settings
path = 'info_dicts.json'
with open(path, "r") as read_file:
    info_dicts = json.load(read_file)
    
#==================================
# Boundaries extraction
#==================================

deltas = pd.DataFrame()
for info_dict in info_dicts:
    
    if info_dict['cruise_name'] == 'KN207-01':
        cols_aliases = ['Fluorescence', 'Oxygen', 'Salinity']
    else:
        cols_aliases = ['Fluorescence', 'Oxygen', 'Pot. temp.', 'Salinity', 'Density']

    #==================================
    # Upper boundary extraction
    #==================================
    
    # Fit the model on the full data
    ruba = rubaliz(info_dict)
    ruba.fit()
    ub_ref = ruba.ub_estim[0]
    lb_ref = ruba.lb_estim[0]

    # Fit the model on the data minus one variable  
    ub_holdout = pd.DataFrame()
    lb_holdout = pd.DataFrame()

    for col, col_alias in zip(ruba.available_cols, ruba.available_aliases):
        
        #===============================
        # Upper boundary sensitivity
        #===============================
        
        ub_data = ruba.ub_data
        hold_out_one_var = ub_data.loc[:,~ub_data.columns.isin([col])]
        ub = ruba.rupture_confidence_interval(hold_out_one_var, 1, [280, 320])
        ub.index = [col_alias]
        ub_holdout = ub_holdout.append(ub)

        #===============================
        # Lower boundary sensitivity
        #===============================   
        
        lb_data = ruba.lb_data
        hold_out_one_var = lb_data.loc[:,~lb_data.columns.isin([col])]
        lb = ruba.rupture_confidence_interval(hold_out_one_var, 1, [1000, 1300])
        lb.index = [col_alias]
        lb_holdout = lb_holdout.append(lb)
    
    #===============================
    # Wrap up
    #===============================   
        
    delta_ub = ((ub_ref - ub_holdout[['Mean']]) / ub_ref).abs().T
    delta_ub['boundary'] = ['Upper']
    delta_lb = ((lb_ref - lb_holdout[['Mean']]) / lb_ref).abs().T
    delta_lb['boundary'] = ['Lower']

    delta = pd.concat([delta_ub, delta_lb], axis = 0).reset_index(drop = True)
    delta['cruise'] = ruba.cruise
    delta['station'] = ruba.station     

    deltas = pd.concat([deltas, delta])
 
#==================================
# Plotting the sensibility analysis
#==================================

n_curves = 5
colors = sns.color_palette("colorblind", n_curves)
colors = dict(zip(deltas.columns[:n_curves], colors))
#colors = dict(zip(['Fluorescence', 'Oxygen', 'Pot. temp.', 'Salinity', 'Density'], colors))

fig, axs = plt.subplots(2, 1, figsize=(7, 5), sharex=True)

upper_deltas = deltas[deltas['boundary'] == 'Upper']
del(upper_deltas['boundary'])
(upper_deltas.set_index(['cruise', 'station']) * 100).plot(kind='bar', stacked=True,\
                                                    ax = axs[0],\
                                                    color = colors)
plt.legend(['Fluorescence', 'Oxygen', 'Pot. temp.', 'Salinity', 'Density'],\
           loc="lower center", bbox_to_anchor=(0.5, -0.05),\
           ncol = 5, fontsize = 9)
axs[0].set_title('a) Mesopelagic upper boundary')
axs[0].set_ylabel("Variation (%)")

lower_deltas = deltas[deltas['boundary'] == 'Lower']
del(lower_deltas['boundary'])
(lower_deltas.set_index(['cruise', 'station']) * 100).plot(kind='bar', stacked=True,\
                                                          ax = axs[1],\
                                                          color = colors)
axs[1].set_title('b) Mesopelagic lower boundary')
axs[1].get_legend().remove()
axs[1].set_xticklabels((lower_deltas['cruise'] + ' ' + lower_deltas['station']).tolist())
axs[1].set_xlabel("")
axs[1].set_ylabel("Variation (%)")

plt.tight_layout()
plt.show()


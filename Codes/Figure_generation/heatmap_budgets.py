# -*- coding: utf-8 -*-
"""
Created on Thu Mar  3 15:23:53 2022

@author: rfuchs
"""

import os 
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Change with your path:
os.chdir('C:/Users/rfuchs/Documents/GitHub/rubaliz_paper/Results/integration')

#=====================
# Import the data
#=====================

disc = pd.read_csv('Cbudget.csv', sep = ';')
disc = disc.rename(columns = {'METHOD': 'Method'})

color = dict(zip(set(disc['Method']), ['#9467bd', '#1f77b4', '#2ca02c', '#d62728',\
                                       'orange', 'tab:pink', 'tab:cyan']))
        
hm = pd.pivot_table(disc, values = 'Discrepancy', index = 'Station', columns = 'Method')
hm = hm[['Ez0.1', 'Ez1', 'MLD temperature', 'MLD density', 'PPZ',
       '200-1000', 'RUBALIZ']]
                

stations = ['D341 PAP', 'KN207-01 QL-2', 'KN207-03 PS-3&4', 'MALINA 620',\
            'PEACETIME FAST', 'TONGA STATION 8']

disc = disc[disc['Station'].isin(stations)]
methods = disc['Method']

#=====================
# Plot
#=====================

g = sns.heatmap(hm, vmin = -1100, vmax = 200, cmap = sns.color_palette("Spectral", as_cmap=True))
g.set_facecolor('grey')
plt.title('Discrepancy $\Delta$ (mgC $m^{-2}d^{-1}$)')
plt.tight_layout()
plt.show()

disc.columns

# -*- coding: utf-8 -*-
"""
Created on Wed Mar  9 15:40:15 2022

@author: rfuchs
"""

import os
import json
import numpy as np
import pandas as pd
from rubaliz import rubaliz
import matplotlib.pyplot as plt

# Change with your path:
os.chdir('C:/Users/rfuchs/Documents/GitHub/rubaliz_paper/')

# Import campaigns metadata and importation settings
with open('info_dicts.json', "r", encoding = 'UTF-8') as read_file:
    info_dicts = json.load(read_file)

info_dict = info_dicts[-4]
ruba = rubaliz(info_dict)

zones = pd.DataFrame()
    
#==================================
# Upper boundary extraction
#==================================

data = ruba.format_data([0, 320])
nb_signals = len(ruba.available_cols)
nb_ctds_upper = data.shape[1] // nb_signals

all_upper = pd.DataFrame()
for nb_ctd in range(1, nb_ctds_upper + 1):
   data_ctd = data.iloc[:,:(nb_ctd * nb_signals)] 
   upper = ruba.rupture_confidence_interval(data_ctd, 1, [280, 320])
   upper.columns = ['Upper boundary', 'std Upper boundary']
   upper['Number of CTDs'] = nb_ctd
   all_upper = pd.concat([all_upper, upper])

upper = all_upper.iloc[-1]

#==================================
# Lower boundary extraction
#==================================

data = ruba.format_data([int(np.ceil(upper['Upper boundary'])), 1300])
nb_signals = len(ruba.available_cols)
nb_ctds_lower = data.shape[1] // nb_signals

all_lower = pd.DataFrame()
for nb_ctd in range(1, nb_ctds_lower + 1):
   data_ctd = data.iloc[:,:(nb_ctd * nb_signals)] 
   lower = ruba.rupture_confidence_interval(data_ctd, 1, [1000, 1300])
   lower.columns = ['Lower boundary', 'std Lower boundary']
   lower['Number of CTDs'] = nb_ctd
   all_lower = pd.concat([all_lower, lower])


fig, axs = plt.subplots(2,2, figsize = (10, 10))
axs[0][0].plot(all_upper['Number of CTDs'], all_upper['Upper boundary'], color = 'black')
axs[0][0].set_ylabel('Upper boundary estimate (m)')
axs[0][0].set_title('a) Upper boundary estimate')
axs[0][0].set_ylim([0,200])
axs[0][0].invert_yaxis()


axs[0][1].plot(all_upper['Number of CTDs'], all_upper['std Upper boundary'], color = 'black')
axs[0][1].set_ylabel('Upper boundary std (m)')
axs[0][1].set_xlabel('Number of CTD casts')
axs[0][1].set_title('b) Upper boundary standard error')
axs[0][1].set_ylim([0,33])

axs[1][0].plot(all_lower['Number of CTDs'], all_lower['Lower boundary'], color = 'black') 
axs[1][0].set_ylabel('Lower boundary estimate (m)')
axs[1][0].set_title('c) Lower boundary estimate')
axs[1][0].set_ylim([200,1000])
axs[1][0].invert_yaxis()


axs[1][1].plot(all_lower['Number of CTDs'], all_lower['std Lower boundary'], color = 'black')
axs[1][1].set_ylabel('Lower boundary std (m)')
axs[1][1].set_xlabel('Number of CTD casts')
axs[1][1].set_title('d) Lower boundary standard error')
axs[1][1].set_ylim([0,33])

# -*- coding: utf-8 -*-
"""
Created on Wed Mar  9 15:40:15 2022

@author: rfuchs
"""

import os
import json
import pandas as pd
#from rubaliz import rubaliz
import matplotlib.pyplot as plt

# Change with your path:
os.chdir('C:/Users/rfuchs/Documents/GitHub/rubaliz_paper/')

# Import campaigns metadata and importation settings
with open('info_dicts.json', "r") as read_file:
    info_dicts = json.load(read_file)

info_dict = info_dicts[-4]
ruba = rubaliz(info_dict)

zones = pd.DataFrame()
    
#==================================
# Euphotic extraction
#==================================

data = ruba.format_data([0, 320])
nb_signals = len(ruba.available_cols)
nb_ctds_eupho = data.shape[1] // nb_signals

all_eupho = pd.DataFrame()
for nb_ctd in range(1, nb_ctds_eupho + 1):
   data_ctd = data.iloc[:,:(nb_ctd * nb_signals)] 
   eupho = ruba.rupture_confidence_interval(data_ctd, 1, [280, 320])
   eupho.columns = ['Upper boundary', 'std Upper boundary']
   eupho['Number of CTDs'] = nb_ctd
   all_eupho = all_eupho.append(eupho)

eupho = all_eupho.iloc[-1]
#==================================
# Mesopelagic extraction
#==================================

data = ruba.format_data([eupho['Upper boundary'], 1300])
nb_signals = len(ruba.available_cols)
nb_ctds_meso = data.shape[1] // nb_signals

all_meso = pd.DataFrame()
for nb_ctd in range(1, nb_ctds_meso + 1):
   data_ctd = data.iloc[:,:(nb_ctd * nb_signals)] 
   meso = ruba.rupture_confidence_interval(data_ctd, 1, [1000, 1300])
   meso.columns = ['Lower boundary', 'std Lower boundary']
   meso['Number of CTDs'] = nb_ctd
   all_meso = all_meso.append(meso)


fig, axs = plt.subplots(2,2, figsize = (10, 10))
axs[0][0].plot(all_eupho['Number of CTDs'], all_eupho['Upper boundary'], color = 'black')
axs[0][0].set_ylabel('Upper boundary estimate (m)')
axs[0][0].set_title('a) Upper boundary estimate')
axs[0][0].set_ylim([0,200])
axs[0][0].invert_yaxis()


axs[0][1].plot(all_eupho['Number of CTDs'], all_eupho['std Upper boundary'], color = 'black')
axs[0][1].set_ylabel('Upper boundary std (m)')
axs[0][1].set_xlabel('Number of CTD casts')
axs[0][1].set_title('b) Upper boundary standard error')
axs[0][1].set_ylim([0,33])

axs[1][0].plot(all_meso['Number of CTDs'], all_meso['Lower boundary'], color = 'black') 
axs[1][0].set_ylabel('Lower boundary estimate (m)')
axs[1][0].set_title('c) Lower boundary estimate')
axs[1][0].set_ylim([200,1000])
axs[1][0].invert_yaxis()


axs[1][1].plot(all_meso['Number of CTDs'], all_meso['std Lower boundary'], color = 'black')
axs[1][1].set_ylabel('Lower boundary std (m)')
axs[1][1].set_xlabel('Number of CTD casts')
axs[1][1].set_title('d) Lower boundary standard error')
axs[1][1].set_ylim([0,33])

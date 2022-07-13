# -*- coding: utf-8 -*-
"""
Created on Thu Nov 25 19:02:09 2021

@author: rfuchs
"""

import os
import json
import pandas as pd
from rubaliz import rubaliz

# Change with your path:
os.chdir('C:/Users/rfuchs/Documents/GitHub/rubaliz_paper/')

# Import campaigns metadata and importation settings
with open('info_dicts.json', "r", encoding='UTF-8') as read_file:
    info_dicts = json.load(read_file)
 
#==================================
# Boundaries extraction
#==================================

zones = pd.DataFrame()
for info_dict in info_dicts:
    
    ruba = rubaliz(info_dict)
    ruba.fit()
    zone = ruba.boundaries
    zone['cruise'] = info_dict['cruise_name']
    zone['station'] = info_dict['station_name']
    
    zone['Upper CTD number'] = ruba.nb_ctd_ub
    zone['Lower CTD number'] = ruba.nb_ctd_lb    
    zones = pd.concat([zones, zone])
    
        
zones = zones[['cruise', 'station', 'Upper boundary', 'std Upper boundary',\
               'Upper CTD number', 'Lower boundary', 'std Lower boundary',\
               'Lower CTD number']]   

zones.loc[:, ['std Upper boundary', 'std Lower boundary']] =\
    zones[['std Upper boundary', 'std Lower boundary']].round(0)
 
zones.loc[:,['Upper boundary', 'Lower boundary']] =\
    zones[['Upper boundary', 'Lower boundary']].round(0)
   
zones.to_csv('Results/ruptures/zones.csv', index = False)

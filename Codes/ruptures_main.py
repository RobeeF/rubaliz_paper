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
with open('info_dicts.json', "r") as read_file:
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
    
    zone['Euphotic CTD number'] = ruba.nb_ctd_ub
    zone['Mesopelagic CTD number'] = ruba.nb_ctd_lb    
    zones = zones.append(zone)
        
zones = zones[['cruise', 'station', 'Euphotic end', 'std Euphotic end',\
               'Euphotic CTD number', 'Mesopelagic end', 'std Mesopelagic end',\
               'Mesopelagic CTD number']]   

zones.loc[:, ['std Euphotic end', 'std Mesopelagic end']] =\
    zones[['std Euphotic end', 'std Mesopelagic end']].round(0)
 
zones.loc[:,['Euphotic end', 'Mesopelagic end']] =\
    zones[['Euphotic end', 'Mesopelagic end']].round(0)
   
zones.to_csv('Results/ruptures/zones.csv', index = False)

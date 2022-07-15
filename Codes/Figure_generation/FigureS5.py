# -*- coding: utf-8 -*-
"""
Created on Thu Nov 25 19:02:09 2021

@author: rfuchs
"""

import os
import json
import pandas as pd
import ruptures as rpt
from rubaliz import rubaliz

import numpy as np
from copy import deepcopy
import matplotlib.pyplot as plt

# Change with your path:
os.chdir('C:/Users/rfuchs/Documents/GitHub/rubaliz_paper/')

#==================================
# Without fluo and [02]
#==================================

# Import campaigns metadata and importation settings
with open('info_dicts.json', "r", encoding = 'UTF-8') as read_file:
    info_dicts = json.load(read_file)
 
# Do not use Fluorescence and [02] curves
for info_dict in info_dicts:
    info_dict['Fluorescence'] = None
    info_dict['Oxygen'] = None
    
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

   
zones_allvars = pd.read_csv('Results/ruptures/zones.csv')

plt.scatter(zones_allvars['Upper boundary'], zones['Upper boundary'])
plt.scatter(zones_allvars['Lower boundary'], zones['Lower boundary'])

delta_upper = (zones_allvars['Upper boundary'] - zones['Upper boundary']).abs().median()
delta_lower = (zones_allvars['Lower boundary'] - zones['Lower boundary']).abs().median()

deltas = np.array([delta_upper, delta_lower]).reshape(1,-1)
pd.DataFrame(deltas, columns = ['Upper boundary', 'Lower boundary'])


#==================================
# On simulated data
#==================================

# generate signal
n_noisevars = 10
depth_max = 1300
n_samples, dim, sigma = depth_max, 1, 1
n_bkps = 2  # number of breakpoints
delta = [0.1,0.6]
signal, bkps = rpt.pw_constant(n_samples, dim, n_bkps, noise_std=sigma, delta = delta)

signal_noised = deepcopy(signal)
result_noise = rpt.Binseg(model="rbf").fit(signal_noised).predict(n_bkps=2)

bkps_noise = [result_noise]

for noise_idx in range(n_noisevars):
    noise = np.random.normal(0.5, sigma, 1300)[..., np.newaxis]
    signal_noised = np.concatenate([signal_noised, noise], axis = 1)
    result_noise = rpt.Binseg(model="rbf").fit(signal_noised).predict(n_bkps=2)
    bkps_noise.append(result_noise)

result_noise = rpt.Binseg(model="rbf").fit(signal_noised).predict(n_bkps=2)
fig, axs = rpt.display(signal_noised, bkps, result_noise)
fig.gca().invert_yaxis()
plt.show()

df = pd.DataFrame(bkps_noise, columns = ['Upper boundary', 'Lower boundary', 'Bottom']).iloc[:,:2]
df = df - bkps[:2]

fig, axs = plt.subplots(2, 1, sharex=True)
axs[0].scatter(range(n_noisevars + 1), df['Upper boundary'])
#axs[0].set_xlabel('Number of noise variables')
axs[0].set_ylabel('Upper boundary (m)')

axs[1].scatter(range(n_noisevars + 1), df['Lower boundary'])
axs[1].set_xlabel('Number of noise variables')
axs[1].set_ylabel('Lower boundary (m)')
plt.suptitle('Distance to true boundaries')


# detection
result_noise = rpt.Binseg(model="rbf").fit(signal_noised).predict(n_bkps=2)
fig, axs = rpt.display(signal_noised, bkps, result_noise)
fig.gca().invert_yaxis()
plt.show()
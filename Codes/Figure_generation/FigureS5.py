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

from Codes.Figure_generation.noise_generation import blue_noise, pink_noise, white_noise

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
delta = [0.6,-0.4]


bkps = [440, 865, 1300]
signal = white_noise(depth_max)
signal[bkps[0]:bkps[1]] = signal[bkps[0]:bkps[1]] + delta[0]
signal[bkps[1]:] = signal[bkps[1]:] + delta[1]
signal = signal[...,np.newaxis]

#delta = [0.3,0.6]
#signal, bkps = rpt.pw_constant(n_samples, dim, n_bkps, noise_std=sigma, delta = delta)

signals_noised = {}
signals_noised['white'] = deepcopy(signal)
signals_noised['blue'] = deepcopy(signal)
signals_noised['pink'] = deepcopy(signal)
signals_noised['red'] = deepcopy(signal)

results_noise = {}
results_noise['white'] = rpt.Binseg(model="rbf").fit(signal).predict(n_bkps=2)
print(bkps)
print(results_noise['white'])
results_noise['blue'] = rpt.Binseg(model="rbf").fit(signal).predict(n_bkps=2)
results_noise['pink'] = rpt.Binseg(model="rbf").fit(signal).predict(n_bkps=2)
results_noise['red'] = rpt.Binseg(model="rbf").fit(signal).predict(n_bkps=2)

bkps_noises = {}
bkps_noises['white'] = [results_noise['white']]
bkps_noises['blue'] = [results_noise['blue']]
bkps_noises['pink'] = [results_noise['pink']]
bkps_noises['red'] = [results_noise['red']]

#bkps_noise = [result_noise]

for noise_idx in range(n_noisevars):
    # White noise
    noise = np.random.normal(0.5, sigma, depth_max)[..., np.newaxis]
    signals_noised['white'] = np.concatenate([signals_noised['white'], noise], axis = 1)
    results_noise['white'] = rpt.Binseg(model="rbf").fit(signals_noised['white']).predict(n_bkps=2)
    bkps_noises['white'].append(results_noise['white'])
    
    # Blue noise
    noise = blue_noise(depth_max)[..., np.newaxis]
    signals_noised['blue'] = np.concatenate([signals_noised['blue'], noise], axis = 1)
    results_noise['blue'] = rpt.Binseg(model="rbf").fit(signals_noised['blue']).predict(n_bkps=2)
    bkps_noises['blue'].append(results_noise['blue'])
    
    # Pink noise
    noise = pink_noise(depth_max)[..., np.newaxis]
    signals_noised['pink'] = np.concatenate([signals_noised['pink'], noise], axis = 1)
    results_noise['pink'] = rpt.Binseg(model="rbf").fit(signals_noised['pink']).predict(n_bkps=2)
    bkps_noises['pink'].append(results_noise['pink'])
    
    # Red noise
    noise = pink_noise(depth_max)[..., np.newaxis]
    signals_noised['red'] = np.concatenate([signals_noised['red'], noise], axis = 1)
    results_noise['red'] = rpt.Binseg(model="rbf").fit(signals_noised['red']).predict(n_bkps=2)
    bkps_noises['red'].append(results_noise['red'])
'''    
# For the first subplot, with a white noise
results_noises = rpt.Binseg(model="rbf").fit(signals_noised['white']).predict(n_bkps=2)
fig, axs = rpt.display(signals_noised['white'], bkps, results_noises)
fig.gca().invert_yaxis()
plt.show()
'''


letters = ['a) ', 'b) ', 'c) ', 'd) ', 'e) ', 'f) ', 'g) ', 'h) ']
offset = 0

fig, axs = plt.subplots(8, 1, sharex=True, figsize = (7, 18))

for idx, noise_type in enumerate(['white', 'blue', 'pink', 'red']):
    df = pd.DataFrame(bkps_noises[noise_type], columns = ['Upper boundary',\
                                                          'Lower boundary', 'Bottom']).iloc[:,:2]
    df = df - bkps[:2]
    
    axs[0 + offset].scatter(range(n_noisevars + 1), df['Upper boundary'])
    #axs[0].set_xlabel('Number of noise variables')
    axs[0 + offset].set_ylabel('Upper boundary (m)')
    axs[0 + offset].set_title(letters[offset] + noise_type.capitalize() +\
                              '  noise',  loc='left', fontsize = 12)
    
    axs[1 + offset].scatter(range(n_noisevars + 1), df['Lower boundary'])
    axs[1 + offset].set_ylabel('Lower boundary (m)')
    axs[1 + offset].set_title(letters[offset + 1] + noise_type.capitalize() +\
                              '  noise',  loc='left', fontsize = 12)
    
    offset += 2

axs[-1].set_xlabel('Number of noise variables')



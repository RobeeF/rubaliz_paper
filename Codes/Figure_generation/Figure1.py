# -*- coding: utf-8 -*-
"""
Created on Wed Dec 15 14:38:57 2021

@author: rfuchs
"""

import re
import os 
import json
import pandas as pd
import seaborn as sns
from rubaliz import rubaliz
from seabird.cnv import fCNV
import matplotlib.pyplot as plt

# Change it with your path
os.chdir('C:/Users/rfuchs/Documents/GitHub/rubaliz_paper/')

# Import campaigns metadata and importation settings
path = 'info_dicts.json'
with open(path, "r") as read_file:
    info_dicts = json.load(read_file)
 
cruise = 'MALINA'
station = '430'
info_dict = [d for d in info_dicts if (d['cruise_name'] == cruise)\
             & (d['station_name'] == station)][0]

# Define the columns to keep and their name to display
if info_dict['cruise_name'] == 'KN207-01':
    cols_aliases = ['Fluorescence', 'Oxygen', 'Salinity']
    cols_units = ['($a.u.$)', '($ml.l^{-1}$)', '']

else:
    cols_aliases = ['Fluorescence', 'Oxygen', 'Pot. temp.', 'Salinity', 'Density']
    cols_units = ['($a.u.$)', '($ml.l^{-1}$)', '($°C$)', '', '($kg.m^{-3}$)']

# Import the CTD data
ruba = rubaliz(info_dict)
dir_ = os.path.join('Data','ruptures', cruise, station)

signals = []

files = os.listdir(dir_)
files = [f for f in files if re.search(info_dict['files_format'], f)] # or .txt

for file in files:
    path = os.path.join(dir_, file)
    if info_dict['files_format'] in ['.txt', '.csv']:
        ctd_signal = pd.read_csv(path, sep  = info_dict['sep'], engine = 'python', header = 0) 
    elif info_dict['files_format'] == '.cnv':
        ctd_signal = fCNV(path).as_DataFrame()
        ctd_signal.loc[:, info_dict['pres_col']] = ctd_signal[info_dict['pres_col']].round(0)
        ctd_signal = ctd_signal.groupby(info_dict['pres_col']).first().reset_index()
    else:
        raise ValueError('Please enter a valid file_format: .txt, .csv, .cnv')

    try:
        ctd_signal = ctd_signal[[info_dict['pres_col']] + ruba.available_cols]
        signals.append(ctd_signal)
    except: 
        print(file, 'not taken into account')
        continue
    

# Import the ruptures 
rupt_path = os.path.join('Results', 'ruptures', 'zones.csv')
ruptures = pd.read_csv(rupt_path)
rpts = ruptures[(ruptures['cruise'] == cruise) &\
                (ruptures['station'] == station)][['Euphotic end',\
                            'Mesopelagic end']].values[0]
# Define the colors 
eupho_color = 'lightgray'
meso_color = 'slategrey'

# Malina is in uM and not in ml.l-1
ox_conv = {d['cruise_name']: 1 for d in info_dicts}
ox_conv['D341'] = 22.4 / 1000 
ox_conv['DY032'] = 22.4 / 1000 
ox_conv['KN207-01'] = 22.4 / 1000 
ox_conv['KN207-03'] = 22.4 / 1000
ox_conv['TONGA'] = 22.4 / 1000
ox_conv['MALINA'] = 1/1.4287
ox_conv['PEACETIME'] = 22.4 / 1000 

#============================================
# Generate the plots
#============================================

n_curves = 5
colors = sns.color_palette("colorblind", n_curves)
colors = dict(zip(['Fluorescence', 'Oxygen', 'Pot. temp.', 'Salinity', 'Density'], colors))


for signal in signals: 
    
    print(signal.shape)
    
    # More versatile wrapper
    fig, host = plt.subplots(figsize=(4,12)) # (width, height) in inches
        
    par1 = host.twiny()
    par2 = host.twiny()
    par3 = host.twiny()
    par4 = host.twiny()
     
    host.set_xlim(0, 2)
    host.set_ylim(0, 1300)
    par1.set_ylim(0, 1300)
    par2.set_ylim(1, 1300)
    par3.set_ylim(1, 1300)
    par4.set_ylim(1, 1300)
     
    par1.xaxis.set_label_position('bottom') 
    par1.xaxis.tick_bottom()
    par2.xaxis.set_label_position('bottom') 
    par2.xaxis.tick_bottom()
    par3.xaxis.set_label_position('bottom') 
    par3.xaxis.tick_bottom()
    par4.xaxis.set_label_position('bottom') 
    par4.xaxis.tick_bottom()
    
    
    p1, = host.plot(signal[ruba.available_cols[0]], signal[info_dict['pres_col']],    color = colors['Fluorescence'])
    p2, = par1.plot(signal[ruba.available_cols[1]] * ox_conv[cruise], signal[info_dict['pres_col']],    color=colors['Oxygen'])
    p3, = par2.plot(signal[ruba.available_cols[2]], signal[info_dict['pres_col']],    color=colors['Pot. temp.'])
    p4, = par3.plot(signal[ruba.available_cols[3]], signal[info_dict['pres_col']],    color=colors['Salinity'])
    p5, = par4.plot(signal[ruba.available_cols[4]], signal[info_dict['pres_col']],    color=colors['Density'])
    
    # right, left, top, bottom
    par1.spines['bottom'].set_position(('outward', 35))
    par2.spines['bottom'].set_position(('outward', 75))
    par3.spines['bottom'].set_position(('outward', 110))
    par4.spines['bottom'].set_position(('outward', 145))
    
    host.invert_yaxis()
    
    # Color the labels
    host.xaxis.label.set_color(p1.get_color())
    par1.xaxis.label.set_color(p2.get_color())
    par2.xaxis.label.set_color(p3.get_color())
    par3.xaxis.label.set_color(p4.get_color())
    par4.xaxis.label.set_color(p5.get_color())
    
    # Color the ticks
    host.tick_params(axis='x', colors = p1.get_color())
    par1.tick_params(axis='x', colors = p2.get_color())
    par2.tick_params(axis='x', colors = p3.get_color())
    par3.tick_params(axis='x', colors = p4.get_color())
    par4.tick_params(axis='x', colors = p5.get_color())
    
    # Define label aliases
    host.set_xlabel(cols_aliases[0] + ' ' + cols_units[0], fontsize = 11)
    par1.set_xlabel(cols_aliases[1] + ' ' + cols_units[1], fontsize = 11)
    par2.set_xlabel(cols_aliases[2] + ' ' + cols_units[2], fontsize = 11)
    par3.set_xlabel(cols_aliases[3] + ' ' + cols_units[3], fontsize = 11)
    par4.set_xlabel(cols_aliases[4] + ' ' + cols_units[4], fontsize = 11)
    
    host.axhspan(0, rpts[0], facecolor = eupho_color, alpha=0.3, label = 'Euphotic zone')
    host.axhspan(rpts[0], rpts[1], facecolor = meso_color, alpha=0.3, label = 'Mesopelagic zone')
    
    host.set_title(info_dict['station_name'], fontsize = 16) 
    
    # Adjust spacings w.r.t. figsize
    fig.tight_layout()
    plt.show()

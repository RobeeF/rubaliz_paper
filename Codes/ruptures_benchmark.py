# -*- coding: utf-8 -*-
"""
Created on Wed Sep 15 13:16:26 2021

@author: rfuchs
"""


import re
import os 
import numpy as np
import pandas as pd
from rubaliz.seabird import fCNV

# Change it with your path
os.chdir('C:/Users/rfuchs/Documents/GitHub/rubaliz_paper/')

res_folder = 'Results/'
benchmark = pd.DataFrame()

campaigns = os.listdir('Data/ruptures/')
file_regex = '(.+)\.[A-Za-z]+'

#==================================================
# Crawling through campaigns and stations
#==================================================

for campaign in campaigns:

    if campaign in ['KN207-01']:
        fluo_col = 'flECO-AFL'
        pres_col = 'PRES'
        temp_col = 'TEMP' 
        density_col = None
        cols = ['flECO-AFL', 'oxygen', 'PSAL']

    elif campaign == 'KN207-03':
        fluo_col = 'fluor' 
        pres_col = 'press'
        density_col = 'sigma_0'
        temp_col = 'temp'
        cols = ['fluor', 'O2', 'potemp', 'sal',  'sigma_0']    
        
    elif campaign == 'D341':
        fluo_col = 'fluor' 
        pres_col = 'press' 
        density_col = 'sigma0'
        temp_col = 'temp'
        cols = ['fluor', 'oxygen', 'potemp', 'salin', 'sigma0']
        
    elif campaign == 'MALINA':
        fluo_col = 'fluo' 
        pres_col = 'pres'  
        density_col = 'sigt'
        temp_col = 'temp'
        cols = ['fluo', 'o2', 'theta', 'sal', 'sigt'] # theta and sigt to check

    elif (campaign == 'PEACETIME') | (campaign == 'DY032'):
        fluo_col = 'flC'
        pres_col = 'PRES'
        density_col = 'sigma-�00'
        temp_col = 'TEMP'
        cols = ['flC', 'oxygen', 'potemperature', 'PSAL', 'sigma-�00']
        
    else:
        fluo_col = 'flC'
        pres_col = 'PRES'
        density_col = 'sigma-�00'
        temp_col = 'TEMP'
        cols = ['flC', 'sbox0Mm/Kg', 'potemperature', 'PSAL', 'sigma-�00']  
        
    par_col = 'PAR' if campaign == 'D341' else 'par'
    stations = os.listdir('Data/ruptures/' + campaign)
    
    for station in stations:
        print(campaign, station)
        
        folder = 'ruptures/' + campaign + '/' + station + '/'
        files = os.listdir('Data/' + folder)
        
        # Some CTDs are in .cnv format while others are in .csv
        if campaign in ['KN207-03', 'MALINA']:
            files = [file for file in files if re.search('.csv', file)]
            files = [file for file in files if not(re.search('.err', file))]
        elif campaign == 'D341':
            files = [file for file in files if re.search('.txt', file)]
        else:
            files = [file for file in files if re.search('.cnv', file)]

        flc_signals = []
        
        #==================================================
        # Delimiting the euphotic zone
        #==================================================
        
        #************************
        # Format the signal
        #************************
        
        # Storage definition
        euphotic_par_ends = []
        euphotic_par_ends_01 = []
        
        euphotic_mld_ends_temp = []
        euphotic_mld_ends_sigma = []
        
        ppz_ends = []
        
        for file in files:
            fname = 'Data/' + folder + file  
            
            # Some CTDs are in .cnv format while others are in .csv
            if campaign in ['KN207-03', 'D341', 'MALINA']:
                down = pd.read_csv(fname, sep  = ',', engine = 'python')           
            else:
                down = fCNV(fname).as_DataFrame()
                
            #**************************************
            # Resample on a one meter depth basis
            #**************************************
            
            # Drop upward profiles
            down = down.groupby(pres_col).first().reset_index()

            # If the the depth is not an integer 
            down[pres_col] = down[pres_col].round(0)
            #down = down.groupby(pres_col).mean()
            down = down.groupby(pres_col).first().reset_index()
            
            # If there are missing depths
            Xresampled = np.arange(down.index.min(), down.index.max() + 1)
            down = down.reindex(down.index.union(Xresampled)).interpolate().loc[Xresampled]
                        
            #************************
            # Get PAR data
            #************************
        
            # Compute the "classical" euphotic zone criterion = 1%/0.1% of surface PAR 
            if par_col in down.columns:
                par_data = down[[par_col]]

                # Compute the PAR at the surface and the depth of 1% surface PAR 
                # and 0.1% surface PAR             
                surface_par = par_data.loc[par_data.index.min()][par_col]
                p1 = (par_data > (surface_par / 100))
                p01 = (par_data > (surface_par / 1000))
                
                # Check if such a depth exist  
                if len(set(p1[par_col])) == 1: # == 1 if no depth takes the value 1% PAR
                    euphotic_par_ends.append(np.nan)
                else:
                    euphotic_par_ends.append(p1.idxmin()[par_col])

                if len(set(p01[par_col])) == 1:
                    euphotic_par_ends_01.append(np.nan)
                else:
                    euphotic_par_ends_01.append(p01.idxmin()[par_col])
                    
            else:
                print(file, 'no par signal, was recorded at night ?')
                pass

            #************************
            # Get MLD data
            #************************
            
            # Test if the colum exist
            if density_col in down.columns:

                surface_density = down.loc[down.index[0]][density_col]
                d125 = (down[density_col] - surface_density) > 0.125

                # Check if such a depth exist  
                if len(set(d125)) == 1: # == 1 if no depth takes the value 1% PAR
                    euphotic_mld_ends_sigma.append(np.nan)
                else:
                    euphotic_mld_ends_sigma.append(d125.idxmax())

            else:
                euphotic_mld_ends_sigma.append(np.nan)   
                
                            
            # Temperature based method
            if temp_col in down.columns:
                surface_temp = down.loc[down.index[0]][temp_col]
                t05 = (surface_temp - down[temp_col]) > 0.5
                
                # Check if such a depth exist  
                if len(set(t05)) == 1: 
                    euphotic_mld_ends_temp.append(np.nan)
                else:
                    euphotic_mld_ends_temp.append(t05.idxmax())
                                            
            else:
                euphotic_mld_ends_temp.append(np.nan)
            
            #************************
            # Get PPZ data
            #************************
            max_fluo_index = down[fluo_col].argmax()
            ppz_depth = down.loc[max_fluo_index:][fluo_col] > (down[fluo_col].max() / 10)
            
            # Check if such a depth exist (look for values after the max only) 
            if len(set(ppz_depth)) == 1: # == 1 if no depth takes the value 1% PAR
                ppz_ends.append(np.nan)
            else:
                ppz_ends.append(ppz_depth.idxmin())
            
        #*************************************
        # Wrap all signals together
        #*************************************
        
        # PAR signal handling
        euphotic_par_end = np.nanmean(euphotic_par_ends)
        euphotic_par_end_01 = np.nanmean(euphotic_par_ends_01)
            
        # MLD signal handling
        euphotic_mld_end_temp = np.nanmean(euphotic_mld_ends_temp)
        euphotic_mld_end_sigma = np.nanmean(euphotic_mld_ends_sigma) 
 
        # PPZ signal handling
        ppz_end = np.nanmean(ppz_ends) 
        
        ind_benchmark = pd.DataFrame.from_dict({'cruise': campaign, 'station': station,\
                                  '1% PAR': round(euphotic_par_end, 0),\
                                  '0.1% PAR': round(euphotic_par_end_01, 0),\
                                  'MLD temp': round(euphotic_mld_end_temp, 0),\
                                  'MLD sigma': round(euphotic_mld_end_sigma, 0),\
                                  'PPZ': round(ppz_end, 0),\
                                  }, orient = 'index').T
            
        benchmark = pd.concat([benchmark, ind_benchmark])
        
#==================================================
# Store the determined zones
#==================================================

benchmark = benchmark[['cruise', 'station', '1% PAR', '0.1% PAR',\
               'MLD temp', 'MLD sigma', 'PPZ']]
    
path = os.path.join(res_folder, 'ruptures', 'benchmark.csv')
benchmark.to_csv(path, index = False)
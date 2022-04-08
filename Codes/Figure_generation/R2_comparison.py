# -*- coding: utf-8 -*-
"""
Created on Wed Mar  9 19:07:22 2022

@author: rfuchs
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

os.chdir('C:/Users/rfuchs/Documents/GitHub/rubaliz_paper/')

r2 = pd.read_csv('Results/integration/oldR2_newR2.csv')
r2['Old R2'] = r2['Old R2'].round(2)

fig, ax = plt.subplots(1, 1, figsize = (5, 5))
x = np.linspace(0,1, 50)
ax.scatter(r2['Old R2'], r2['R2'], label = 'power law vs. spline regression $R^2$')
ax.plot(x,x, color = 'red', label = 'y=x')
ax.set_xlabel('$R^2$ from power law regressions')
ax.set_ylabel('$R^2$ from spline regressions')
plt.legend()

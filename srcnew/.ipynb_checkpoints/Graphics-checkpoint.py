#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 15:45:31

@author: JM-RPC
"""    

#import pdb; pdb.set_trace()
import tkinter as tk
from sklearn.metrics import roc_curve, auc
import statsmodels.api  as sm
import statsmodels.formula.api as smf
from statsmodels.graphics.regressionplots import plot_partregress_grid, plot_leverage_resid2, influence_plot, plot_fit
from scipy import stats
import numpy as np
import pandas as pd
import io
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sb
from mpl_toolkits.mplot3d import Axes3D
#from shiny import App, Inputs, Outputs, Session, reactive, render, ui
#from shiny.types import FileInfo
#import shinywidgets
#from shinywidgets import render_widget, output_widget
#import plotly.graph_objs as go
#import plotly.express as pltx
import os
import signal
from datetime import datetime    

from Regression import imdl

LOGSTR = ''

def pushlog(msgstr):
    global LOGSTR
    LOGSTR = LOGSTR + '\n' + msgstr
    
    
basecolors0 = ['blue', 'red',  'green', 'yellow', 'magenta', 'cyan', 'violet',
               'orange',  'goldenrod', 'grey', 'gold', 'silver', 'orangered', 'darkolivegreen',
               'olive', 'khaki', 'thistle', 'lightsteelblue', 'slateblue', 'black', 'darkviolet',
               'brown', 'indigo', 'hotpink', 'lavender']

basecolorsalpha = ['red',  'blue', 'green', 'goldenrod', 'violet','cyan', 'yellow','grey','gold','magenta']
basecolors = [matplotlib.colors.to_rgba(item,alpha = None) for item in basecolorsalpha]
protected_names = ['Residuals','Predictions','Deviance_Resid']

def getcolor(cvar, col_data):
    dfc = pd.DataFrame(col_data)
    choicesCo = list(dfc[dfc.columns[0]].unique())
    choicesCo.sort()
    if (len(choicesCo) < len(basecolors0)):
        colorD = {item : basecolors0[choicesCo.index(item)]  for item in choicesCo}
        colorlist = [colorD[item] for item in col_data]
        lpatches = [mpatches.Patch(color = colorD[item],label = cvar + ', ' + str(item)) for item in colorD.keys()]
    else:
        cmap = plt.cm.plasma
        colorD = {item : cmap(choicesCo.index(item)/len(choicesCo)) for item in choicesCo}
        colorlist = [colorD[item] for item in col_data]
        lpatches = [mpatches.Patch(color = colorD[item],label = cvar +  ', ' + str(item)) for item in choicesCo]
    return colorD, colorlist, lpatches

    
def getcolorM(col_data):
    dfc = col_data.astype('str')
    choicesCo = list(dfc.unique())
    choicesCo.sort()
    if (len(choicesCo) < len(basecolors0)):
        colorD = {item: basecolors0[choicesCo.index(item)] for item in choicesCo}
        cvar = dfc.map(colorD)
    else: 
        cvar = ['black']*len(dfc)
        colorD = {}
    return(cvar,colorD)     


def doTrend():
    dfg = imdl.fitdata
    cur_mdl = imdl.modelres
    yv = imdl.depvar
    #print(f"from doTrend indvars = {imdl.indvars}")
    if len(imdl.indvars) == 1:
        xv = list(imdl.indvars)[0]
        yv = imdl.depvar
        zv = '-'
    elif len(imdl.indvars) == 2:
        xv = list(imdl.indvars)[0]
        yv = list(imdl.indvars)[1]
        zv = imdl.depvar
    else:
        return
    #res = imdl.modelres
    MTYPE = imdl.model_type
    #fig2 = plt.figure(figsize = (8,8))
    #fig3 = imdl.fig3
    #ax2 = imdl.ax2
    #ax3 = imdl.ax3
    #set up the input data for the independent variables
    sq = 0.00
    gridcount = 25
    if (xv != '-'):
        deltax = dfg[xv].max() - dfg[xv].min()
        xlo = dfg[xv].min() - sq*deltax
        xup = dfg[xv].max() + sq*deltax
    if (yv != '-'): 
        deltay = dfg[yv].max() - dfg[yv].min()
        ylo = dfg[yv].min() - sq*deltay
        yup = dfg[yv].max() + sq*deltay
    if (zv != '-'): #We are doing 3D
        xvar, yvar = np.meshgrid(np.arange(xlo,xup,deltax/gridcount),np.arange(ylo, yup,deltay/gridcount))                
        exog0 = pd.DataFrame({xv: xvar.ravel(), yv: yvar.ravel()}) 
    else: #we are doing 2D
        xvar = np.arange(xlo, xup, deltax/gridcount) 
        yvar = []                      
        exog0 = pd.DataFrame({xv : xvar})
    #print(f"exog0 = {exog0.head()}")
    res = imdl.modelres
    #print(f"Current model: {cur_mdl.summary()}")
    MTYPE = imdl.model_type
    #res_predictions =cur_mdl.get_prediction(exog=exog0,transform = True)
    #res_frame = res_predictions.summary_frame(alpha = imdl.sig_level)
      
    try:
       res_predictions =cur_mdl.get_prediction(exog=exog0,transform = True)
       res_frame = res_predictions.summary_frame(alpha = imdl.sig_level)
    except Exception as er:
        #print(f"...Predictions failed! {er}")
        return [],[],[],[],[],[],[]
   
    znew = res_frame['mean'].values.reshape(xvar.shape)    
    Ci_lb1 =  res_frame['mean_ci_lower'].values.reshape(xvar.shape)
    Ci_ub1 =  res_frame['mean_ci_upper'].values.reshape(xvar.shape)
    if (MTYPE == 'OLS'):
        Pi_lb1 =  res_frame['obs_ci_lower'].values.reshape(xvar.shape)
        Pi_ub1 =  res_frame['obs_ci_upper'].values.reshape(xvar.shape)
    else:
        Pi_lb1 = []
        Pi_ub1 = []
    return xvar, yvar, znew, Ci_lb1, Ci_ub1, Pi_lb1, Pi_ub1
   
  
   

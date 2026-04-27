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

#from Regression import imdl

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

def doTrend(res, depvar, indvars, MTYPE = '-'):
    #calculates the data for plotting the fitted regression line 
    # or plane and confidence intervals for a model. 
    # Returns xvar, yvar, znew, Ci_lb1, Ci_ub1, Pi_lb1, Pi_ub1
    fitdata = res.model.data.frame[[depvar] + indvars]
    dfg = fitdata
    cur_mdl = res
    yv = depvar
    #print(f"from doTrend indvars = {imdl.indvars}")
    if len(indvars) == 1:
        xv = list(indvars)[0]
        yv = depvar
        zv = '-'
    elif len(indvars) == 2:
        xv = list(indvars)[0]
        yv = list(indvars)[1]
        zv = depvar
    else:
        return
    
    #MTYPE = imdl.model_type
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

    #print(f"Current model: {cur_mdl.summary()}")
    #MTYPE = imdl.model_type
      
    try:
       res_predictions =cur_mdl.get_prediction(exog=exog0,transform = True)
       res_frame = res_predictions.summary_frame(alpha = 0.05)
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

   
##########################  
#Model Graphics Functions    
##########################  
def doroc(MODEL = None):
    if (MODEL is None): return
    prediction_res = MODEL.get_prediction(transform = True)
    res_frame= prediction_res.summary_frame(alpha = 0.05)

    fpr, tpr, thresholds = roc_curve(MODEL.model.endog, res_frame['mean']) 
    roc_auc = auc(fpr, tpr)
    fig = plt.figure(figsize = (8,8))
    ax = fig.add_subplot()
    ax.plot(fpr, tpr)
    ax.plot([0, 1], [0, 1], 'k--')
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.set_title(f"ROC: {MODEL.model.formula}, AUC={round(roc_auc,5)}")
    fig.show()  #show the plots simultaneously
    #plt.show() #show plots one at a time
    return


def dopredict(res = None, xname = None, colorvar = '-', dsize = 8.0 ):
    if res is None: return
    if xname == '-' or xname == '': return  
    tstr = res.model.formula
    depvar = res.model.endog
    dsize = 8.0
    prediction_res = res.get_prediction(transform = True)
    res_frame= prediction_res.summary_frame(alpha = 0.05)
    ylabstr = "Est. Mean Response"
    fig, ax = plt.subplots() 
    if colorvar == '-' or colorvar == '':
        sb.scatterplot(ax = ax, x = res.model.data.frame[xname], y = res_frame['mean'], color = 'blue',label = 'Observed', s= dsize)
    else:
        sb.scatterplot(ax = ax, x = res.model.data.frame[xname], y = res_frame['mean'], hue = res.model.data.frame[colorvar], palette = 'bright', s= dsize)
    #plt.ylim((0, 1))
    plt.ylabel(ylabstr)
    plt.xlabel(xname)
    plt.title(tstr)
    fig.show()  #show the plots simultaneously
    #plt.show() #show plots one at a time
    return

def showFit(res = None, xname = None, colorvar = '-', dsize = 8.0 ):
    if xname is None: return
    xvdependent = xname
    if (xvdependent == '') or (xvdependent == '-'): return       
    dsizenu = float(dsize)/20.0
    fig, ax = plt.subplots()
    plot_fit(res, xvdependent, vlines = False, ax = ax, markersize=dsizenu)
    for line in ax.lines:
        if line.get_linestyle() == 'None' and line.get_marker() != 'None': # Identify scatter plot
            line.set_markersize(dsizenu) # Set desired marker size

    #plt.ylabel(ylabstr)
    plt.show()
    return


def doresidual(res = None, mtype = 'OLS', xname = None, cvresid = None, dsize = 8.0):
    if res == None: return
    tstr = res.model.formula
    #xvresidlist = list(res.model.exog_names)
    #xname is the x variable for the residual plot.  
    # If it's not given, then the residuals will be 
    # plotted against the predicted values.
    if mtype != 'OLS': #if it's not OLS it's GLM
        vres = res.resid_deviance
        ylabstr = 'Deviance Residual'
    else:
        vres = res.resid
        ylabstr = 'Residual'
    residlim = max(np.abs(vres))
    fig, ax = plt.subplots()
    if xname is None:
        prediction_res = res.get_prediction(transform = True)
        res_frame= prediction_res.summary_frame(alpha = 0.05)
        if cvresid == None or cvresid == '-':           
            sb.scatterplot(ax=ax, x = res_frame['mean'], y = vres, color = 'blue', s = dsize)
        else:
            sb.scatterplot(ax=ax, x = res_frame['mean'], y = vres, hue = res.model.data.frame[cvresid], palette = 'bright', s = dsize)
        plt.xlabel('Predicted ' + res.model.endog_names)
    else:
        fig, ax = plt.subplots()
        if cvresid == None or cvresid == '-':
            sb.scatterplot(ax=ax, x = res.model.data.frame[xname], y = vres, color = 'blue', s = dsize)
        else:
            sb.scatterplot(ax=ax, x = res.model.data.frame[xname], y = vres, hue = res.model.data.frame[cvresid], palette = 'bright', s = dsize)
        plt.xlabel(xname)
    plt.axhline(y=0, color='black', linestyle='-')
    plt.ylim((-residlim, residlim))
    plt.ylabel(ylabstr)

    plt.title(tstr)
    fig.show()  #show the plots simultaneously
        #plt.show() #show plots one at a time
    return

#############################
#############################


def modelplot(res, depvar = None, indvars=None, color_var = '-', showCI = 'False', showPI = 'False', MTYPE = '-'):
    if depvar is None: return
    if indvars is None: return  
    fitdata = res.model.data.frame
    if len(indvars) == 1:
        xv = list(indvars)[0]
        yv = '-'
        zv = depvar
    elif len(indvars) == 2:
        xv = list(indvars)[0]
        yv = list(indvars)[1]
        zv = depvar
    else:   
        return
    xvar, yvar, znew, Ci_lb1, Ci_ub1, Pi_lb1, Pi_ub1 = doTrend(res, depvar, indvars, MTYPE = MTYPE)
    dsize = 8.0
    if len(indvars)==1:
        fig = plt.figure(figsize = (8,8)) 
        ax = fig.add_subplot()
        xv = list(indvars)[0]
        zv = depvar
        cv = color_var
        if cv == '-':
            sb.scatterplot(fitdata, x = xv, y = zv, ax = ax,s = dsize, color = 'black')
        else:
            sb.scatterplot(fitdata, x = xv, y= zv, ax = ax, s = dsize, hue = cv, palette = 'bright' )
        dftemp = pd.DataFrame({xv:xvar, zv:znew})

        sb.lineplot(dftemp, x = xv, y = zv, ax = ax, color = 'red', linewidth = dsize/2)
        if showCI == 'True':
            sb.lineplot(dftemp, x = xv, y = Ci_lb1, ax = ax, color = 'green', linewidth = dsize/2)
            sb.lineplot(dftemp, x = xv, y = Ci_ub1, ax = ax, color = 'green', linewidth = dsize/2)
        if showPI == 'True' and MTYPE == 'OLS':
            sb.lineplot(dftemp, x = xv, y = Pi_lb1, ax = ax, color = 'cyan', linewidth = dsize/2)
            sb.lineplot(dftemp, x = xv, y = Pi_ub1, ax = ax, color = 'cyan', linewidth = dsize/2)
        plt.xlabel(xv)
        plt.ylabel(zv)
        plt.title(res.model.formula)
        fig.show()
    elif len(indvars) == 2:
        fig = plt.figure(figsize = (8,8))
        ax = fig.add_subplot(111, projection='3d')
        xv = list(indvars)[0]
        yv = list(indvars)[1]
        zv = depvar
        cv = '-'
        xdat = fitdata[xv]
        ydat = fitdata[yv]
        zdat = fitdata[zv]
        ax.set_xlabel(xv)
        ax.set_ylabel(yv)
        ax.set_zlabel(zv)
        if (cv == '-') or (cv == ''):
            ax.scatter(xdat, ydat, zdat ,marker='o', color = 'black', s = dsize)
        else:
            colordat = fitdata[cv]
            colorD, colorlist ,lpatches= getcolor(cv,list(colordat))
            ax.scatter(xdat, ydat, zdat ,marker='o', c = colorlist, s = dsize)
            if colorD != {}:
                handles , labels = ax.get_legend_handles_labels()
                handles.extend(lpatches)
                ax.legend(handles = handles)
        
        ax.plot_surface(xvar,yvar,znew, alpha = 0.8, color = 'cyan', edgecolor = 'grey') 
        if showCI:    
            ax.plot_surface(xvar,yvar,Ci_ub1, alpha = 0.4, color ='goldenrod', edgecolor = 'grey')
            ax.plot_surface(xvar,yvar,Ci_lb1, alpha = 0.4, color ='goldenrod', edgecolor = 'grey')            
        if showPI and MTYPE == 'OLS':
            ax.plot_surface(xvar,yvar,Pi_ub1, alpha = 0.2, color = 'magenta', edgecolor = 'grey')                
            ax.plot_surface(xvar,yvar,Pi_lb1, alpha = 0.2, color = 'magenta', edgecolor = 'grey')                
        fig.show()
    else:
        return
    return

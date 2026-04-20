#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  6 16:36:46 2025

@author: John
"""
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sb
from mpl_toolkits.mplot3d import Axes3D


import functools

#####################Code generation preamble

codepreamble = """
import pandas as pd
from pandas.api.types import is_numeric_dtype
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
matplotlib.use('TkAgg')
import numpy as np
import statsmodels.api  as sm
import statsmodels.formula.api as smf 
from statsmodels.graphics.regressionplots import plot_partregress_grid, plot_leverage_resid2, influence_plot, plot_fit
from patsy import dmatrices, dmatrix, NAAction
import seaborn as sb
from sklearn.metrics import roc_curve, auc


basecolors0 = ['blue', 'red',  'green', 'yellow', 'magenta', 'cyan', 'violet',
               'orange',  'goldenrod', 'grey', 'gold', 'silver', 'orangered', 'darkolivegreen',
               'olive', 'khaki', 'thistle', 'lightsteelblue', 'slateblue', 'black', 'darkviolet',
               'brown', 'indigo', 'hotpink', 'lavender']


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

#############################
### Model Plotting Functions
#############################


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

def dopredictbin(res = None):
    if res is None: return
    xvpredictlist = list(res.model.exog_names)
    cvpredict = res.model.endog
    tstr = res.model.formula
    dsize = 8.0
    prediction_res = res.get_prediction(transform = True)
    res_frame= prediction_res.summary_frame(alpha = 0.05)
    ylabstr = "Est. Mean Response"
 
    for idx,xvpredict in enumerate(xvpredictlist):
        if idx == 0: continue
        fig, ax = plt.subplots() 
        sb.scatterplot(ax= ax, x = res.model.exog[:,idx], y = res_frame['mean'], hue = res.model.endog, palette = 'bright',s = dsize)
        plt.axhline(y=0, color='black', linestyle='-')
        plt.axhline(y=0.2, color = 'black', linestyle = 'dashed',linewidth = 0.5)
        plt.axhline(y=0.4, color = 'black', linestyle = 'dashed',linewidth = 0.5)
        plt.axhline(y=0.5, color = 'black', linestyle = 'solid',linewidth = 0.5)
        plt.axhline(y=0.6, color = 'black', linestyle = 'dashed',linewidth = 0.5)
        plt.axhline(y=0.8, color = 'black', linestyle = 'dashed',linewidth = 0.5)
        plt.axhline(y=1.0, color = 'black', linestyle = '-',linewidth = 0.5)
        plt.ylim((0, 1))
        plt.ylabel(ylabstr)
        plt.xlabel(xvpredict)
        plt.title(tstr)
        fig.show()  #show the plots simultaneously
        #plt.show() #show plots one at a time
    return

def dopredict(res = None):
    if res is None: return
    xvpredictlist = list(res.model.exog_names)
    tstr = res.model.formula
    depvar = res.model.endog
    dsize = 8.0
    prediction_res = res.get_prediction(transform = True)
    res_frame= prediction_res.summary_frame(alpha = 0.05)
    ylabstr = "Est. Mean Response"
    for idx,xvpredict in enumerate(xvpredictlist):
        if idx == 0: continue
        fig, ax = plt.subplots() 
        sb.scatterplot(ax = ax, x = res.model.exog[:,idx], y = depvar, color = 'blue',label = 'Observed', s= dsize)
        sb.scatterplot(ax = ax, x = res.model.exog[:,idx], y = res_frame['mean'], color = 'red',label = 'Predicted', s = dsize)
        #plt.ylim((0, 1))
        plt.ylabel(ylabstr)
        plt.xlabel(xvpredict)
        plt.title(tstr)
        fig.show()  #show the plots simultaneously
        #plt.show() #show plots one at a time
    return

def doresidual(res = None, mtype = 'OLS'):
    if res == None: return
    tstr = res.model.formula
    xvresidlist = list(res.model.exog_names)
    dsize = 8 #dot size
    if mtype != 'OLS': #if it's not OLS it's GLM
        vres = res.resid_deviance
        ylabstr = 'Deviance Residual'
    else:
        vres = res.resid
        ylabstr = 'Residual'
    residlim = max(np.abs(vres))
    for idx, xvresid in enumerate(xvresidlist):
        fig, ax = plt.subplots()
        if idx == 0 :
            prediction_res = res.get_prediction(transform = True)
            res_frame= prediction_res.summary_frame(alpha = 0.05)            
            sb.scatterplot(ax=ax, x = res_frame['mean'], y = vres, color = 'blue', s = dsize)
            plt.xlabel('Predicted ' + res.model.endog_names)
        else:
            sb.scatterplot(ax=ax, x = res.model.exog[:,idx], y = vres, color = 'blue', s = dsize) 
            plt.xlabel(xvresid)
        plt.axhline(y=0, color='black', linestyle='-')
        plt.ylim((-residlim, residlim))
        plt.ylabel(ylabstr)

        plt.title(tstr)
        fig.show()  #show the plots simultaneously
        #plt.show() #show plots one at a time
    return

#############################
#############################


"""

codepostamble = """
while True:
    user_input = input("Enter 'q' to quit: ")
    if user_input.lower() == 'q':
        print("Quitting app...")
        sys.exit(0) # Graceful exit

"""
#######Global Data Structures######

class globalData():
    def __init__(self, data_in=pd.DataFrame()):
        self.data = data_in.copy(deep=True)
        #self.data0 = data_in.copy(deep = True)
        self.fpath = ''
        self.model_res = None
        self.model_data = None
        self.datatable = None
        self.logstr = ''
        self.codestr = ''
        #self.x2 = 0
        #self.x3 = 0
        
    def reset_Data(self, nupath = '', data_in = pd.DataFrame()):
        #reset the globalData object to contain the data set in data_in
        #data = the working data set
        self.data = data_in.copy(deep=True)
        self.fpath = nupath
        self.datatable = None
        return
    
    def put_Data(self, data_in=pd.DataFrame()):
        #Saves a changed (via new variables or filtering) into the working data set
        self.data = data_in.copy(deep=True)
        return

    def get_Data(self):
        #gets the working data set
        return (self.data)

    def show_Data(self):
        if len(self.data) > 0:
            self.data.head(10)
        return
            
    def restore_Data(self):  #deprecated
        #restores the working data set from the global data set.
        return(self.data)
    
    def log_It(self, msg = ''):
        self.logstr += "\n" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + msg
        return
        
    def log_Init(self):
        self.logstr = "\n" + str(datetime.now()) + ": Session Init"
        return
        
    def log_Get(self):
        return(self.logstr + '\n')
    
    def code_It(self, msg = ''):
        self.codestr = self.codestr + msg + '\n'
        return
        
    def code_Get(self):
    
        return(codepreamble + self.codestr + codepostamble)
    
    def code_Init(self):
        self.codestr = "# " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' Code: \n'
        return
        
    
gdata = globalData()




#alpha test code create decorator function to log function arguments --currently not used

def log_function_call(func):
    """Decorator to log function calls and their arguments."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Log the function call details before execution
        nuargsp = []
        nuargsk = []
        if len(args) != 0:
            nuargsp = [str(item) for item in args]
        if len(kwargs.keys()) != 0:
            nuargsk = [item + '=' +  str(kwargs[item]) for item in list(kwargs.keys())]
            #print(nuargsk)
        nuargs = nuargsp + nuargsk
        nuargs_str = ", ".join(nuargs)
        #print(nuargs)
        lmsg = f"{func.__name__}({nuargs_str}) \n"
        print(lmsg)
        gdata.code_It(lmsg)
        #print(logstr)
        result = func(*args, **kwargs)
        return result
        # Log the result after execution
    return wrapper

@log_function_call 
def sb_scatterplotJM(*args, **kwargs):
    return(sb.scatterplot(*args, **kwargs))

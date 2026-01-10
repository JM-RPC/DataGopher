#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 15:45:31

@author: JM-RPC
"""
#import pdb; pdb.set_trace()
#import tkinter as tk
from tkinter import messagebox

#from sklearn.metrics import roc_curve, auc
import statsmodels.api  as sm
import statsmodels.formula.api as smf
#from statsmodels.genmod import families

#from statsmodels.graphics.regressionplots import plot_partregress_grid, plot_leverage_resid2, influence_plot, plot_fit
#from scipy import stats
#import numpy as np
import pandas as pd
#import io
#import matplotlib
#import matplotlib.pyplot as plt
#import matplotlib.patches as mpatches
#import seaborn as sb
#from mpl_toolkits.mplot3d import Axes3D
#from shiny import App, Inputs, Outputs, Session, reactive, render, ui
#from shiny.types import FileInfo
#import shinywidgets
#from shinywidgets import render_widget, output_widget
#import plotly.graph_objs as go
#import plotly.express as pltx
#import os
#import signal
from datetime import datetime
#from shinywidgets import output_widget, render_widget
    


class modelData:

    def __init__(self):
        self.inputdata = None
        self.model_vars = None
        self.fname = None
        self.indvars = set([])
        self.depvar = ''
        self.model_string = '~'
        self.model_type = 'OLS'
        self.sig_level = 0.05
        self.overdispersion = 1.0
        self.fitdata = None
        self.modelres = None
        self.link = ''
        #graphics = None
        #self.gphax2d = None
        #self.gphFig3d = None
        #self.gphax3d = None
        #self.gphx = '-'
        #self.gphy = '-'
        #self.gphz = '-'
        #self.gphc = '-'
        #self.gphw1 = '-'
        #self.gphw2 = '-'
        #self.gphw3 = '-'
        #self.gphw4 = '-'
        #self.gphw5 = '-'
        #self.gphw6 = '-'
        #self.xlower = None
        #self.xupper = None
        #self.ylower = None
        #self.yupper = None
        self.addPredictions = '-'
        self.LOGSTR = ''
        
    def pushlog(self, msg): 
        self.LOGSTR = self.LOGSTR + '\n' + msg
        
    def clearlog(self):
        self.LOGSTR = ''
        
    def modelData_Clear(self):
        self.inputdata = None
        self.model_vars = None
        self.fname = None
        self.indvars = set([])
        self.depvar = ''
        self.model_string = '~'
        self.model_type = 'OLS'
        self.sig_level = 0.05
        self.overdispersion = 1.0
        self.link = None
        self.fitdata = None
        self.modelres = None
        self.addPredictions = '-'
        self.LOGSTR = ''
        

        
imdl = modelData()



LOGSTR = ''

"""
fileGetWindow = dr.fileBrowsePreview()
df = fileGetWindow.df
filename = fileGetWindow.iodata.filepath
print(">>>>>>>>>File name from getData: ", filename)
print(f">>>>>>>>>Columns: {",".join(list(df.columns))}")

"""



#def runModel(DATA = pd.DataFrame(), MODEL_STRING = '', DEPVAR = '', INDVAR = [],MODEL_TYPE = 'OLS'):
def goModel():
    df = imdl.inputdata.copy(deep = True)
    if (('Predictions' in list(df.columns)) |  ('Residuals' in list(df.columns)) | 
            ('CI_lb' in list(df.columns)) | ('CI_ub' in list(df.columns)) | 
            ('PI_lb' in list(df.columns)) |('PI_ub' in list(df.columns))):
        bmsg = "One of the names: Predictions, Residuals, CI_lb, CI_up, PI_lb, PI_ub conflicts "
        bmsg += "with one or more variable names. Variables with conflicting names will be overwritten"
        bmsg += "\nFor best results, please change the relevant variable names before running the model.  Continue?"
        if not messagebox.askokcancel("Warning:",bmsg):
            return
    
    MODEL_STRING = imdl.model_string
    DEPVAR = imdl.depvar
    INDVAR = imdl.indvars
    MODEL_TYPE = imdl.model_type
    MODEL_LINK = imdl.link

    if (DEPVAR == ''): 
        return

    size0 = len(df)


    imdl.pushlog(f"runModel:: Dependent Var: {DEPVAR}, Independent Var: {','.join(INDVAR)}, \n...Model: {MODEL_STRING}")
    
    #manually remove rows containing NaNs in the dependent or independent variables columns
    df.dropna(subset = [DEPVAR] + list(INDVAR),inplace = True)   
    size2 = len(df)  
    imdl.pushlog(f"...Data size: {size0}, fitted data size: {size2}, {size0-size2} rows deleted due to missing data.")
    imdl.pushlog(f"...Model type = {MODEL_TYPE}  link: {MODEL_LINK}")
        
    #minimal sanity check: a) dependent variable can't be constant b) if LOGIT has been chosen, dependent variable must be binary (0 or 1)
    outcomes = list(df[DEPVAR].unique())
    ISINT = False
    if df[DEPVAR].dtype == 'int':
        ISINT = True
    elif df[DEPVAR].dtype == 'float':
        if (df[DEPVAR].apply(float.is_integer).all()):
            ISINT = True
        else:
            ISINT = False
    else: 
        ISINT = False
    imdl.pushlog(f"...Dependent variable type: {df[DEPVAR].dtype}")
    no_outcomes = len(outcomes)
    if (no_outcomes <=1):
        imdl.pushlog("The dependent variable is a constant.  I'm confused.  Please check and try again.")
        #print(LOGSTR)
        return (None, None, imdl.LOGSTR)
    STOP = False
    #choose and solve a model
    if (MODEL_TYPE == 'LOGIT'):
        if set([0,1]) == set(outcomes) :
            try:
                #res = smf.logit(formula = input.stringM(), data=df).fit()
                res = smf.glm(formula = MODEL_STRING, data = df, family=sm.families.Binomial(link=sm.families.links.Logit())).fit()
            except: 
                STOP = True
        else:
            imdl.pushlog("...Logistic Regression Error: dependent variable not binary 0,1.")
            #print(LOGSTR)
            return (None, None, imdl.LOGSTR)
    elif (MODEL_TYPE == 'PROBIT'):
        if set([0,1]) == set(outcomes) :
            try:
                #res = smf.logit(formula = input.stringM(), data=df).fit()
                res = smf.glm(formula = MODEL_STRING, data = df, family=sm.families.Binomial(link=sm.families.links.Probit())).fit()
            except: 
                STOP = True
        else:
            imdl.pushlog("...Probit ModelError: dependent variable not binary 0,1.")
            #print(LOGSTR)
            return (None, None, imdl.LOGSTR)
    elif (MODEL_TYPE == 'GAMMA'):
        if min(outcomes) >= 0.0 :
            try:
                if MODEL_LINK == "InversePower":
                    res = smf.glm(formula = MODEL_STRING, data = df, family=sm.families.Gamma(link = sm.families.links.InversePower())).fit()
                elif MODEL_LINK == "Log":
                    res = smf.glm(formula = MODEL_STRING, data = df, family=sm.families.Gamma(link = sm.families.links.Log())).fit()
                elif MODEL_LINK == "Identity":
                    res = smf.glm(formula = MODEL_STRING, data = df, family=sm.families.Gamma(link = sm.families.links.Identity())).fit()
                else:
                    res = smf.glm(formula = MODEL_STRING, data = df, family=sm.families.Gamma()).fit()
            except Exception as er: 
                imdl.pushlog(f" Gamma failed: {str(er)}")
                STOP = True
        else:
            imdl.pushlog("...Gamma Model Error: dependent variable takes on negative values.")
            #print(LOGSTR)
            return (None, None, imdl.LOGSTR)
    elif (MODEL_TYPE == 'OLS'):
        try:
            res = smf.ols(formula=MODEL_STRING, data=df).fit()
        except Exception as er:
            messagebox.showerror(' ',f"OLS fit failed. error: {str(er)}")
            STOP = True            
    elif (MODEL_TYPE== 'POISSON') & (min(outcomes) >=0):
        if (min(outcomes) >= 0) & ISINT:
            try:
                imdl.pushlog(f" ...Estimating model: ISINT= {ISINT}, min outcome = {min(outcomes)}")
                if MODEL_LINK == "Log":
                    res = smf.glm(formula = MODEL_STRING, data=df, family = sm.families.Poisson(link = sm.families.links.Log())).fit()
                elif MODEL_LINK == "Identity":
                    res = smf.glm(formula = MODEL_STRING, data=df, family = sm.families.Poisson(link = sm.families.links.Identity())).fit()
                elif MODEL_LINK == "Sqrt":
                    res = smf.glm(formula = MODEL_STRING, data=df, family = sm.families.Poisson(link = sm.families.links.Sqrt())).fit()
                else:
                    res = smf.glm(formula = MODEL_STRING, data=df, family = sm.families.Poisson()).fit()                    
            except: 
                STOP = True            
        else:
            imdl.pushlog("...Poisson Regression Error: dependent variables are not non-negative integers.")
            #print(LOGSTR)
            return (None, None, imdl.LOGSTR)
    elif (MODEL_TYPE == 'NEGATIVE BINOMIAL') & (min(outcomes) >=0):
        if (min(outcomes) >= 0) & ISINT:
            try:
                imdl.pushlog(f" ...Estimating model: ISINT= {ISINT}, min outcome = {min(outcomes)}")
                if MODEL_LINK == "Log":
                    res = smf.glm(formula=MODEL_STRING, data=df, family = sm.families.NegativeBinomial(alpha = imdl.overdispersion,link = sm.families.links.Log())).fit()
                elif MODEL_LINK == "Identity":
                    res = smf.glm(formula=MODEL_STRING, data=df, family = sm.families.NegativeBinomial(alpha = imdl.overdispersion,link = sm.families.links.Identity())).fit()
                elif MODEL_LINK == "Sqrt":
                    res = smf.glm(formula=MODEL_STRING, data=df, family = sm.families.NegativeBinomial(alpha = imdl.overdispersion,link = sm.families.links.Sqrt())).fit()
                else:
                    res = smf.glm(formula=MODEL_STRING, data=df, family = sm.families.NegativeBinomial()).fit()            
            except Exception as er:
                imdl.pushlog(f"Negative Binomial Fit Failed. Error: {er}")
                STOP = True            
        else:
            imdl.pushlog("...Negative Binomial Regression Error: dependent variables are not non-negative integers.")
            #print(LOGSTR)
            return (None, None, imdl.LOGSTR)
    else:
        STOP = True
        imdl.pushlog("No model or inappropriate model chosen. Choose OLS, GAMMA, LOGIT, POISSON, or NEGATIVE BINOMIAL")
    if STOP:
        #print(LOGSTR)
        return (None, None, imdl.LOGSTR)
    # regression succeeded           
    mdl_d = pd.concat([res.model.data.orig_exog,res.model.data.orig_endog],axis = 1).copy(deep = True)
    if (MODEL_TYPE != 'OLS') : # if it's not OLS then it's GLM
        prediction_res = res.get_prediction(transform = True)
        res_frame= prediction_res.summary_frame(alpha = 0.05)
        mdl_d['CI_lb'] =  res_frame['mean_ci_lower']
        mdl_d['CI_ub'] =  res_frame['mean_ci_upper']
        #mdl_d['PI_lb'] =  res_frame['obs_ci_lower']
        #mdl_d['PI_ub'] =  res_frame['obs_ci_upper']
        mdl_d['Predictions'] = res_frame['mean']
        mdl_d['Deviance_Resid'] = res.resid_deviance
    elif (MODEL_TYPE=='OLS'):
        prediction_res = res.get_prediction(transform  = True)
        res_frame= prediction_res.summary_frame(alpha = 0.05)
        mdl_d['CI_lb'] =  res_frame['mean_ci_lower']
        mdl_d['CI_ub'] =  res_frame['mean_ci_upper']
        mdl_d['PI_lb'] =  res_frame['obs_ci_lower']
        mdl_d['PI_ub'] =  res_frame['obs_ci_upper']
        mdl_d['Predictions'] = res_frame['mean']
        mdl_d['Residuals'] =  res.resid
    addoncols = [item for item in df.columns if item not in mdl_d.columns]
    imdl.pushlog(f"...Model data columns: \n....{','.join(mdl_d.columns)}")
    imdl.pushlog(f"...Extra data columns: \n....{','.join(addoncols)}")
    mdl_d = pd.concat([mdl_d,df[addoncols]],axis = 1)
    #print(f" In goModel modelsttring = {imdl.model_string}")

    return mdl_d, res, imdl.LOGSTR

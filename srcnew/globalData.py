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
import modelgrph as mgrph
import sys



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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  6 16:36:46 2025

@author: Knucklehead
"""
import pandas as pd
from pandas.api.types import is_numeric_dtype

import numpy as np

import seaborn as sb
from datetime import datetime
import functools
#import tkinter as tk
from tkinter import filedialog, messagebox
import re
import io

def checkName(namestr):
    if type(namestr) is not str: 
        gdata.log_It(f"{namestr} not interpretable as a string.")
        return(str(namestr))
    match0 = re.match(r'[0-9]',namestr)
    if match0 is not None:
        return namestr
    match1 = re.search(r'[^a-zA-Z0-9_]',namestr)
    if match1 is not None:
        return namestr
    return None


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
import Graphics as grp
import sys
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from scipy.interpolate import griddata


HAVELOESS2D = False
emsg = ''
loess_msg = "LOESS_2D routine of Cappellari et al. (2013b), which implements the multivariate LOESS algorithm of Cleveland & Devlin (1988)"
try:
    from loess.loess_2d import loess_2d
    HAVELOESS2D = True
except ImportError:
    emsg = "Non-fatal Warning: loess.loess_2d package not installed.  Loess smoothing for 3D plots will not be available."
    print(emsg)
    emsg = "install from: https://pypi.org/project/loess/  using pip install loess in your environment."
    print(emsg)



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
        self.data = pd.DataFrame()
        self.model_res = None
        self.model_data = None
        self.datatable = None
        self.logstr = ''
        self.codestr = ''
        #self.x2 = 0
        #self.x3 = 0
        #linear modelling globals
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
        self.addPredictions = '-'


    def getData(self):
        df = None
        filepath=None
        #filetypes = [("CSV Files", "*.csv")]
        filetypes = [("CSV files","*.csv"),("Excel files","*.xlsx"),("Old Excel files", "*.xls"),("Stata files","*.dta")]
        filepath = filedialog.askopenfilename(title="Open Data File",filetypes=filetypes)
        if not filepath:
            #messagebox.showinfo("Info","No file selected.")
            return(None,None)
        remove_comments = False
        comment_count = 0
        if filepath.endswith('.csv'):
            #buffered read for csv file to remove all data after a # (including the #).
            #Note: We can't use 'comment = "#" ' in read_csv because it interacts with nrows and header. If a bunch of '#' rows
            #come first nrow counts off eventhough the rows are skipped. Which means read stops before nrows of data have been read.
            buf = io.StringIO()
            with open(filepath, "r", encoding="utf-8") as file:
                for line in file:
                    has_comment = line.find("#")
                    if (has_comment != -1):
                        # if this is the first comment ask if we want to remove comments
                        if comment_count == 0:
                            emsg = f"Found a comment line (containing '#'). \n {line} \n Remove comments?"
                            remove_comments = messagebox.askyesno(" ", emsg)
                            comment_count += 1
                        #on the other hand if we've already selected our comment option either remove the comment and continue or
                        #write this line to the buffer and continue reading (the enclosing for loop)
                        if remove_comments:
                            gdata.log_It(f"Comment line removed: {line}")
                            line = line.split("#",1)[0]  + '\n'
                            comment_count += 1
                            # A line starting with # will not be read into the buffer a line with only whitespace
                            # before # will not be read into the buffer
                            if not line.strip():
                                continue
                    buf.write(line)            
            try:
                #read the first non-comment row
                buf.seek(0)
                df_temp= pd.read_csv(buf, engine= 'python', header=None, nrows=1)
                #note: strip() applied to item below will turn sequence of blanks into an empty string '' check for them later
                inputheader = [str(item).strip().replace(' ','_') for item in df_temp.iloc[0]]
                no_headercols = len(inputheader)
                ###Check for NA's in the header 
                #headerNAs = sum(np.array(inputheader).isna())
                headerNAs = list(df_temp.iloc[0].isna())
                headerEmpties = [True if item == '' else False for item in inputheader]
                headerBlanks = [itemNA or itemEM for itemNA, itemEM in zip(headerNAs, headerEmpties)]
                if any(headerBlanks):
                    naCol = [idx for idx, item in enumerate(headerBlanks) if item]
                    messagebox.showerror(" ",f"Columns: {naCol} do not have names. Temporary names will be attempted.")
                    for ix in naCol:
                        iy=0
                        dummyname = f"_*_Col({ix})"
                        while dummyname in inputheader:
                            iy += 1
                            dummyname = f"_*_Col{ix}_({iy})"
                        #print(f" missing or blank column name at: ix={ix} replaced with {dummyname}")
                        gdata.log_It(f" missing or blank column name at: ix={ix} replaced with {dummyname}")
                        inputheader[ix] = str(dummyname)
                #check for duplicate column names
                dup_names = [item for idx, item in enumerate(inputheader) if (item in inputheader[0:idx])]
                if len(dup_names)>0:
                    messagebox.showerror("  ", f"Inspite of my best efforts...\nDuplicate column names detected: {', '.join(list(set(dup_names)))}\n. ...Stopping.")
                    return(None, None)
                #read the remainder of the file
                buf.seek(0)
                df = pd.read_csv(buf, skiprows = 1, header=None) # header=0 is default
                ###Make sure there are as many column names as columns
                if len(df.columns) != no_headercols:
                        # Header line has a different length from the first data line
                        #print(inputheader)
                        #print(df.columns)
                        messagebox.showerror(title= '  ', message=f"Column label count ({no_headercols}) does not match the data column count {len(df.columns)}. \nProceeding will not end well. \nCheck data and try again.")
                        return(None,None)
                else:
                        #df.columns = [str(item) for item in inputheader] #make sure all column names are strings
                        df.columns = inputheader
                        lstr = f"df = pd.read_csv('{filepath}',engine='python')"
                        gdata.code_It(lstr)
                        gdata.log_It(f"Columns: {', '.join(inputheader)}")
            except pd.errors.ParserError as e:
                print(f"Error reading CSV: {e}")
                messagebox.showerror(title = '  ',message=f"Error reading CSV: {e}" )
                #df = pd.read_csv(filepath,engine='python',encoding_errors = 'ignore')
                #df = pd.read_csv(filepath,engine='python',index_col=False)
                return(None,None)
            except UnicodeDecodeError as ef:
                messagebox.showerror(" ", f"Error Reading CSV: {ef}. Recode data as utf-8")
                return(None,None)
            except Exception as exr:                 
                messagebox.showerror("Error Reading CSV:",f"Failed to read CSV file:\n{exr}")
                return(None,None)
        elif filepath.endswith(('.xlsx','.xls')):
            #much less robust input screening, assuming user has done required cleaning in excel 
            try:
                df = pd.read_excel(filepath)
                lstr = f"df=pd.read_excel('{filepath}')"
                gdata.code_It(lstr)
            except Exception as e:
                messagebox.showerror("Error",f"Failed to read Excel file:\n{e}")
                return(None,None)
        elif filepath.endswith('.dta'):
            #much less robust screening, assuming input file written by stata so has been pre-processed
            try:
                df = pd.read_stata(filepath)
                lstr = f"df=pd.read_stata('{filepath}')"
                gdata.code_It(lstr)
            except Exception as e:
                messagebox.showerror("Error",f"Failed to read Stata file:\n{e}")
                return(None,None)
        else:
            messagebox.showerror("Error","Unsupported file type. Please select a CSV, Excel or Stata .dta file.")
            return(None,None)       
        if df.empty:
            messagebox.showwarning("Warning","The selected file is empty or could not be read.")
            return(None,None)
        ### Check for machine infinite values (+/- np.inf)
        infbool = [sum(np.isinf(df[item])) for item in df.columns if is_numeric_dtype(df[item])]
        suminf = sum(infbool)
        listinf = [df.columns[idx]  for idx, item in enumerate(infbool) if infbool[idx] > 0] #for item in df.columns if sum(np.isinf(df[item])) >0]
        if suminf > 0:
            emsg = f"Data file contains {suminf} infinite values in columns: {', '.join(listinf)}\n Convert to NA? (Yes = convert, No = do not convert)"
            gdata.log_It(emsg)
            ynbool = messagebox.askyesno(" ", emsg)
            if ynbool:
                df.replace([np.inf, -np.inf], np.nan, inplace=True)
                gdata.log_It(f"{suminf} infinite values converted to NaN. Seriously, you should look at your input data.")


        success_msg = f"Data loaded successfully from file {gdata.fpath} \n{len(df)} rows and {len(df.columns)} columns."
        success_msg = success_msg + f"\n{len(gdata.data) - len(gdata.data.dropna())} rows contain missing data. {comment_count} comment rows skipped."
        messagebox.showinfo("Info",success_msg)
           
        badnames = [checkName(item) for item in df.columns if checkName(item) is not None]
        if len(badnames) > 0: 
            #print(f"{','.join(badnames)}")
            badnames_str = " ], [ ".join(badnames[:5])
            mstr  = "Found nonconforming variable names:\n" + badnames_str + "..." + "\n"
            mstr += "Variable names may consist of letters, numbers \nand underscores,"
            mstr += "no initial numerals, other symbols or included spaces.  "
            mstr += "Variables with non-conforming names may \nbe excluded from modelling and plotting.\n"
            mstr += "\n You can fix the non-conforming names by renaming those \n variables with 'Wrangle Data' module,"
            mstr += "saving the \nrenamed data and then reloading the data. \n"
            mstr += "Or, you may proceed and take your chances....YOU HAVE BEEN WARNED...\n"

            messagebox.showinfo(" ", mstr)
        return(df,filepath) 

        
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

    def get_Data2(self):
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

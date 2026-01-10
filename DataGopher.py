#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct  4 23:21:56 2025

@author: John
"""

#from patsy import dmatrices, NAAction
#from sklearn.metrics import roc_curve, auc
#from datetime import datetime
#import statsmodels.api  as sm
#import statsmodels.formula.api as smf
#from statsmodels.graphics.regressionplots import plot_partregress_grid, plot_leverage_resid2, influence_plot, plot_fit

import pandas as pd
from pandas.api.types import is_numeric_dtype
#import DataRead as dr
import Regression as rg
from Regression import imdl
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

#import matplotlib
import matplotlib.pyplot as plt
#import matplotlib.patches as mpatches
#     from mpl_toolkits.mplot3d import Axes3D
#import seaborn as sb

#import numpy as np 
#import scipy
#import globalData as gd
import goDataFilter as godf
import goPlot as gopt
import goModel as gosc
import goPivotb as gopv

from globalData import gdata

from datetime import datetime

import re
def checkName(namestr):
    match0 = re.match(r'[0-9]',namestr)
    if match0 is not None:
        return namestr
    match1 = re.search(r'[^a-zA-Z0-9_]',namestr)
    if match1 is not None:
        return namestr
    return None

class goStat(tk.Tk):
    def __init__(self):
        super().__init__()
        
        
        self.title("Data Gopher")
        self.geometry("800x50+0+0") 

        self.getButton = tk.Button(self, text = "Get Data", command = self.getData )
        self.getButton.pack(side = tk.LEFT, padx = 30)
        
        self.dataButton = tk.Button(self, text = 'Wrangle Data', command = self.startData)
        self.dataButton.pack(side = tk.LEFT)
        #self.dwrangle = gopiv.goPivot()
        
        self.pivotButton = tk.Button(self, text = 'Pivot Data', command = self.startPivot)
        self.pivotButton.pack(side = tk.LEFT)
        #self.dwrangle = godf.goData()

        self.plotButton = tk.Button(self,text="Plot Data",command = self.startPlot)
        self.plotButton.pack(side = tk.LEFT)
        
        self.regressionButton = tk.Button(self,text="Models",command = self.startRegression)
        self.regressionButton.pack(side = tk.LEFT)

        self.savelogButton = tk.Button(self, text ="Save Log", command = self.saveLog)
        self.savelogButton.pack(side = tk.LEFT)
        
        self.exitButton = tk.Button(self,text = "Graceful Exit", command = self.on_stat_close)
        self.exitButton.pack(side = tk.LEFT, padx = 30)
        #self.ddraw = gopt.goPlot()

        self.protocol("WM_DELETE_WINDOW", self.on_stat_close)

        self.regOn = False
        self.dataOn = False
        self.plotOn = False
        self.pivotOn = False
        #start the logger
        gdata.log_Init()
        #self.ddraw.protocol("WM_DELETE_WINDOW", self.on_toplevel_close)

    def saveLog(self, *args):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[('Text Files', '*.txt'), ('All Files', '*.*'), ('CSV Files', '*.csv')],
            initialfile = f"DG_LOG_{str(datetime.now()).replace(' ','_')}.txt"
        )
        if file_path.endswith((".txt",".TXT")):
            try:
                # Open the file in write mode ('w')
                with open(file_path, 'w') as file:
                    file.write(gdata.logstr)
                    #print(f"Successfully wrote the string to {file_path}")
                    gdata.log_It
            except IOError as e:
                    print(f"An error occurred while writing to the file: {e}")
   
            return

    def on_stat_close(self, *args):
        plt.close('all')
        endmsg = ''
        endmsg = "If you started this session from Idle, Spyder or Jupyter, \n"
        #to access original data globals()['gdata'].data   globals() gets the dictionary of global variables ['gdata'].data accesses
        #the data member of the gdata object.
        endmsg +="The data can be found in:"
        endmsg +="  dir(globals()['gdata'])\n"
        #endmsg +="  Spyder: Variable Explorer in  'gdata'\n"
        #endmsg +="  Jupyter: dir(globals()['gdata'])\n\n"
        #endmsg +="  ....Goodbye!"
        #messagebox.showinfo(" ", endmsg)

        
        bmsg = "Save Log File?"
        if messagebox.askyesno("Warning:",bmsg):
            #write out logger here
            self.saveLog()
            
        plt.close('all')
        self.destroy()
        
        
        
    def getData(self):
        df = None
        #filetypes = [("CSV Files", "*.csv")]
        filetypes = [("CSV files","*.csv"),("Excel files","*.xlsx"),("Old Excel files", "*.xls"),("Stata files","*.dta")]
        filepath = filedialog.askopenfilename(title="Open Data File",filetypes=filetypes)
        if filepath:
            if filepath.endswith('.csv'):
                try:
                    df = pd.read_csv(filepath,engine='python',encoding_errors = 'ignore')
                except UnicodeDecodeError as ef:
                    messagebox.showerror(" ", f"Error: {ef}. Recode data as utf-8")
                except Exception as e:                 
                    messagebox.showerror("Error",f"Failed to read CSV file:\n{e}")
                    return
            elif filepath.endswith(('.xlsx','.xls')):
                try:
                    df = pd.read_excel(filepath)
                except Exception as e:
                    messagebox.showerror("Error",f"Failed to read Excel file:\n{e}")
                    return
            elif filepath.endswith('.dta'):
                try:
                    df = pd.read_stata(filepath)
                except Exception as e:
                    messagebox.showerror("Error",f"Failed to read Stata file:\n{e}")
                    return
            else:
                messagebox.showerror("Error","Unsupported file type. Please select a CSV, Excel or Stata .dta file.")
                return
            
            if df.empty:
                messagebox.showwarning("Warning","The selected file is empty or could not be read.")
                return
            
            gdata.reset_Data(nupath=filepath, data_in=df)
            gdata.log_It(f"New Data File: {filepath}, Rows= {len(df)}, Columns={len(df.columns)} \n")
            
            #synchronize data in the open apps
            if self.regOn:
                #self.dstat.syncData()
                imdl.modelData_Clear()
                self.dstat.destroy()
                plt.close('all')
                self.regOn = False
            if self.pivotOn:
                self.dpivot.destroy()
                plt.close('all')
                self.pivotOn = False
                #self.dpivot.syncData()
            if self.plotOn:
                self.ddraw.destroy()
                self.plotOn = False
                plt.close('all')
                #self.ddraw.syncData()
            if self.dataOn:
                self.dwrangle.destroy()
                self.dataOn = False
                #self.dwrangle.syncData()
                
            messagebox.showinfo("Info",f"Data loaded successfully from file {gdata.fpath} \n{gdata.data.shape[0]} rows and {gdata.data.shape[1]} columns.")
            # if (('Predictions' in list(gdata.data.columns)) |  ('Residuals' in list(gdata.data.columns)) | 
            #         ('CI_lb' in list(gdata.data.columns)) | ('CI_ub' in list(gdata.data.columns)) | 
            #         ('PI_lb' in list(gdata.data.columns)) |('PI_ub' in list(gdata.data.columns))):
            #     bmsg = "One of the names: Predictions, Residuals, CI_lb, CI_up, PI_lb, PI_ub conflicts"
            #     bmsg += "with one or more variable names. For best results, please change the relevant variable names before continuing."
            #     messagebox.showinfo(" ",bmsg)
                
            badnames = [item for item in df.columns if checkName(item) is not None]
            if len(badnames) > 0: 
                badnames_str = " ], [ ".join(badnames)
                mstr  = "Found nonconforming variable names:\n" + "[" + badnames_str + "]\n"
                mstr += "For best results change the variable names.\n"
                mstr += "Or, you may proceed and use Q(\"variable name\") where needed.\n"
                mstr += "Variable names may consist of letters, numbers and underscores, no\n"
                mstr += "initial numerals, other symbols or included spaces."
                messagebox.showinfo(" ", mstr)
        else:
            messagebox.showinfo("Info","No file selected.")
        return      

    def startRegression(self):
        if gdata.data.empty: return
        if not self.regOn:
            self.dstat = gosc.RegressionApp()
            self.dstat.protocol("WM_DELETE_WINDOW", self.on_dstat_close)
            self.regOn = True
        else:
            self.dstat.lift()
            #messagebox.showinfo("Info","Regression window already open")
        return  
    
    def startPivot(self):
        if gdata.data.empty: return
        if not self.pivotOn:
            self.dpivot = gopv.goPivot()
            self.dpivot.protocol("WM_DELETE_WINDOW", self.on_pivot_close)
            self.pivotOn = True
        else:
            self.dpivot.lift()
            #messagebox.showinfo("Info","Data Wrangling window already open")
        return  
    
    def startData(self):
        if gdata.data.empty: return
        if not self.dataOn:
            self.dwrangle = godf.goData(self)
            self.dwrangle.protocol("WM_DELETE_WINDOW", self.on_data_close)
            self.dataOn = True
        else:
            self.dwrangle.lift()
            #messagebox.showinfo("Info","Data Wrangling window already open")
        return  
    
    def startPlot(self):
        if gdata.data.empty: return
        if not self.plotOn:
            self.ddraw = gopt.goPlot()
            self.ddraw.protocol("WM_DELETE_WINDOW", self.on_plot_close)
            self.plotOn = True
        else:
            self.ddraw.lift()
            #messagebox.showinfo("Info","Plotting window already open")
        return  
    
    def on_dstat_close(self):
        self.regOn = False
        self.dstat.destroy()
        plt.close('all')
        return
    
    def on_data_close(self):
        self.dataOn = False
        self.dwrangle.destroy()
        return
    
    
    def on_plot_close(self):
        self.plotOn = False
        plt.close('all')
        self.ddraw.destroy()
        return
    
    def on_pivot_close(self):
        self.pivotOn = False
        plt.close('all')
        self.dpivot.destroy()
        return
        

if __name__ == "__main__":
    app = goStat()

    app.mainloop()

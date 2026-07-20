#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct  4 23:21:56 2025

@author: Knucklehead
"""


#import pandas as pd

import tkinter as tk
from tkinter import filedialog, messagebox

#import matplotlib
import matplotlib.pyplot as plt


#import numpy as np  
import goDataFilter as godf
import goPlot as gopt
import goModel as gosc
import goPivotb as gopv

from globalData import gdata

from datetime import datetime

#from pandas.api.types import is_numeric_dtype
import re
#import io
     
# def nuNames(namelist = None):
#     if len(namelist) == 0: return
#     ix = 0
#     nuname = f"_*_{str(ix)}_Missing"
#     while nuname in namelist:
#         ix += 1
#         nuname = f"_*_{str(ix)}_Missing"
#         print(f"created new name: {nuname}")
#     return(nuname)

        

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

class goStat(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Data Gopher")
        self.geometry("900x50+0+0") 

        self.getButton = tk.Button(self, text = "Get Data", command = self.loadData )
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
        
        self.savelogButton = tk.Button(self, text ="Save Code", command = self.saveCode)
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
        gdata.code_Init()
        #self.ddraw.protocol("WM_DELETE_WINDOW", self.on_toplevel_close)

    def saveLog(self, *args):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[('Text Files', '*.txt'), ('All Files', '*.*'), ('CSV Files', '*.csv')],
            #initialfile = f"DG_LOG_{str(datetime.now()).replace(' ','_')}.txt"
            initialfile = f"DG_LOG_{datetime.now().strftime('%Y-%m-%d@%H-%M-%S')}.txt"
        )
        if file_path.endswith((".txt",".TXT")):
            try:
                # Open the file in write mode ('w')
                with open(file_path, 'w') as file:
                    file.write(gdata.log_Get())
                    #file.write(gdata.log_Get() + gdata.code_Get())
                    #print(f"Successfully wrote the string to {file_path}")
                    gdata.log_It(f"Log saved to {file_path}")
            except IOError as e:
                    print(f"An error occurred while writing to the file: {e}")
   
            return

    def saveCode(self, *args):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[('Text Files', '*.txt'), ('Python Files', '*.py'), ('All Files', '*.*'), ('CSV Files', '*.csv')],
            #initialfile = f"DG_LOG_{str(datetime.now()).replace(' ','_')}.txt"
            initialfile = f"DG_Code_{datetime.now().strftime('%Y-%m-%d@%H-%M-%S')}.py"
        )

        if file_path.endswith((".txt",".TXT",".py")):
            codestr = gdata.code_Get()
            try:
                # Open the file in write mode ('w')
                with open(file_path, 'w') as file:
                    file.write(codestr)
                    #print(f"Successfully wrote the string to {file_path}")
                    gdata.log_It(f"Code saved to {file_path}....hope you like python.")
            except IOError as e:
                    print(f"An error occurred while writing to the file: {e}")
   
            return


    def on_stat_close(self, *args):
        plt.close('all')
        endmsg = ''
        endmsg = "If you started this session from Idle, Spyder or Jupyter, \n"
        endmsg +="The data can be found in:"
        endmsg +="  dir(globals()['gdata'])\n"

        
        bmsg = "Save Log File?"
        if messagebox.askyesno("Warning:",bmsg):
            #write out logger here
            self.saveLog()
            
        plt.close('all')
        self.destroy()
        
    def loadData(self):
        df = None
        filepath = None
        df, filepath = gdata.getData()
        if df is None:
            return
        ##################################################################################
        ############## Updata the global data structure
        ##################################################################################
        gdata.reset_Data(nupath=filepath, data_in=df)
        gdata.log_It(f"pd.read_csv({filepath})")
        if len(gdata.data) <= 5000000000:
            numna = len(gdata.data) - len(gdata.data.dropna())            
            gdata.log_It(f"New Data File: {filepath}, Rows= {len(df)}, Columns={len(df.columns)}, {numna} rows have missing data. \n")

        ################################################
        #synchronize data in the open apps
        ################################################
        if self.regOn:
            #self.dstat.syncData()
            gdata.modelData_Clear()
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
        return        
        

    def startRegression(self):
        if gdata.data.empty:
            return
        if not self.regOn:
            self.dstat = gosc.RegressionApp()
            self.dstat.protocol("WM_DELETE_WINDOW", self.on_dstat_close)
            self.regOn = True
        else:
            self.dstat.lift()
            #messagebox.showinfo("Info","Regression window already open")
        return  
    
    def startPivot(self):
        if gdata.data.empty:
            return
        if not self.pivotOn:
            self.dpivot = gopv.goPivot()
            self.dpivot.protocol("WM_DELETE_WINDOW", self.on_pivot_close)
            self.pivotOn = True
        else:
            self.dpivot.lift()
            #messagebox.showinfo("Info","Data Wrangling window already open")
        return  
    
    def startData(self):
        if gdata.data.empty:
            return
        if not self.dataOn:
            self.dwrangle = godf.goData(self)
            self.dwrangle.protocol("WM_DELETE_WINDOW", self.on_data_close)
            self.dataOn = True
        else:
            self.dwrangle.lift()
            #messagebox.showinfo("Info","Data Wrangling window already open")
        return  
    
    def startPlot(self):
        if gdata.data.empty:
            return
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

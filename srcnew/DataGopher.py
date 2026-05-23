#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct  4 23:21:56 2025

@author: Knucklehead
"""


import sys as sys

import pandas as pd
from Regression import imdl
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

import matplotlib.pyplot as plt


import numpy as np  
import goDataFilter as godf
import goPlot as gopt
import goModel as gosc
import goPivotb as gopv

from globalData import gdata

from datetime import datetime

import re
     
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
    if type(namestr) != str: 
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
            initialfile = f"DG_LOG_{datetime.now().strftime("%Y-%m-%d@%H-%M-%S")}.txt"
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
            initialfile = f"DG_Code_{datetime.now().strftime("%Y-%m-%d@%H-%M-%S")}.py"
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
        
        
        
    def getData(self):
        df = None
        #filetypes = [("CSV Files", "*.csv")]
        filetypes = [("CSV files","*.csv"),("Excel files","*.xlsx"),("Old Excel files", "*.xls"),("Stata files","*.dta")]
        filepath = filedialog.askopenfilename(title="Open Data File",filetypes=filetypes)
        if filepath:
            if filepath.endswith('.csv'):
                try:
                    df_temp= pd.read_csv(filepath, engine= 'python', header=None, nrows=1)
                    #inputheader =  df_temp.iloc[0].astype(str)
                    inputheader = df_temp.iloc[0].copy(deep = True)
                    #print(inputheader)
                    #print(inputheader.astype(str))
                    headercols = len(inputheader)
                    colnamelist = list(inputheader)
                    #headerNAs = sum(df_temp.iloc[0].isna())
                    ###Check for NA's in the header 
                    headerNAs = sum(inputheader.isna())
                    if headerNAs > 0:
                        naCol = [idx for idx, item in enumerate(inputheader.isna()) if item]
                        messagebox.showerror(" ",f"Columns: {naCol} do not have names. Temporary names have been assigned.")
                        for ix in naCol:
                            iy=0
                            dummyname = f"_*_{ix}_missing({iy})"
                            while dummyname in colnamelist:
                                iy += 1
                                dummyname = f"_*_{ix}_missing({iy})"
                            gdata.log_It(f" missing column name at: ix={ix} replaced with {dummyname}")
                            #print(f"Dummy name: {dummyname}")
                            inputheader[ix] = str(dummyname)
                            #print(f"Input header: {', '.join(list(inputheader))}")
                    #inputheader2 = inputheader.astype(str)
                    #print(inputheader2)
                    #inputheader =  df_temp.iloc[0].astype(str)
                    headercols = len(inputheader)
                    df = pd.read_csv(filepath, skiprows = 1, header=None) # header=0 is default
                    ###Make sure there are as many column names as columns
                    if len(df.columns) != headercols:
                         # Header line has a different length from the first data line
                         print(inputheader)
                         print(df.columns)
                         messagebox.showerror(title= '  ', message=f"Column label count ({headercols}) does not match the data column count {len(df.columns)}. Proceeding will not end well. Check data and try again.")
                         return
                    else:
                         #df.columns = [str(item) for item in inputheader] #make sure all column names are strings
                         df.columns = inputheader
                         lstr = f"df = pd.read_csv('{filepath}',engine='python')"
                         gdata.code_It(lstr)
                         gdata.log_It(f"Columns: {', '.join(inputheader)}")
                         #print(f"Dataframe loaded successfully with {headercols} columns per row.")
                         #messagebox.showerror(title= '  ', message=f"Dataframe loaded successfully with {headercols} columns per row.")
                except pd.errors.ParserError as e:
                    print(f"Error reading CSV: {e}")
                    messagebox.showerror(title = '  ',message=f"Error reading CSV: {e}" )
                    #df = pd.read_csv(filepath,engine='python',encoding_errors = 'ignore')
                    #df = pd.read_csv(filepath,engine='python',index_col=False)
                    return
                except UnicodeDecodeError as ef:
                    messagebox.showerror(" ", f"Error Reading CSV: {ef}. Recode data as utf-8")
                    return
                except Exception as exr:                 
                    messagebox.showerror("Error Reading CSV:",f"Failed to read CSV file:\n{exr}")
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
            ### Check for machine infinite values (+/- np.inf)
            suminf = sum([sum(df[item].isin([-np.inf,+np.inf])) for item in df.columns])
            listinf = [item for item in df.columns if sum(df[item].isin([-np.inf, +np.inf])) >0]
            if suminf > 0:
                emsg = f"Data file contains {suminf} infinite values in columns: {",".join(listinf)}\n Convert to NA? (Yes = convert, No = do not convert)"
                gdata.log_It(emsg)
                ynbool = messagebox.askyesno(" ",emsg)
                if ynbool:
                    df.replace([np.inf, -np.inf], np.nan, inplace=True)
                    gdata.log_It(f"{suminf} infinite values converted to NaN")
            gdata.reset_Data(nupath=filepath, data_in=df)
            gdata.log_It(f"pd.read_csv({filepath})")
            if len(gdata.data) <= 5000000:
                numna = len(gdata.data) - len(gdata.data.dropna())            
                gdata.log_It(f"New Data File: {filepath}, Rows= {len(df)}, Columns={len(df.columns)}, {numna} rows have missing data. \n")

            
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
            success_msg = f"Data loaded successfully from file {gdata.fpath} \n{gdata.data.shape[0]} rows and {gdata.data.shape[1]} columns."
            success_msg = success_msg + f"\n{len(gdata.data) - len(gdata.data.dropna())} rows contain missing data."
            messagebox.showinfo("Info",success_msg)
                
            badnames = [checkName(item) for item in df.columns if checkName(item) is not None]
            if len(badnames) > 0: 
                badnames_str = " ], [ ".join(badnames[:5])
                mstr  = "Found nonconforming variable names:\n" + badnames_str + "..." + "\n"
                mstr += "Variable names may consist of letters, numbers \nand underscores,"
                mstr += "no initial numerals, other symbols or included spaces.  "
                mstr += "Variables with non-conforming names may \nbe excluded from modelling and plotting.\n"
                mstr += "\n You can fix the non-conforming names by renaming those \n variables with 'Wrangle Data' module,"
                mstr += "saving the \nrenamed data and then reloading the data. \n"
                mstr += "Or, you may proceed and take your chances....YOU HAVE BEEN WARNED...\n"
 
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

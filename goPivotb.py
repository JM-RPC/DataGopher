 #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 21 14:45:30 2025

@author: John
"""

#from patsy import dmatrices, NAAction
#from sklearn.metrics import roc_curve, auc
from datetime import datetime
import Listwidget as lw
#import statsmodels.api  as sm
#import statsmodels.formula.api as smf
#from statsmodels.graphics.regressionplots import plot_partregress_grid, plot_leverage_resid2, influence_plot, plot_fit

import numpy as np 

import pandas as pd
from pandas.api.types import is_numeric_dtype
#import DataRead as dr
#import Regression as rg
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
#from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, # interface between Figure class and Tkinter's Canvas
    NavigationToolbar2Tk # built-in toolbar for the figure
    )

import seaborn as sb

import globalData as gd
from globalData import gdata


import seaborn as sb

#import TableDisplayb as ptd
import TableDisplaya as ptd

sb.set_style("darkgrid", {"grid.color": ".6", "grid.linestyle": ":"})

aggfuns = ['sum','max', 'min', 'mean', 'count', 'size', 'median', 'std', 'var']
#plottypes = ['line','bar', 'barh', 'box', 'scatter', 'hist', 'kde', 'pie', 'area']
#plotnames = ['Line Plot', 'Bar Plot', 'Horiz. Bar Plot', 'Box Plot', 'Scatter Plot', 'Histogram', 'Kernel Density', 'Pie Chart', 'Area Plot']
#removed scatter plot (use goPlot.py for scatter plots):
plottypes = ['line','bar', 'barh', 'box', 'hist', 'kde', 'pie', 'area']
plotnames = ['Line Plot', 'Bar Plot', 'Horiz. Bar Plot', 'Box Plot', 'Histogram', 'Kernel Density', 'Pie Chart', 'Area Plot']
lzip = list(zip(plotnames, plottypes))
plotdict = {item[0]:item[1] for item in lzip}

class goPivot(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title('Data Pivot 0.1')
        #self.geometry('1100x600')

        #self.fig = plt.figure(figsize = (8,8), num = 1)
        #self.ax = self.fig.add_subplot()
        #set all the parameters
        
        if len(gdata.data) > 0:
            colnames = list(gdata.data.columns)
            numcolnames = [item for item in colnames if is_numeric_dtype(gdata.data[item])]
        else:
            colnames = []
            numcolnames = []
        #self.rowchoices = []
        #self.colchoices = []
        #self.valchoices = []
        
        self.rowlist = []
        self.collist = []
        self.vallist = []
        self.ptable = None
        
        self.f1 = ttk.Frame(self)
        
        #rows
        self.fw = ttk.Frame(self)
        
        #self.syncButton = tk.Button(self.fw, text = "Sync Data", command = self.syncData).grid(row=0, column=0, sticky= 'w',pady = 10, padx = 10)
        self.fpathlabel = tk.Label(self.fw, text = "File: " + gdata.fpath)
        self.fpathlabel.grid(row = 0, column = 1, columnspan = 5, sticky = 'w')
        self.savetablebutton = tk.Button(self.fw, text = "Save Current Table", command = self.saveTable)
        self.savetablebutton.grid(row = 0, column = 6)
        self.row_widget = lw.goList(self.fw,TEXT = "Rows:", CHOICES = colnames)
        #self.row_widget.pack(side = tk.TOP, anchor = tk.W)
        self.row_widget.grid(row = 1, column = 0, sticky = 'w')
        #self.spacelab = ttk.Label(self.fw,text = "  ").pack(side = tk.TOP)
        self.col_widget = lw.goList(self.fw,TEXT = "Columns:", CHOICES = colnames)
        #self.col_widget.pack(side = tk.TOP, anchor = tk.W)
        self.col_widget.grid(row = 1, column = 4,sticky= 'w')
        #self.spacelab = ttk.Label(self.fw,text = "  ").pack(side = tk.TOP)
        self.val_widget = lw.goList(self.fw,TEXT = "Values:", CHOICES = numcolnames)
        #self.val_widget.pack(side = tk.TOP, anchor = tk.W)
        self.val_widget.grid(row = 3, column = 0, sticky = 'w')
        #self.spacelab = ttk.Label(self.fw,text = "  ").pack(side = tk.TOP)
        self.agg_widget = lw.goList(self.fw, TEXT = "Aggregation Functions:", CHOICES=aggfuns)
        #self.agg_widget.pack(side = tk.TOP, anchor = tk.W)
        self.agg_widget.grid(row = 3, column = 4, sticky = 'w')
        self.fw.pack(side =tk.TOP)        

        #aggregation functions
        #self.selected_aggfunc = tk.StringVar(self)
        #self.aggfnlabel = tk.Label(self.f1, text="Aggregation Functions").grid(row = 6, column = 0)
      
        
        RLAST = 0
        self.marginvar = tk.StringVar(self,'Yes')
        self.mlabel = tk.Label(self.f1,text="Margins?").grid(row = RLAST, column = 1)
        self.mbutton = ttk.Radiobutton(self.f1,text = "Yes", variable = self.marginvar, value = 'Yes').grid(row=RLAST, column = 2)
        self.mbutton = ttk.Radiobutton(self.f1,text = "No", variable = self.marginvar, value = 'No').grid(row = RLAST, column = 3)
        self.pivButton = tk.Button(self.f1,text="Pivot", command = self.goPiv).grid(row = RLAST, column = 0)
        self.spacer = tk.Label(self.f1, text = "                ").grid(row = RLAST, column = 5, sticky = 'e', padx = 10, pady=10)
        self.plotlabel = tk.Label(self.f1, text="Plot Type:").grid(row=RLAST,column = 6)
        self.selected_plot = tk.StringVar(self,'Line Plot')
        self.plottype = tk.OptionMenu(self.f1,self.selected_plot,*plotnames)
        self.plottype.grid(row = RLAST, column=7)
        self.plotButton = tk.Button(self.f1, text = "Plot", command = self.dopivotPlot).grid(row =RLAST, column = 8,padx=10, pady=10)


        self.f1.pack(side = tk.TOP, anchor = tk.W)
        self.f2 = ttk.Frame(self)
        #self.pivFrame = ptd.DisplayPivotTable(self.f2,Pivot_Table=gdata.data)
        self.pivFrame = ptd.displayFrame_txt(self.f2,Pivot_Table = gdata.data)
        self.pivFrame.pack(expand = True, fill = "both", padx = 5, pady = 5)
        self.f2.pack(side = tk.TOP)

        #self.f3 = tk.Frame(self)
        #self.pivFrametext = ptd.displayFrame_txt(self.f3)
        #self.pivFrametext.pack(side = tk.TOP)
        #self.f3.pack(side = tk.TOP)

        self.protocol('WM_DELETE_WINDOW', self.exit_closing)  #kill window and clean up plots on exit button
    
    def saveTable(self):
        if gdata.datatable is not None:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[('Text Files', '*.txt'), ('All Files', '*.*'), ('CSV Files', '*.csv')],
                initialfile = f"goData_{str(datetime.now()).replace(' ','_')}.csv"
                )
            gdata.datatable.to_csv(file_path)
        else:
            messagebox.showerror(" ","You need to create a pivot table to save a pivot table.")
        return
            
        
    def dopivotPlot(self, *args):
        plotname = self.selected_plot.get()
        if plotname == '': plotname = 'line'
        if plotname != 'Pie Chart':
            try:
                gdata.datatable.plot(kind = plotdict[plotname], figsize = (6,4), rot = 90)
                plt.subplots_adjust(left=0.10, right=0.80, top=0.9, bottom=0.15)
                #plt.tight_layout()
                plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0)
                plt.show()
            except Exception as er:
                messagebox.showerror(" ","Plotting Error: " + str(er))
            return
        else:
            pval = self.val_widget.rowlist[0]
            aggf = self.agg_widget.rowlist[0]
            try:
                gdata.datatable.plot.pie(y = (aggf,pval), autopct='%1.1f%%',figsize = (8,6))
                plt.show()

            except Exception as er:
                messagebox.showerror(" ","Plotting Error: " + str(er) + "\nHint: categories/series go in the rows and columns, values in value, one value in agg function.")
            return
            
    def goPiv(self, *args):
        pcols = self.col_widget.rowlist
        prows = self.row_widget.rowlist
        pvals = self.val_widget.rowlist
        pfuna = self.agg_widget.rowlist
        if self.marginvar.get() == 'Yes' : 
            domarg = True
        else:
            domarg = False
        try:
            pivot_table = pd.pivot_table(gdata.data, values=pvals, index=prows, columns=pcols, aggfunc=pfuna, margins = domarg)
        except Exception as er:
            messagebox.showerror(" ", "Pivot Error:" + str(er))
            return
        gdata.datatable = pivot_table
        self.pivFrame.do_display(PT = pivot_table)

        log_msg = f" Pivot Table: rows= {', '.join(prows)}, \n...columns= {', '.join(pcols)}, \n...values= {', '.join(pvals)}, \n...aggfunc= {', '.join(pfuna)}, margins= {domarg}"
        gdata.log_It(log_msg)


        return
    


    #replaces syncData for stand alone ops
    def getData(self,*args):
        #self.dfDisplay()
        #file_types = [("CSV Files", "*.csv"), ("Text Files", "*.txt"), ("All Files", "*.*")]
        if len(gdata.data) > 0:
            self.fpath = gdata.fpath
            self.doReset(gdata.data)
            
        else:
            file_types = [("CSV Files", "*.csv"),("Excel Files", "*.xlsx"), ("Stata Files", "*.dta")]
            file_path = filedialog.askopenfilename(filetypes=file_types, title="Select a File")
            if file_path != '':
                df_in = pd.read_csv(file_path)
                self.fpath = file_path
                #self.doReset(df_in)
                gdata.reset_Data(file_path, df_in)
        return
    
    def syncData(self,*arg):
        if len(gdata.data) > 0:
            self.fpath = gdata.fpath
            colnames = list(gdata.data.columns)
            numcolnames = [item for item in colnames if is_numeric_dtype(gdata.data[item])]

            self.row_widget.resetList(NUTEXT = None, NUCHOICES = colnames)
            self.col_widget.resetList(NUTEXT = None, NUCHOICES = colnames)
            self.val_widget.resetList(NUTEXT = None, NUCHOICES = numcolnames)
            
            #plt.close('all')
           
            #self.doReset(gdata.data)
        return
    
    def exit_closing(self,*args):
        plt.close('all')
        self.destroy()
        return 
    
    def doReset(self, data_in):
        self.data = data_in
        return





if __name__ == "__main__":
    
    gdata = gd.globalData()
    class solo(tk.Tk):
        def __init__(self):
            super().__init__()
            self.geometry("350x50+0+0") 
            self.title("Pivot Data Standalone")

            self.onButton = tk.Button(self, text = "Get Data", command = self.getData).pack(side = tk.LEFT, padx = 10)
            self.goPivot  = tk.Button(self, text = "Pivot Data", command = self.pivD).pack(side = tk.LEFT, padx = 10)
            self.offButton = tk.Button(self, text="Graceful Exit", command = self.quit).pack(side = tk.LEFT, padx = 10)

            
            #gst = goPivot(self)
        
        def pivD(self,*args):
            if len(gdata.data) == 0: return
            self.gst = goPivot()
            self.gst.syncData()
            #self.ptable = displayPivotTable(self).pack()
                        
        def quit(self,*args):
            #plt.close('all')
            self.destroy()
            return 
        
        def getData(self,*args):
           #self.dfDisplay()
           #file_types = [("CSV Files", "*.csv"), ("Text Files", "*.txt"), ("All Files", "*.*")]
            file_types = [("CSV Files", "*.csv"),("Excel Files", "*.xlsx"), ("Stata Files", "*.dta")]
            file_path = filedialog.askopenfilename(filetypes=file_types, title="Select a File")
            if file_path != '':
                df_in = pd.read_csv(file_path)
                self.fpath = file_path
                gdata.reset_Data(file_path, df_in)
            return
            

    app = solo()
    app.mainloop()

    #fileGetWindow = dr.fileBrowsePreview()
    #df = fileGetWindow.data
    #filename = fileGetWindow.filepath
    import globalData as gd

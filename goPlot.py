#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  2 09:06:58 2025

@author: John
"""

#from patsy import dmatrices, NAAction
#from sklearn.metrics import roc_curve, auc
from datetime import datetime
#import statsmodels.api  as sm
#import statsmodels.formula.api as smf
#from statsmodels.graphics.regressionplots import plot_partregress_grid, plot_leverage_resid2, influence_plot, plot_fit

import pandas as pd
from pandas.api.types import is_numeric_dtype
#import DataRead as dr
#import Regression as rg
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from mpl_toolkits.mplot3d import Axes3D
from scipy.special import yv
import seaborn as sb

import numpy as np 
#import scipy

import globalData as gd
from globalData import gdata

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, # interface between Figure class and Tkinter's Canvas
    NavigationToolbar2Tk # built-in toolbar for the figure
    )

import seaborn as sb
sb.set_style("darkgrid", {"grid.color": ".6", "grid.linestyle": ":"})


from mpl_toolkits.mplot3d import Axes3D

#import DataRead as dr
#from Regression import imdl
#import Graphics as grp
import sys

colorlim = 1000

basecolors0 = ['blue', 'red',  'green', 'yellow', 'magenta', 'cyan', 'violet', 
               'orange',  'goldenrod','grey','gold','silver','orangered', 'darkolivegreen',
               'olive','khaki','thistle','lightsteelblue','slateblue','black','darkviolet',
               'brown', 'indigo', 'hotpink', 'lavender']


gphIndex = ['V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7', 'V8', 'V9', 'V10']

markers0 = ['.','o','v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'X']

marker_names = ['point', 'filled dot', 'triangle_d', 'triangle_u', 'triangle_l', 'triangle_r',
              'octagon',     'square',   'pentagon',       'star',  'hexagon_1',  'hexagon_2', 'diamond_1',
            'diamond_2',     'plus'  ,   'x']

plot_types = ['Boxplot', 'Histogram', 'ECDF', '2D Scatter Plot','2D Scatter Grid', '3D Scatter Plot']
markerdict = {name : marker for name, marker in zip(marker_names, markers0)}

#Helper function for 3D color plotting
basecolornos = [matplotlib.colors.to_rgba(item,alpha = None) for item in basecolors0]
def getcolor(col_data):
    dfc = pd.DataFrame(col_data).astype('str')
    choicesCo = list(dfc[dfc.columns[0]].astype('str').unique())
    choicesCo.sort()
    if (len(choicesCo) < len(basecolors0)):
        colorD = {item : basecolors0[choicesCo.index(item)]  for item in choicesCo}
        colorlist = [colorD[str(item)] for item in col_data]
        lpatches = [mpatches.Patch(color = colorD[item],label = item) for item in colorD.keys()]
    else:
        cmap = plt.cm.plasma
        #colorNos = [choicesCo.index(item) for item in col_data]
        colorD = {item : cmap(choicesCo.index(item)/len(choicesCo)) for item in choicesCo}
        colorlist = [colorD[item] for item in col_data]
        lpatches = [mpatches.Patch(color = colorD[item],label = item) for item in choicesCo]
    return colorlist, lpatches

#utility function to create a non coflicting column name
def newname(df = pd.DataFrame(), newname = ''):
    if newname == '': return
    if len(df) == 0: return
    names = list(df.columns)
    if newname not in names: return(newname)
    idx = 0
    while newname in names:
        newname += str(idx)
        idx += 1
    return(newname)
       
#class goPlot(tk.Tk):
class goPlot(tk.Toplevel):
    def __init__(self):
        super().__init__()
    
        # self.filepath = ''
        # self.data = pd.DataFrame() #the original data
        # self.outdata = pd.DataFrame() #the wrangled data
        # self.varlist0 = list(self.data.columns) #the original column names 
        #self.data and self.varlist0 will be modified in getData only.
        #they are accessed by varupdate()
    
        self.title('Data Plotter Prototype')
        #self.geometry('1100x400')

        #self.fig = plt.figure(figsize = (8,8), num = 1)
        #self.ax = self.fig.add_subplot()
        self.protocol('WM_DELETE_WINDOW', self.exit_closing)  #kill window and clean up plots on exit button
        self.plot_type = ''

        self.f0a = tk.Frame(self)
        self.f0a.grid_rowconfigure(0, weight=1)
        self.f0a.grid_columnconfigure(0, weight=1)

        self.f0a.configure(borderwidth=2, relief="ridge", highlightthickness=1)
        self.f0a.pack(side = tk.TOP, anchor = 'nw', expand = False) #, padx = 10, pady = 10)


        #self.file_button = tk.Button(self.f0,text= 'Sync Data',command = self.syncData)
        #self.file_button.grid(row = 0, column = 0, sticky = 'w',padx=10)
        
        self.fname_label = tk.Label(self.f0a,text = '')
        self.fname_label.grid(row = 0, column = 1, columnspan = 3)
        self.clear_button = tk.Button(self.f0a,text= 'Clear Last Variable', command = self.clearIt)
        self.clear_button.grid(row = 0, column = 8, sticky = 'e', padx = 10)
        #self.plot_savedata = tk.Button(self.f0a, text="Save Current Plotting Data", command = self.saveData).grid(row=4, column=0)
       
        #now a variable chooser
        self.selected_variable = tk.StringVar()
        self.Label1 = tk.Label(self.f0a, text='Select Numerical Variables:').grid(row = 1, column = 0)
        self.options = ttk.Combobox(self.f0a, values=[],textvariable = self.selected_variable)
        self.options.grid(row = 1, column = 1, columnspan = 3, sticky = 'w')
        self.options.bind("<<ComboboxSelected>>", self.varupdate)
        
        #now a parameter chooser (color, marker, facet etc.)
        self.current_parms = []
        self.selected_color_variable = tk.StringVar()
        self.Label2 = tk.Label(self.f0a, text = 'Color Variable:').grid(row = 1, column = 4)
        self.copts = ttk.Combobox(self.f0a, values = [], textvariable = self.selected_color_variable)
        self.copts.grid(row = 1, column=5)
        self.Label2b = tk.Label(self.f0a, text = f" {colorlim} colors max").grid(row = 1, column = 8, sticky = 'w')
        self.copts.bind("<<ComboboxSelected>>", self.parmupdate)
        
        self.f0_2d = tk.Frame(self.f0a)
        self.f0_2d.grid_rowconfigure(0, weight=1)
        self.f0_2d.grid_columnconfigure(0, weight=1)

        self.f0_2d.configure(borderwidth=0, highlightthickness=0, relief="flat")
        #self.f0.pack(side = tk.TOP, anchor = 'nw', expand = False) #, padx = 10, pady = 10)
        #self.f0.pack_forget()
        #self.f0.grid(row =2, column = 4, columnspan = 4, sticky = 'w')
        self.f0_2d.grid_forget()

        self.f0_2dg = tk.Frame(self.f0a)
        self.f0_2dg.grid_rowconfigure(0, weight=1)
        self.f0_2dg.grid_columnconfigure(0, weight=1)

        self.f0_2dg.configure(borderwidth=0, highlightthickness=0, relief="flat")
        #self.f0.pack(side = tk.TOP, anchor = 'nw', expand = False) #, padx = 10, pady = 10)
        #self.f0.pack_forget()
        #self.f0.grid(row =2, column = 4, columnspan = 4, sticky = 'w')
        self.f0_2dg.grid_forget()

        self.selected_marker_variable = tk.StringVar()
        self.Label3 = tk.Label(self.f0_2d, text = 'Marker  Variable')
        self.Label3.grid(row = 2, column = 4)
        self.mopts = ttk.Combobox(self.f0_2d, values = [], textvariable = self.selected_marker_variable)
        self.mopts.grid(row = 2, column=5)
        self.Label3b = tk.Label(self.f0_2d, text = f" {len(markers0)} markers max").grid(row = 2, column = 8, sticky = 'w')
        self.mopts.bind("<<ComboboxSelected>>", self.parmupdate)

        maxfacet = min(len(markers0),len(basecolors0))
        self.selected_row_variable = tk.StringVar()
        self.Label4 = tk.Label(self.f0_2dg, text = 'Row Facet Variable:').grid(row = 3, column = 4)
        self.fropts = ttk.Combobox(self.f0_2dg, values = [], textvariable = self.selected_row_variable)
        self.fropts.grid(row = 3, column=5)
        self.Label4b = tk.Label(self.f0_2dg, text = f" {maxfacet} row facets max").grid(row = 3, column = 8, sticky = 'w')
        self.fropts.bind("<<ComboboxSelected>>", self.parmupdate)
        
        self.selected_col_variable = tk.StringVar()
        self.Label5 = tk.Label(self.f0_2dg, text = 'Column Facet Variable:').grid(row = 4, column = 4)
        self.fcopts = ttk.Combobox(self.f0_2dg, values = [], textvariable = self.selected_col_variable)
        self.fcopts.grid(row = 4, column=5)
        self.Label5b = tk.Label(self.f0_2dg, text = f" {maxfacet} column facets max").grid(row = 4, column = 8, sticky = 'w')
        self.fcopts.bind("<<ComboboxSelected>>", self.parmupdate)
        
        self.varlist = []
        self.varno = 0
        self.v1list = []
        
        self.f1 = tk.Frame(self)
        self.f1.configure(borderwidth=2, relief="ridge", highlightthickness=1)
        self.f1.pack(side = tk.TOP, anchor = 'nw', expand = True)#, padx = 10 , pady=10)
        self.f2 = tk.Frame(self)
        self.f2.configure(borderwidth=2, relief="ridge", highlightthickness=1)
        self.f2.pack(side = tk.TOP, anchor = 'nw', expand = True)
        self.f3 = tk.Frame(self)
        self.f3.configure(borderwidth = 2, relief = "ridge", highlightthickness = 1)
        self.f3.pack(side = tk.TOP, anchor = 'nw', expand = True)
        
        self.gp1 = gPlot(self.f3)
        self.gp1.pack_forget()


        if len(gdata.data) > 0:
            self.fpath = gdata.fpath
            self.doReset(gdata.data)
        
    def exit_closing(self):
        plt.close('all')
        self.destroy()  # This closes the Tkinter window    
        
    def clearIt(self, *args):       
        if len(self.v1list) == 0:
            return
        vtemp = self.v1list.pop()
        deletedvar = vtemp.varname
        vtemp.destroy()
        self.current_varlist.remove(deletedvar)
        remaining_varlist = [item for item in self.varlist0 if item not in self.current_varlist]
        self.options['values'] = remaining_varlist
        self.options.set("")
        
    def doPlot(self,*args):
        pass
    def savePlot(self,*args):
        pass
    
    def saveData(self, *args):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[('Text Files', '*.txt'), ('All Files', '*.*'), ('CSV Files', '*.csv')],
            initialfile = f"goData_{str(datetime.now()).replace(' ','_')}.csv"
        )
        self.data.to_csv(file_path)
        return


    
    def doReset(self,DATA,*args):
        while len(self.v1list) > 0 : self.clearIt()
        self.data = DATA
        self.varlist0 = [item for item in self.data.columns if is_numeric_dtype(self.data[item])]
        self.marklist0 = [item for item in list(self.data.columns) if len(self.data[item].unique()) <= len(markers0)]
        #self.colorlist0 = [item for item in list(self.data.columns) if len(self.data[item].unique()) <=len(basecolors0)]
        #arbitrary limit 1000 different colors
        self.colorlist0 = [item for item in list(self.data.columns) if len(self.data[item].unique()) <=1000]
        maxfacet = min(len(markers0),len(basecolors0))
        self.facetlist0 = [item for item in list(self.data.columns) if len(self.data[item].unique()) <= maxfacet]
        self.options['values'] = [''] + self.varlist0
        self.mopts['values'] = [''] + self.marklist0
        self.copts['values'] = [''] + self.colorlist0
        self.fropts['values'] = [''] + self.facetlist0  
        self.fcopts['values'] = [''] + self.facetlist0
        self.selected_color_variable.set('')
        self.selected_marker_variable.set('')
        self.selected_row_variable.set('')
        self.selected_col_variable.set('')
        self.current_varlist = []
        self.gp1.pack(side = tk.BOTTOM, anchor = 'sw') #start the plotting stuff
        self.fname_label.config(text = "File: " + self.fpath)
        plt.close('all')
        return
    
    # def get_dfdata(self, *args):
    #     self.path = 'internal'
    #     self.doreset(dfdata)
    #     return
    
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
                self.doReset(df_in)
                gdata.reset_Data(file_path, df_in)
        return
    
    def syncData(self,*arg):
        if len(gdata.data) > 0:
            self.fpath = gdata.fpath
            self.doReset(gdata.data)
        return

    def varupdate(self,event):
        newvar = str(self.selected_variable.get())
        if newvar == '': return
        
        #add newvar to the list of current variables if it is new
        if newvar in self.current_varlist:
            return
        self.current_varlist.append(newvar)
        
        #now reset the remaining variable choices
        remaining_varlist = [item for item in self.varlist0 if item not in self.current_varlist]
        self.options['values'] = remaining_varlist
        self.options.set("")
        
        #now create an instance v1, of a  variable object (gVar) to hold variable info and append it to the list
        #of active variables (v1list
        self.v1 = gVar(self.f1,varname = newvar)
        self.v1.pack(side = tk.LEFT, anchor = 'w')
        self.v1list.append(self.v1)
        
        #change the variable frame depending on whether variable is independent (and x or y) 
        # or dependent (z, z1, .. and beyond).  Independent variables don't get markers
        #they are represented on the axes. Whether or not the y variable (v1list[1])
        #is dependent or independent depends on the dimensions of the
        #plot: for 3D first two are indep, for 2D only the first one.
        #Independent variables  are v1list[0] for 2D and v1list[0] and v1list[1] for 3D plots.
        #....this may be over-the-top  a little bit.
        if len(self.v1list) == 1: #if this is the x variable don't show graphing options
            self.v1.mframe.grid_forget()
        elif (self.plot_type in ['3D Scatter Plot', '3D Surface Plot']) & (len(self.v1list) >= 2):
            self.v1list[1].mframe.grid_forget()
        elif (self.plot_type in ['2D Scatter Plot', '2D Line Graph']) & (len(self.v1list) >= 2):
            self.v1list[1].mframe.grid(row = 4, column = 0, rowspan=3, columnspan = 2, sticky='w')
        #if there are no variables in v1list then kill the plot choice window
        if (len(self.v1list)==0):
            for item in self.f3.winfo_children():
                item.destroy()
        return

    def parmupdate(self, event):  #makes the entries in the color variable, marker variable, and facet variables unique
        
        self.current_parms = [self.selected_col_variable.get(),self.selected_row_variable.get(),
                              self.selected_color_variable.get(), self.selected_marker_variable]
        
        marker_var = [item for item in self.marklist0 if item not in self.current_parms ]
        color_var  = [item for item in self.colorlist0 if item not in self.current_parms]
        facet_var  = [item for item in self.facetlist0 if item not in self.current_parms]
        
        self.mopts['values'] = [''] + marker_var
        self.copts['values'] = [''] + color_var
        self.fropts['values'] = [''] + facet_var  
        self.fcopts['values'] = [''] + facet_var


    
class gVar(tk.Frame):    
    def __init__(self, parent, varname = None):  
        super().__init__(master= parent)

        self.clickedGX = tk.StringVar()
        
        self.configure(borderwidth=2, relief="ridge", highlightthickness=1)
        #gphvars = list(self.master.varlist0)
        
        #nameing convention for variables
        novars = len(self.master.master.v1list)
        if novars == 0:
            namesuffix = 'X'
        elif novars == 1:
            namesuffix = 'Y'
        elif novars == 2:
            namesuffix = 'Z'
        else: 
            namesuffix = 'Z'+str(novars-2)
            
        self.varname = varname


        #self.clickedGX = tk.StringVar()
        self.gxlab = tk.Label(self, text=varname + ": " + namesuffix)
        self.gxlab.grid(row = 0, column = 0,sticky='w', padx = 20)
        if is_numeric_dtype(self.master.master.data[varname]):
            vmin = np.nanmin(self.master.master.data[varname])
            vmax = np.nanmax(self.master.master.data[varname])
        else:
            vmin = 0
            vmax = 0
            
        self.xub = tk.DoubleVar(self,vmax)
        self.gxupper = tk.Label(self, text = 'Upper lim:').grid(row = 1, column = 0, sticky = 'w')
        self.gxub = tk.Entry(self, textvariable = self.xub, width = 10)
        self.gxub.grid(row = 1, column = 1,sticky = 'w')

        self.xlb = tk.DoubleVar(self,vmin)
        self.gxlow = tk.Label(self,text = "Lower lim:").grid(row = 2, column =0, sticky = 'w')
        self.gxlb  = tk.Entry(self,textvariable = self.xlb, width = 10)
        self.gxlb.grid(row = 2,column=1, sticky = 'w')
        
        self.xlabel = tk.StringVar(self,varname)
        self.label =tk.Label(self, text = 'Axis Label:').grid(row=3, column=0, sticky = 'w')
        self.gxlabel = tk.Entry(self, textvariable = self.xlabel, width = 12)
        self.gxlabel.grid(row = 3, column = 1, sticky = 'w')

        self.mframe = tk.Frame(self)
        self.mframe.grid(row = 4, column = 0, rowspan=3, columnspan = 2, sticky='w')
        self.clickedGXmkr = tk.StringVar()
        self.selected_gzmarker = tk.StringVar()
        self.gxmkrl= tk.Label(self.mframe, text = 'Marker:')
        self.gxmkrl.grid(row = 0, column=0, sticky = 'w')
        self.gxmkr = tk.OptionMenu(self.mframe,self.clickedGXmkr, *marker_names)
        self.gxmkr.grid(row =  0, column = 1, sticky = 'w')
    
        self.clickedGXcol = tk.StringVar()
        self.gxlabcolor = tk.Label(self.mframe,text = "Color:").grid(row = 1, column = 0, sticky = 'w')
        self.gxcolor = tk.OptionMenu(self.mframe,self.clickedGXcol,*([''] + basecolors0))
        self.gxcolor.grid(row = 1, column = 1, sticky = 'w')
    
        self.gxszsld = tk.Label(self.mframe, text = 'Marker Size:')
        self.gxszsld.grid(row = 2, column =0, sticky = 'w')
        self.gxlsz = tk.Scale(self.mframe, from_ = 0.25, to = 100, orient='horizontal', showvalue = True)
        self.gxlsz.grid(row = 2, column =1, sticky = 'w')
        self.gxlsz.set(5)
        
        self.clickedGXlnstyle = tk.StringVar()
        self.gxlnstylel = tk.Label(self.mframe, text = 'Line Style:')
        self.gxlnstylel.grid(row = 3, column =0, sticky = 'w')
        self.gxlnstyle = tk.OptionMenu(self.mframe,self.clickedGXlnstyle,*['scatter', 'line', 'dashed', 'dotted', 'dashdot'])
        self.gxlnstyle.grid(row = 3, column =1, sticky = 'w',padx = 5)
        

class gPlot(tk.Frame):
    
    def __init__(self, parent):  
        super().__init__(master = parent)

        self.plotchoice = tk.StringVar(self)
        self.plotlabel = tk.Label(self,text="Plot Type:").grid(row = 0, column=0)
        self.plot_options = tk.OptionMenu(self, self.plotchoice, *plot_types , command = self.doPlotParms)
        self.plot_options.grid(row= 0,column=1)
        #self.plot_button = tk.Button(self, text="Plot It!", command = self.doPlot).grid(row = 0 , column = 2)
        #self.plot_save = tk.Button(self, text ="Save Plot", command = self.savePlot).grid(row = 0, column = 4)
        #self.plot_savedata = tk.Button(self, text="Save Plotting Data", command = self.saveData).grid(row=0, column=6)

        self.optionsframe = tk.Frame(self, borderwidth=2, relief="ridge", highlightthickness=1)
        self.optionsframe.grid(row = 1, column = 0, rowspan = 6, columnspan = 6)



        #self.optionslabel.pack(anchor = 'nw')
        
        self.meqn = tk.StringVar(None)
        self.teq1 = tk.Entry(self,textvariable = self.meqn, width = 80)
    
    
    def doPlotParms(self,*args): #set up the UI for extra information for each type of plot
        #first, clear the options frame
        for item in self.optionsframe.winfo_children():
            item.destroy()
        #plt.close('all')
        plot_type = self.plotchoice.get()
        #setup the facet/marker variable option lists
        self.master.plot_type = plot_type
        colvar = self.master.master.selected_color_variable.get()
        if colvar != '':
            flist = [item for item in self.master.master.facetlist0 if item != colvar]
            mlist = [item for item in self.master.master.marklist0 if item != colvar]
        else:
            flist = self.master.master.facetlist0
            mlist = self.master.master.marklist0
        
        if plot_type == 'Histogram':
            if len(self.master.master.v1list) > 1:
                self.master.master.v1list[1].mframe.grid(row = 4, column = 0, rowspan=3, columnspan = 2, sticky='w') 
            self.master.master.mopts['values'] = [''] + mlist
            self.master.master.selected_marker_variable.set('')            
            self.master.master.f0_2d.grid_forget() #don't show the marker choice
            self.master.master.f0_2dg.grid(row =2, column =4, columnspan = 4, sticky = 'w') #show facet choices
            self.getHistogramParms()
        elif plot_type == 'Boxplot':
            if len(self.master.master.v1list) > 1:
                self.master.master.v1list[1].mframe.grid(row = 4, column = 0, rowspan=3, columnspan = 2, sticky='w')
            self.master.master.mopts['values'] = [''] + mlist
            self.master.master.selected_marker_variable.set('')

            self.master.master.f0_2d.grid_forget()
            self.master.master.f0_2dg.grid(row =2, column =4, columnspan = 4, sticky = 'w')
            self.getBoxplotParms()
        elif plot_type == 'ECDF':
            if len(self.master.master.v1list) > 1:
                self.master.master.v1list[1].mframe.grid(row = 4, column = 0, rowspan=3, columnspan = 2, sticky='w')
            self.master.master.mopts['values'] = [''] + mlist
            self.master.master.selected_marker_variable.set('')

            self.master.master.f0_2d.grid_forget()
            self.master.master.f0_2dg.grid(row =2, column =4, columnspan = 4, sticky = 'w')
            self.getECDFParms()
        elif plot_type == '2D Scatter Plot' :
            if len(self.master.master.v1list) > 1:
                self.master.master.v1list[1].mframe.grid(row = 4, column = 0, rowspan=3, columnspan = 2, sticky='w')  
            #self.master.master.f0.pack()
            #reset the row and column facet indicators if doing a single 2d plot
            self.master.master.f0_2d.grid(row =2, column = 4, columnspan = 4, sticky = 'w')
            self.master.master.fropts['values'] = [''] + flist  
            self.master.master.fcopts['values'] = [''] + flist
            self.master.master.selected_row_variable.set('')
            self.master.master.selected_col_variable.set('')
            self.master.master.f0_2dg.grid_forget()
            self.get2DScatterParms()
            return
        elif plot_type == '2D Scatter Grid':
            if len(self.master.master.v1list) > 1:
                self.master.master.v1list[1].mframe.grid(row = 4, column = 0, rowspan=3, columnspan = 2, sticky='w')  
            #self.master.master.f0.pack()
            self.master.master.f0_2dg.grid(row =2, column =4, columnspan = 4, sticky = 'w')
            #reset the marker variable when facet plotting
            self.master.master.mopts['values'] = [''] + mlist
            self.master.master.selected_marker_variable.set('')
            self.master.master.f0_2d.grid_forget()
            self.get2DScatterGridParms()
            return
        elif plot_type == '3D Scatter Plot':
            if len(self.master.master.v1list) > 1:
                self.master.master.v1list[1].mframe.grid_forget()
            #self.master.master.f0.pack_forget()
            #reset the row and column facet indicators if doing a single 3d plot

            self.master.master.fropts['values'] = [''] + flist 
            self.master.master.fcopts['values'] = [''] + flist
            self.master.master.selected_row_variable.set('')
            self.master.master.selected_col_variable.set('')
            #reset  marker variable when doing 3d plot
            self.master.master.mopts['values'] = [''] + mlist
            self.master.master.selected_marker_variable.set('')
            self.master.master.f0_2dg.grid_forget()
            self.master.master.f0_2d.grid_forget()
            self.get3DScatterParms()
            return
        elif plot_type == '3D Surface Plot':
            if len(self.master.master.v1list) > 1:
                self.master.master.v1list[1].mframe.grid_forget()
            self.get3DSurfParms()
            return
        else:
            return
        #self.label = tk.Label(self.optionsframe, text=f"Plot type = {plot_type}").grid(row = 0, column = 0)
        #self.gobutton = tk.Button(self.optionsframe, text="Plot It!", command = self.plotHisto).grid(row=0,column = 6)

        return

###########################################################################
###  functions to get extra parameters for the chosen plots
###########################################################################

    def get2DScatterParms(self):
        self.label = tk.Label(self.optionsframe, text='Line Plot Estimator:').grid(row=1, column = 0)
        
        self.lineEstimator=tk.StringVar(self.optionsframe,'None')
        
        self.lestradio = tk.Radiobutton(self.optionsframe,text = 'None', variable = self.lineEstimator, value = 'None')
        self.lestradio.grid(row = 1, column = 2,sticky = 'w')
        
        self.lestradio = tk.Radiobutton(self.optionsframe,text = 'mean', variable = self.lineEstimator, value = 'mean')
        self.lestradio.grid(row = 1, column = 3, sticky = 'w')
        
        self.lestradio = tk.Radiobutton(self.optionsframe,text = 'median', variable = self.lineEstimator, value = 'median')
        self.lestradio.grid(row = 1, column = 4,sticky = 'w')
        
        
        self.label2 = tk.Label(self.optionsframe, text='Show OLS line?').grid(row=2, column = 0)
        
        self.do_ols=tk.StringVar(self.optionsframe,'No')
        
        self.olsradio = tk.Radiobutton(self.optionsframe,text = 'No', variable = self.do_ols, value = 'No')
        self.olsradio.grid(row = 2, column = 2,sticky = 'w')
        
        self.olsradio = tk.Radiobutton(self.optionsframe,text = 'Yes', variable = self.do_ols, value = 'Yes')
        self.olsradio.grid(row = 2, column = 3, sticky = 'w')
        
        
        

        self.label3 = tk.Label(self.optionsframe, text="Plot type: 2D Scatter Plot").grid(row = 0, column = 0)
        self.gobutton = tk.Button(self.optionsframe, text="Plot It!", command = self.plot2DScatter).grid(row=0,column = 6)
        
        self.titlelabel = tk.StringVar(self)
        self.label =tk.Label(self, text = 'Plot Title:').grid(row=0, column=7, sticky = 'w')
        self.gxlabel = tk.Entry(self, textvariable = self.titlelabel, width = 20)
        self.gxlabel.grid(row = 0, column = 8, sticky = 'w')


    def get2DScatterGridParms(self):
        
        self.regline = tk.StringVar(self,'No')
        self.reglabel = tk.Label(self.optionsframe, text = "Show regression line?").grid(row = 1, column = 0)
        self.regbutton = tk.Radiobutton(self.optionsframe, text= "Yes", variable = self.regline,value = "Yes" ).grid(row = 1,column = 1)
        self.regbutton = tk.Radiobutton(self.optionsframe, text= "No", variable = self.regline,value = "No" ).grid(row = 1,column = 2)
        
        #self.label = tk.Label(self.optionsframe, text="Plot type: 2D Line Plot Grid").grid(row = 0, column = 0)
        self.gobutton = tk.Button(self.optionsframe, text="Plot It!", command = self.plot2DScatterGrid).grid(row=0,column = 6)
        self.titlelabel = tk.StringVar(self)
        self.label =tk.Label(self, text = 'Plot Title:').grid(row=0, column=7, sticky = 'w')
        self.gxlabel = tk.Entry(self, textvariable = self.titlelabel, width = 20)
        self.gxlabel.grid(row = 0, column = 8, sticky = 'w')

    def get3DScatterParms(self):
        #self.label = tk.Label(self.optionsframe, text="Plot type: 3D Scatter Plot").grid(row = 0, column = 0)
        self.gobutton = tk.Button(self.optionsframe, text="Plot It!", command = self.plot3DScatter).grid(row=0,column = 6)
        self.titlelabel = tk.StringVar(self)
        self.label =tk.Label(self, text = 'Plot Title:').grid(row=0, column=7, sticky = 'w')
        self.gxlabel = tk.Entry(self, textvariable = self.titlelabel, width = 20)
        self.gxlabel.grid(row = 0, column = 8, sticky = 'w')

    def get3DSurfParms(self):
        #self.label = tk.Label(self.optionsframe, text="Plot type: 3D Surface Plot").grid(row = 0, column = 0)
        self.gobutton = tk.Button(self.optionsframe, text="Plot It!", command = self.plot3DSurf).grid(row=0,column = 6)
        self.titlelabel = tk.StringVar(self)
        self.label =tk.Label(self, text = 'Plot Title:').grid(row=0, column=7, sticky = 'w')
        self.gxlabel = tk.Entry(self, textvariable = self.titlelabel, width = 20)
        self.gxlabel.grid(row = 0, column = 8, sticky = 'w')
  
    def getBoxplotParms(self):
        #self.label = tk.Label(self.optionsframe, text="Plot type: Box Plot").grid(row = 0, column = 0)
        self.gobutton = tk.Button(self.optionsframe, text="Plot It!", command = self.plotBoxplot).grid(row=0,column = 6)
        self.titlelabel = tk.StringVar(self)
        self.label =tk.Label(self, text = 'Plot Title:').grid(row=0, column=7, sticky = 'w')
        self.gxlabel = tk.Entry(self, textvariable = self.titlelabel, width = 20)

        self.dodither = tk.StringVar(self.optionsframe, 'No')
        self.ditherlab= tk.Label(self.optionsframe, text = "Show Dithered Data Points?").grid(row = 1, column = 0, sticky = 'w')
        self.ditherbutton = tk.Radiobutton(self.optionsframe,text = 'Yes', variable = self.dodither, value = 'Yes')
        self.ditherbutton.grid(row = 1, column = 2, sticky = 'w')
        self.ditherbutton = tk.Radiobutton(self.optionsframe,text = 'No', variable = self.dodither, value = 'No')
        self.ditherbutton.grid(row = 1, column = 3, sticky = 'w')

        self.ditherseed = tk.StringVar(self.optionsframe, '12345')
        self.ditherseedlab= tk.Label(self.optionsframe, text = "Dither Seed:").grid(row = 2, column = 0, sticky = 'w')  
        self.ditherseedentry = tk.Entry(self.optionsframe, textvariable = self.ditherseed, width = 10)
        self.ditherseedentry.grid(row = 2, column = 2, sticky = 'w')

        self.ditherdotsize = tk.StringVar(self.optionsframe, '2')
        self.ditherdotlab= tk.Label(self.optionsframe, text = "Dither Dot Size:").grid(row = 2, column = 3, sticky = 'w')  
        self.ditherdotentry = tk.Entry(self.optionsframe, textvariable = self.ditherdotsize, width = 10)
        self.ditherdotentry.grid(row = 2, column = 5, sticky = 'w')




        self.gxlabel.grid(row = 0, column = 8, sticky = 'w')

    
    def getECDFParms(self):
        #self.label = tk.Label(self.optionsframe, text="Plot type: ECDF").grid(row = 0, column = 0)
        self.gobutton = tk.Button(self.optionsframe, text="Plot It!", command = self.plotECDF).grid(row=0,column = 6)
        self.titlelabel = tk.StringVar(self)
        self.label =tk.Label(self, text = 'Plot Title:').grid(row=0, column=7, sticky = 'w')
        self.gxlabel = tk.Entry(self, textvariable = self.titlelabel, width = 20)
        self.gxlabel.grid(row = 0, column = 8, sticky = 'w')

    
    def getHistogramParms(self):
        self.nobins = tk.StringVar(self,'auto')
        self.binlabel = tk.Label(self.optionsframe,text = "# of bins:")
        self.nobins = tk.Entry(self.optionsframe,textvariable = self.nobins,width = 6 )
        self.binlabel.grid(row = 0, column = 1)
        self.nobins.grid(row=0, column = 2)
                
        self.kdelabel = tk.Label(self.optionsframe,text="Add KDE overlay?").grid(row = 1, column = 0,sticky='w')
        self.dokde=tk.StringVar(self.optionsframe,'No')
        self.kderadio = tk.Radiobutton(self.optionsframe,text = 'Yes', variable = self.dokde, value = 'Yes')
        self.kderadio.grid(row = 1, column = 2,sticky = 'w')
        self.kderadio = tk.Radiobutton(self.optionsframe,text = 'No', variable = self.dokde, value = 'No')
        self.kderadio.grid(row = 1, column = 3,sticky = 'w')
        
        #self.label = tk.Label(self.optionsframe, text="Plot type = Histogram").grid(row = 0, column = 0)
        self.gobutton = tk.Button(self.optionsframe, text="Plot It!", command = self.plotHistogram).grid(row=0,column = 6)
        self.titlelabel = tk.StringVar(self)
        self.label =tk.Label(self, text = 'Plot Title:').grid(row=0, column=7, sticky = 'w')
        self.gxlabel = tk.Entry(self, textvariable = self.titlelabel, width = 20)
        self.gxlabel.grid(row = 0, column = 8, sticky = 'w')

###########################################################################
###  functions to do the plotting
###########################################################################
    def plot2DScatter(self):
        if (len(self.master.master.v1list) <=1): return
        vx = self.master.master.v1list[0]
        vy = self.master.master.v1list[1] 
        xv = vx.varname
        yv = vy.varname
        cv = self.master.master.selected_color_variable.get()
        mv = self.master.master.selected_marker_variable.get()
        rf = self.master.master.selected_col_variable.get()
        cf = self.master.master.selected_row_variable.get()
        #find the object for the "y" variable
        ytemp = vy.clickedGXmkr.get()
        #get the marker choice
        if ytemp == '': 
            ymarker = 'o'
        else:
            ymarker = markerdict[ytemp]
        #get the color choice
        ycolor =  vy.clickedGXcol.get()
        if ycolor == '': ycolor = 'black'
        ysize = vy.gxlsz.get()
        
        #get the plot type
        plot_type = self.plotchoice.get()
        
        #get rid of NA's report resulting sample size in nobs        
        vars = [xv, yv, cv, mv, rf, cf]
        if len(self.master.master.v1list) >= 3:
            nuvars = [item.varname for item in self.master.master.v1list[2:]]
            vars = vars + nuvars
        active_vars = [item for item in vars if (item != '')]        
        df0 = self.master.master.data
        nobs0 = len(df0)
        df = self.master.master.data[active_vars].dropna(subset = active_vars)
        nobs = len(df)
        
        #find the chosen style for y, use scatter as default
        vystemp = vy.clickedGXlnstyle.get()
        if vystemp == '': vystemp = 'scatter'
        
        #find the estimator to use for multiple values at a single  x point
        #when lineplotting        
        ltemp = self.lineEstimator.get()
        if ltemp == 'None' : 
            lin_est = None
        elif ltemp == 'median':
            lin_est = np.median
        else: 
            lin_est = 'mean'
            
        #finally get labels and titles
        xlab = vx.xlabel.get()
        ylab = vy.xlabel.get()
        
        #get the axis limits
        xlower = float(vx.gxlb.get())
        xupper = float(vx.gxub.get())
        ylower = float(vy.gxlb.get())
        yupper = float(vy.gxub.get())

        
        ptitle = f" Number of obs. = {nobs} out of {nobs0}"        
        user_title = self.titlelabel.get()
        if user_title != '':
            ptitle = user_title
            
        lg_msg= f" 2D Scatter Plot y= {yv}, x= {xv}, color= {cv}, marker= {mv}, rows= {rf}, cols= {cf}, Title: {ptitle}"
        gdata.log_It(lg_msg)


        #Now start plotting
        sfig = plt.figure(figsize = (8,8))
        ax = sfig.subplots()
        
        show_ols = self.do_ols.get()
        if (len(self.master.master.v1list)<3):
            if (mv != '') & (cv != ''):
                if vystemp == 'scatter':
                    if show_ols == 'No':
                        sb.scatterplot(df, x = xv, y= yv, hue = cv, style = mv, palette = 'bright', s = ysize, ax = ax)
                    else:
                        sb.regplot(df, x = xv, y=yv,  ax = ax, scatter_kws={'color': ycolor, 's':ysize})
                else:
                    sb.lineplot(df, x = xv, y= yv, hue = cv, style = mv, palette = 'bright', markersize = ysize, ax = ax)
            elif (mv == '') & (cv != ''):
                if vystemp == 'scatter':
                    if show_ols == 'No':
                        sb.scatterplot(df, x = xv, y= yv, hue = cv, palette = 'bright', s = ysize, ax = ax)
                    else:
                        sb.regplot(df, x = xv, y=yv,  ax = ax, scatter_kws={'color': ycolor, 's':ysize})
                else:
                    sb.lineplot(df, x = xv, y=yv, marker=ymarker, hue = cv, palette = 'bright', markersize = ysize, ax = ax )                
            elif (mv != '') & (cv == ''):
                if vystemp == 'scatter': 
                    if show_ols == 'No':
                        sb.scatterplot(df, x = xv, y = yv, style = mv, color = ycolor, s = ysize, ax = ax)
                    else:
                        sb.regplot(df, x = xv, y=yv,  ax = ax, scatter_kws={'color': ycolor, 's':ysize})
                else:
                    sb.lineplot(df, x = xv, y = yv, style = mv, color = ycolor, markersize = ysize, ax = ax)  
            else:
                if vystemp == 'scatter':
                    if show_ols == 'No':
                        sb.scatterplot(df, x = xv, y = yv, marker = ymarker, color = ycolor, s = ysize, ax = ax)
                    else:
                        sb.regplot(df, x = xv, y=yv,  ax = ax, scatter_kws={'color': ycolor, 's':ysize})
                else:
                    sb.lineplot(df, x = xv, y = yv, marker = ymarker, color = ycolor, markersize = ysize, ax = ax)                
        #now add line plots as needed
        else :
            for item in self.master.master.v1list[1:]:
                yv = item.varname
                ycolor = item.clickedGXcol.get()
                if ycolor == '': ycolor = 'black'
                
                ytemp = item.clickedGXmkr.get()                
                if ytemp == '':
                    ymarker = 'o'
                else:
                    ymarker = markerdict[ytemp]
                    
                ysz = item.gxlsz.get()
                
                ltemp = self.lineEstimator.get()
                if ltemp== 'None' : 
                    lin_est = None
                elif ltemp == 'median':
                    lin_est = np.median
                else: 
                    lin_est = 'mean'
        
                stemp = item.clickedGXlnstyle.get()
                if stemp == '': stemp = 'solid'
                if stemp == 'line': stemp = 'solid'
                    
                    
                if stemp != 'scatter':
                    sb.lineplot(df, x = xv, y= yv, color = ycolor, marker = ymarker, label = yv,
                             markersize = ysz, linestyle = stemp, ax=ax,estimator = lin_est)
                else:
                    sb.scatterplot(df, x = xv, y= yv, color = ycolor, marker = ymarker, label = yv,
                            s= ysz,  ax=ax)  
        ax.set_xlabel(xlab)
        ax.set_ylabel(ylab)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0)
        #ax.legend()
        ax.set_xlim(xlower,xupper)
        ax.set_ylim(ylower,yupper)
        sfig.suptitle(t = ptitle, y = 0.95)
        sfig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1) 
        sfig.show()
        return    
    
    
    def plot2DScatterGrid(self):
        if (len(self.master.master.v1list) <=1): return
        vx = self.master.master.v1list[0]
        vy = self.master.master.v1list[1] 
        xv = vx.varname
        yv = vy.varname
        cv = self.master.master.selected_color_variable.get()
        mv = self.master.master.selected_marker_variable.get()
        rf = self.master.master.selected_row_variable.get()
        cf = self.master.master.selected_col_variable.get()
        if cf == '' and rf == '': return
        #find the object for the "y" variable
        ytemp = vy.clickedGXmkr.get()
        doreg = self.regline.get()
        #replace cv if none supplied
        
        #get the marker choice
        if ytemp == '': 
            ymarker = 'o'
        else:
            ymarker = markerdict[ytemp]
        #get the color choice
        ycolor =  vy.clickedGXcol.get()
        if ycolor == '': ycolor = 'black'
        ysize = vy.gxlsz.get()

        
        #get the plot type
        plot_type = self.plotchoice.get()
        
        #get rid of NA's report resulting sample size in nobs        
        vars = [item for item in [xv, yv, cv, mv, rf, cf] if item !='']
        if len(self.master.master.v1list) >= 3:
            nuvars = [item.varname for item in self.master.master.v1list[2:]]
            vars = vars + nuvars
        active_vars = [item for item in vars if (item != '')]        
        df0 = self.master.master.data
        nobs0 = len(df0)
        df = self.master.master.data[active_vars].dropna(subset = active_vars)
        #if cv == '' create a column of 1's in df to display a single color.
        nobs = len(df)
        
        #set the color palette for automatic coloring
        palettenu = 'bright'
        
        #finally get labels and titles
        xlab = vx.xlabel.get()
        ylab = vy.xlabel.get()
        
        #get axis limits
        xlower = float(vx.gxlb.get())
        xupper = float(vx.gxub.get())
        ylower = float(vy.gxlb.get())
        yupper = float(vy.gxub.get())


        ptitle = f" Number of obs. = {nobs} out of {nobs0}"        
        user_title = self.titlelabel.get()
        if user_title != '':
            ptitle = user_title
        
        lg_msg= f" 2D Scatter Plot Grid: y= {yv}, x= {xv}, color= {cv}, marker= {mv}, rows= {rf}, cols= {cf}, Title: {ptitle}"
        gdata.log_It(lg_msg)


#### NB: Apparently, the marker variable is ignored in seaborn lmplot.  If you add a vector of markers it uses the
#### hue variable to choose marker types.  So I just ignore it. Colors are enough of a problem to manage.
    
        if cv != '':
        #now do the plot
            if doreg == 'Yes':
                if (rf != '') & (cf != ''):
                    g = sb.lmplot(df, x = xv, y= yv, hue = cv, palette = palettenu, row = rf, col=cf, scatter_kws={"s": ysize})
                elif (rf != '') & (cf == ''):
                    g = sb.lmplot(df, x = xv, y= yv, hue = cv, palette = palettenu, row = rf, scatter_kws={"s": ysize})                    
                elif (rf == '') & (cf!= '' ):
                    g = sb.lmplot(df, x = xv, y= yv, hue = cv, palette = palettenu, col = cf, scatter_kws={"s": ysize})                
                else:
                    return                                        
            else: 
                if (rf != '') & (cf != ''):
                    g = sb.relplot(df, x = xv, y= yv, hue = cv, palette = palettenu, row = rf, col=cf)
                elif (rf != '') & (cf == ''):
                    g = sb.relplot(df, x = xv, y= yv, hue = cv, palette = palettenu, row = rf)                    
                elif (rf == '') & (cf!= '' ):
                    g = sb.relplot(df, x = xv, y= yv, hue = cv, palette = palettenu, col = cf)                
                else:
                    return                                        
        else:
             #now do the plot
             if doreg == 'Yes':
                 if (rf != '') & (cf != ''):
                     g = sb.lmplot(df, x = xv, y= yv, scatter_kws={'color': ycolor, 's': ysize}, row = rf, col=cf)
                 elif (rf != '') & (cf == ''):
                     g = sb.lmplot(df, x = xv, y= yv, scatter_kws={'color': ycolor,'s': ysize}, row = rf)                    
                 elif (rf == '') & (cf!= '' ):
                     g = sb.lmplot(df, x = xv, y= yv, scatter_kws={'color': ycolor, 's': ysize},  col = cf)                
                 else:
                     return                                        
             else: 
                 if (rf != '') & (cf != ''):
                     g = sb.relplot(df, x = xv, y= yv,  color = ycolor, row = rf, col=cf)
                 elif (rf != '') & (cf == ''):
                     g = sb.relplot(df, x = xv, y= yv, color = ycolor, row = rf)                    
                 elif (rf == '') & (cf!= '' ):
                     g = sb.relplot(df, x = xv, y= yv, color = ycolor, col = cf, s =ysize)                
                 else:
                     return
        g.set(xlim=(xlower,xupper), ylim = (ylower, yupper))
        g.set_axis_labels(xlab, ylab)        
        g.fig.suptitle(ptitle, fontsize=12)
        g.fig.subplots_adjust(top=0.9);
        plt.show()
        return
                           
    def plot3DScatter(self):
        if (len(self.master.master.v1list) <=2): return
        vx = self.master.master.v1list[0]
        vy = self.master.master.v1list[1] 
        vz = self.master.master.v1list[2]
        xv = vx.varname
        yv = vy.varname
        zv = vz.varname
        cv = self.master.master.selected_color_variable.get()
        mv = self.master.master.selected_marker_variable.get()
        rf = self.master.master.selected_col_variable.get()
        cf = self.master.master.selected_row_variable.get()
        #find the object for the "y" variable
        ztemp = vz.clickedGXmkr.get()
        #get the marker choice
        if ztemp == '': 
            zmarker = 'o'
        else:
            zmarker = markerdict[ztemp]
        #get the color choice
        zcolor =  vz.clickedGXcol.get()
        if (zcolor == '') | (zcolor == '-'): zcolor = 'blue'
        zsize = vz.gxlsz.get()
        df = self.master.master.data
        
        #get the plot type
        plot_type = self.plotchoice.get()
        
        #get rid of NA's report resulting sample size in nobs        
        vars = [xv, yv, zv, cv, mv, rf, cf]
        if len(self.master.master.v1list) > 3:
            nuvars = [item.varname for item in self.master.master.v1list[3:]]
            vars = vars + nuvars
        active_vars = [item for item in vars if (item != '')]        
        df0 = self.master.master.data
        nobs0 = len(df0)
        df = df0[active_vars].dropna(subset = active_vars) 
        nobs = len(df)
        #find the chosen style for y, use scatter as default
        vystemp = vy.clickedGXlnstyle.get()
        if vystemp == '': vystemp = 'scatter'
        
        #finally get labels and titles
        xlab = vx.xlabel.get()
        ylab = vy.xlabel.get()
        zlab = vz.xlabel.get()
        
        xlower = float(vx.gxlb.get())
        xupper = float(vx.gxub.get())
        ylower = float(vy.gxlb.get())
        yupper = float(vy.gxub.get())
        zlower = float(vz.gxlb.get())
        zupper = float(vz.gxub.get())

        ptitle = f" Number of obs. = {nobs} out of {nobs0}"        
        user_title = self.titlelabel.get()
        if user_title != '':
            ptitle = user_title

        lg_msg= f" 3D Scatter Plot z= {zv}, y= {yv}, x= {xv}, color= {cv}, marker= {mv}, rows= {rf}, cols= {cf}, Title: {ptitle}"
        gdata.log_It(lg_msg)

        fig = plt.figure(figsize = (8,8))
        ax = fig.add_subplot(111, projection='3d')
        

        #now do the plots
#        ax.scatter(df[xv], df[yv], df[zv])# color = zcolor, marker='o', s=50, alpha=0.8)
#        plt.show()
        if cv != '':
            colorlist ,lpatches= getcolor(list(df[cv]))                         
            ax.scatter3D(df[xv], df[yv], df[zv], c = colorlist, marker=zmarker, s=zsize, alpha=0.8)
            legend1 = ax.legend(title = cv, handles = lpatches)
            ax.add_artist(legend1)

        else:
            ax.scatter3D(df[xv], df[yv], df[zv],color = zcolor,  marker=zmarker, s=zsize, alpha=0.8,label = zv)
            
            
        if (len(self.master.master.v1list) >= 3):
            for item in self.master.master.v1list[3:]:
                zv = item.varname
                zcolor = item.clickedGXcol.get()
                if zcolor == '': zcolor = 'black'
                
                ztemp = item.clickedGXmkr.get()                
                if ztemp == '':
                    zmarker = 'o'
                else:
                    zmarker = markerdict[ztemp]
                    
                zsz = item.gxlsz.get()
                        
                stemp = item.clickedGXlnstyle.get()
                if stemp == '': stemp = 'scatter'
                if stemp == 'line': stemp = 'solid'
                    
                    
                if stemp != 'scatter':
                    ax.plot_trisurf(df[xv], df[yv], df[zv], color = zcolor, label = zv, edgecolor = 'lightgrey')# edgecolor = 'black')
                             #markersize = ysz, linestyle = stemp, ax=ax,estimator = lin_est)
                else:
                    ax.scatter3D(df[xv], df[yv], df[zv], color = zcolor, marker = zmarker, label = zv,
                            s= zsz, alpha = 0.8)  
        ax.set_xlabel(xlab)
        ax.set_ylabel(ylab)
        ax.set_zlabel(zlab)
        ax.set_title(ptitle)
        ax.set_xlim(xlower,xupper)
        ax.set_ylim(ylower,yupper)
        ax.set_zlim(zlower,zupper)
        plt.legend()
        plt.show()
        return
    
    def plot3DSurf():
        #finally get labels and titles
        #xlab = vx.xlabel.get()
        #ylab = vy.xlabel.get()

        pass
    
        
    def plotECDF(self):
        #get the variable data
        if (len(self.master.master.v1list) == 0): return
        v1 = self.master.master.v1list[0]
        xv = v1.varname
        cv = self.master.master.selected_color_variable.get()
        mv = self.master.master.selected_marker_variable.get()
        rf = self.master.master.selected_col_variable.get()
        cf = self.master.master.selected_row_variable.get()
        plot_type = self.plotchoice.get()
        
        #get rid of NA's report resulting sample size in nobs        
        vars = [xv, cv, mv, rf, cf]
        active_vars = [item for item in vars if (item != '')]        
        df0 = self.master.master.data
        nobs0 = len(df0)
        df = self.master.master.data[active_vars].dropna(subset = active_vars)   
        nobs = len(df)
        
        #finally get labels and titles
        xlab = v1.xlabel.get()
        
        xupper = float(v1.xub.get())
        xlower = float(v1.xlb.get())

        
        ptitle = f" Number of obs. = {nobs} out of {nobs0}"        
        user_title = self.titlelabel.get()
        if user_title != '':
            ptitle = user_title

        lg_msg= f" Empirical CDF Plot:  x= {xv}, color= {cv}, marker= {mv}, rows= {rf}, cols= {cf}, Title: {ptitle}"
        gdata.log_It(lg_msg)
    
        #now do the plotting
        if (rf == '') & (cf ==''):
            if cv == '':
                fg = sb.displot(df, x= xv,kind = 'ecdf')
            else:
                fg = sb.displot(df, x= xv, hue = cv, kind = 'ecdf', palette='bright')
        elif (cf == '') & (rf != ''):
            if (cv != ''):
                fg = sb.displot(df, x=xv, hue = cv, row = rf, kind = 'ecdf', palette='bright')
            else:
                fg = sb.displot(df, x=xv, row = rf, kind = 'ecdf')
        elif (cf != '') & (rf == ''):
            if (cv!= ''):
                fg = sb.displot(df, x=xv, hue = cv, row = cf, kind = 'ecdf', palette='bright')
            else:
                fg = sb.displot(df, x=xv, row = cf, kind = 'ecdf')                
        else:
            if (cv != ''):
                fg = sb.displot(df, x=xv, hue = cv, row = rf, col = cf, kind = 'ecdf', palette='bright')
            else:
                fg = sb.displot(df, x=xv, row = rf, col = cf, kind = 'ecdf')
                
        fg.set_axis_labels(xlab,'Cumulative Probability')
        #fg.set(xlim=(xlower,xupper))
        plt.xlim(xlower, xupper)
        plt.suptitle(t = ptitle, y = 0.95)
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1) 

        plt.show()
        return
    
    
    

    def plotBoxplot(self):
        #get the seed for dithering
        DOTSIZE= int(self.ditherdotsize.get())
        RSEED = int(self.ditherseed.get())
        np.random.seed(RSEED)
        #get the variable data
        if (len(self.master.master.v1list) == 0): return
        v1 = self.master.master.v1list[0]
        xv = v1.varname
        cv = self.master.master.selected_color_variable.get()
        mv = self.master.master.selected_marker_variable.get()
        rf = self.master.master.selected_col_variable.get()
        cf = self.master.master.selected_row_variable.get()
        
        plot_type = self.plotchoice.get()
        
        #get rid of NA's report resulting sample size in nobs        
        vars = [xv, cv, mv, rf, cf]
        active_vars = [item for item in vars if (item != '')]        
        df0 = self.master.master.data
        nobs0 = len(df0)
        df = self.master.master.data[active_vars].dropna(subset = active_vars)
        nobs = len(df)

        #finally get labels and titles
        ylab = v1.xlabel.get()
        xlab = cv
        
        ptitle = f" Number of obs. = {nobs} out of {nobs0}"        
        user_title = self.titlelabel.get()
        if user_title != '':
            ptitle = user_title

        lg_msg= f" Box Plot y= {xv}, x= {cv}, color= {cv}, marker= {mv}, rows= {rf}, cols= {cf}, Title: {ptitle}"
        gdata.log_It(lg_msg)
        
        nuname = ''
        if (cv == ''):
            nuname = newname(df, 'A_col')
            df[nuname] = ['A']*len(df)

        #now do the plotting
        if (rf == '') & (cf ==''):
            if cv == '':
                fg = sb.catplot(data = df, y= xv,fill = True, kind = 'box')
                if self.dodither.get() == 'Yes': 
                    np.random.seed(RSEED)
                    fg.map_dataframe(sb.stripplot, data=df, y=xv,jitter=True, alpha=0.6, size=DOTSIZE,color = 'black')
            else:
                fg = sb.catplot(df, x=cv ,y=xv, fill = True, hue = cv, palette='bright', kind = 'box')
                if self.dodither.get() == 'Yes': 
                    np.random.seed(RSEED)
                    fg.map_dataframe(sb.stripplot, data=df, y=xv, x=cv, jitter=True, alpha=0.6, size=DOTSIZE, color = 'black')
        elif (cf == '') & (rf != ''):
            if (cv == ''):
                fg = sb.catplot(data=df, x=nuname, y=xv,  row = rf,fill=True, kind = 'box')
                if self.dodither.get() == 'Yes': 
                    np.random.seed(RSEED)
                    fg.map_dataframe(sb.stripplot, nuname, xv, jitter=True, alpha=0.6, size=DOTSIZE, color = 'black', order = ['A'])
            else:
                fg = sb.catplot(df, y=xv, x=cv, row = rf, hue = cv, palette = 'bright', kind = 'box')
                if self.dodither.get() == 'Yes': 
                    np.random.seed(RSEED)
                    fg.map_dataframe(sb.stripplot, y=xv, x=cv, jitter=True, alpha=0.6, size=DOTSIZE, color = 'black')
        elif (cf != '') & (rf == ''):
            if (cv== ''):
                fg = sb.catplot(df, y=xv, col = cf, kind = 'box')
                if self.dodither.get() == 'Yes': 
                    np.random.seed(RSEED)
                    fg.map_dataframe(sb.stripplot, data=df, y=xv, x=cf, jitter=True, alpha=0.6, size=DOTSIZE, color = 'black')
            else:
                fg = sb.catplot(df, y=xv, col = cf, x=cv, hue = cv, palette='bright', kind = 'box')
                if self.dodither.get() == 'Yes': 
                    np.random.seed(RSEED)
                    fg.map_dataframe(sb.stripplot, y=xv, x=cv, jitter=True, alpha=0.6, size=DOTSIZE, color = 'black')
        else:
            if (cv == ''):
                fg = sb.catplot(df, y=xv,  row = rf, col = cf, kind = 'box')
            else:
                fg = sb.catplot(df, y=xv, hue = cv, row = rf, col = cf, palette='bright',kind = 'box')
        fg.set_axis_labels(xlab,ylab)
        #fg.set(xlim=(xlower,xupper))
        plt.suptitle(t = ptitle, y = 0.95)
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1) 

        plt.show()
        return

    
    def plotHistogram(self,*args):# finally we're going to make a plot happen!
        #get the variable data
        if (len(self.master.master.v1list) == 0): return
        v1 = self.master.master.v1list[0]
        xv = v1.varname
        cv = self.master.master.selected_color_variable.get()
        mv = self.master.master.selected_marker_variable.get()
        rf = self.master.master.selected_col_variable.get()
        cf = self.master.master.selected_row_variable.get()
        
        plot_type = self.plotchoice.get()
        
        vars = [xv, cv, mv, rf, cf]
        
        active_vars = [item for item in vars if (item != '')]
        
        df0 = self.master.master.data
        nobs0 = len(df0)
        df = self.master.master.data[active_vars].dropna(subset = active_vars) 
        nobs = len(df)
        
        
        xupper = float(v1.xub.get())
        xlower = float(v1.xlb.get())

        #set some local histogram parameters
        #override bins
        nbins= self.nobins.get()
        if nbins != 'auto': nbins = int(nbins)
        #add a kde plot
        KDE = False
        if self.dokde.get() == 'Yes': KDE = True
        
        #dfig = self.master.master.fig 
        #axh = self.master.master.ax
        #axh.clear()
        
        #finally get labels and titles
        xlab = v1.xlabel.get()
        
        ptitle = f" Number of obs. = {nobs} out of {nobs0}"        
        user_title = self.titlelabel.get()
        if user_title != '':
            ptitle = user_title

        
        #now do the plotting
        if (rf == '') & (cf ==''):
            if cv == '':
                #ax = sb.histplot(df, x= xv,kde = KDE, fill = True, ec = 'black', lw = 1, bins = nbins)
                fg = sb.displot(df, x=xv,  kde = KDE, bins = nbins, facet_kws=dict(margin_titles=True))
            else:
                #ax = sb.histplot(df, x= xv, hue = cv, kde = KDE, fill = True, palette='bright', ec = 'black', lw = 1, bins = nbins)
                fg = sb.displot(df, x=xv, hue = cv, kde = KDE,bins = nbins, palette = 'bright', facet_kws=dict(margin_titles=True))
        elif (cf == '') & (rf != ''):
            if (cv != ''):
                fg = sb.displot(df, x=xv, hue = cv, row = rf, kde = KDE,bins = nbins,palette = 'bright', facet_kws=dict(margin_titles=True))
            else:
                fg = sb.displot(df, x=xv, row = rf, kde = KDE,bins = nbins, facet_kws=dict(margin_titles=True))
        elif (cf != '') & (rf == ''):
            if (cv!= ''):
                fg = sb.displot(df, x=xv, hue = cv, row = cf, kde = KDE,bins = nbins, palette = 'bright', facet_kws=dict(margin_titles=True))
            else:
                fg = sb.displot(df, x=xv, row = cf, kde = KDE,bins = nbins, facet_kws=dict(margin_titles=True))                
        else:
            if (cv != ''):
                fg = sb.displot(df, x=xv, hue = cv, row = rf, col = cf, kde = KDE,bins = nbins,palette = 'bright',  facet_kws=dict(margin_titles=True))
            else:
                fg = sb.displot(df, x=xv, row = rf, col = cf, kde = KDE,bins = nbins, facet_kws=dict(margin_titles=True))
                
        #ax.set_xlabel(xlab)
        fg.set_axis_labels(xlab, 'Count')
        fg.set(xlim=(xlower,xupper))
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1) 
        plt.suptitle(t = ptitle, y = 0.95)

        plt.show()
        return


if __name__ == "__main__":
    gdata = gd.globalData()
    class solo(tk.Tk):
        def __init__(self):
            super().__init__()
            self.title("Data Plot Stand Alone App")
            self.onButton = tk.Button(self, text = "Get Data", command = self.getData).pack(side = tk.LEFT, padx = 10)
            self.goPivot  = tk.Button(self, text = "Plot Data", command = self.pivD).pack(side = tk.LEFT, padx = 10)
            self.offButton = tk.Button(self, text="Graceful Exit", command = self.quit).pack(side = tk.LEFT, padx = 10)

            
            #gst = goPivot(self)
        
        def pivD(self,*args):
            if len(gdata.data) == 0: return
            self.gst = goPlot()
            self.gst.syncData()

                        
        def quit(self,*args):
            plt.close('all')
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
                #self.doReset(df_in)
                gdata.reset_Data(file_path, df_in)
            return
            

    app = solo()
    app.mainloop()



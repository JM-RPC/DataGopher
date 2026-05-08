#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  2 09:06:58 2025

@author: Knucklehead
"""

# from patsy import dmatrices, NAAction
# from sklearn.metrics import roc_curve, auc
import sys
from datetime import datetime

import pandas as pd
from pandas.api.types import is_numeric_dtype
import numpy as np
import scipy
from scipy.interpolate import griddata
import statsmodels.api as sm

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from mpl_toolkits.mplot3d import Axes3D
#from matplotlib.backends.backend_tkagg import (
#    FigureCanvasTkAgg,  # interface between Figure class and Tkinter's Canvas
#    NavigationToolbar2Tk  # built-in toolbar for the figure
#)
import seaborn as sb
sb.set_style("darkgrid", {"grid.color": ".6", "grid.linestyle": ":"})



from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression

#local imports
import Graphics as grp

import globalData as gd
from globalData import gdata


HAVELOESS2D = False
emsg = ''
loess_msg = "LOESS_2D routine of Cappellari et al. (2013b), which implements \nthe multivariate LOESS algorithm of Cleveland & Devlin (1988)"
try:
    from loess.loess_2d import loess_2d
    HAVELOESS2D = True
except ImportError:
    emsg = "Non-fatal Warning: loess.loess_2d package not installed. \n Loess smoothing for 3D plots will not be available."
    emsg = "\ninstall from: https://pypi.org/project/loess/  using pip install loess in your environment."
    print(emsg)

# import scipy





# import DataRead as dr
# from Regression import imdl

colorlim = 1000

baselinestyles = ['solid', 'dashed', 'dotted', 'dashdot']


smootherwl= ['None', 'mean', 'median', 'loess', 'polynomial']
smoothernl= ['None', 'mean', 'median', 'polynomial']


basecolors0 = ['blue', 'red',  'green', 'yellow', 'magenta', 'cyan', 'violet',
               'orange',  'goldenrod', 'grey', 'gold', 'silver', 'orangered', 'darkolivegreen',
               'olive', 'khaki', 'thistle', 'lightsteelblue', 'slateblue', 'black', 'darkviolet',
               'brown', 'indigo', 'hotpink', 'lavender']


gphIndex = ['V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7', 'V8', 'V9', 'V10']

markers0 = ['.', 'o', 'v', '^', '<', '>', '8',
            's', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'X']

marker_names = ['point', 'filled dot', 'triangle_d', 'triangle_u', 'triangle_l', 'triangle_r',
                'octagon',     'square',   'pentagon',       'star',  'hexagon_1',  'hexagon_2', 'diamond_1',
                'diamond_2',     'plus',   'x']

plot_types = ['-', 'Boxplot', 'Histogram', 'ECDF',
              '2D Line/Scatter Plot', '2D Scatter Grid', '3D Scatter Plot']
markerdict = {name: marker for name, marker in zip(marker_names, markers0)}

# Helper function for 3D color plotting
basecolornos = [matplotlib.colors.to_rgba(
    item, alpha=None) for item in basecolors0]




def newname(df=pd.DataFrame(), newname=''):
    if newname == '':
        return
    if len(df) == 0:
        return
    names = list(df.columns)
    if newname not in names:
        return (newname)
    idx = 0
    while newname in names:
        newname += str(idx)
        idx += 1
    return (newname)


# ROWLENGTH and getRowCol control the display of numeric variables (rows and 
# columns) in the plotting variable choice frame
ROWLENGTH = 4


def getRowCol(idx, rowlength=4):
    row = int(idx/rowlength)
    col = idx - row*rowlength
    return row, col


# class goPlot(tk.Tk):
class goPlot(tk.Toplevel):
    def __init__(self):
        super().__init__()
        
        #self.option_add("*Background", "lightblue")
        #self.option_add("*Button.Background", "lightblue")
        #self.option_add("Button.background.highlightbackground", "lightblue")


        self.title('Data Plotter Prototype')
        self.resizable(True, True)
        self.current_data = pd.DataFrame()
        # self.geometry('1100x400')

        # self.fig = plt.figure(figsize = (8,8), num = 1)
        # self.ax = self.fig.add_subplot()
        # kill window and clean up plots on exit button
        self.protocol('WM_DELETE_WINDOW', self.exit_closing)
        self.plot_type = ''

        self.f0a = tk.Frame(self)
        self.f0a.grid_rowconfigure(0, weight=1)
        self.f0a.grid_columnconfigure(0, weight=1)
        # self.testlab = tk.Label(self.f0a, text="This is frame f0a").grid(row = 0, column=1)

        self.f0a.configure(borderwidth=2, relief="ridge", highlightthickness=1)
        # , padx = 10, pady = 10)
        self.f0a.pack(side=tk.TOP, anchor='nw', expand=False)

        # self.file_button = tk.Button(self.f0,text= 'Sync Data',command = self.syncData)
        # self.file_button.grid(row = 0, column = 0, sticky = 'w',padx=10)

        self.fname_label = tk.Label(self.f0a, text='')
        self.fname_label.grid(row=0, column=1, columnspan=3)
        self.clear_button = tk.Button(self.f0a, text='Clear Last Variable', 
                                      command=self.clearIt)
        self.clear_button.grid(row=0, column=8, sticky='e', padx=10)
        self.plot_savedata = tk.Button(self.f0a, text="Save Current Plotting Data", command = self.saveData).grid(row=4, column=0)

        # now a variable chooser
        self.selected_variable = tk.StringVar(value='')
        self.Label1 = tk.Label(
            self.f0a, text='Select Numerical Variables:').grid(row=1, column=0)
        self.options = ttk.Combobox(
            self.f0a, values=[], textvariable=self.selected_variable)
        self.options.grid(row=1, column=1, columnspan=3, sticky='w')
        self.options.bind("<<ComboboxSelected>>", self.varupdate)

        # now a parameter chooser (color, marker, facet etc.)
        # self.current_parms = []
        self.selected_color_variable = tk.StringVar(value='-')
        self.Label2 = tk.Label(
            self.f0a, text='Color Variable:').grid(row=1, column=4)
        self.copts = ttk.Combobox(
            self.f0a, values=[], textvariable=self.selected_color_variable)
        self.copts.grid(row=1, column=5)
        self.Label2b = tk.Label(self.f0a, text=f" {colorlim} colors max").grid(
            row=1, column=8, sticky='w')
        self.copts.bind("<<ComboboxSelected>>", self.parmupdate)

        self.f0_2d = tk.Frame(self.f0a)
        self.f0_2d.grid_rowconfigure(0, weight=1)
        self.f0_2d.grid_columnconfigure(0, weight=1)

        self.f0_2d.configure(
            borderwidth=0, highlightthickness=0, relief="flat")
        # self.f0.pack(side = tk.TOP, anchor = 'nw', expand = False) #, padx = 10, pady = 10)
        # self.f0.pack_forget()
        # self.f0.grid(row =2, column = 4, columnspan = 4, sticky = 'w')
        self.f0_2d.grid_forget()

        self.f0_2dg = tk.Frame(self.f0a)
        self.f0_2dg.grid_rowconfigure(0, weight=1)
        self.f0_2dg.grid_columnconfigure(0, weight=1)

        self.f0_2dg.configure(
            borderwidth=0, highlightthickness=0, relief="flat")
        # self.f0.pack(side = tk.TOP, anchor = 'nw', expand = False) #, padx = 10, pady = 10)
        # self.f0.pack_forget()
        # self.f0.grid(row =2, column = 4, columnspan = 4, sticky = 'w')
        self.f0_2dg.grid_forget()

        self.selected_marker_variable = tk.StringVar(value='')
        self.Label3 = tk.Label(self.f0_2d, text='Marker  Variable')
        self.Label3.grid(row=2, column=4)
        self.mopts = ttk.Combobox(
            self.f0_2d, values=[], textvariable=self.selected_marker_variable)
        self.mopts.grid(row=2, column=5)
        self.Label3b = tk.Label(self.f0_2d, text=f" {len(markers0)} markers max").grid(
            row=2, column=8, sticky='w')
        self.mopts.bind("<<ComboboxSelected>>", self.parmupdate)

        maxfacet = min(len(markers0), len(basecolors0))
        self.selected_row_variable = tk.StringVar(value='-')
        self.Label4 = tk.Label(
            self.f0_2dg, text='Row Facet Variable:').grid(row=3, column=4)
        self.fropts = ttk.Combobox(
            self.f0_2dg, values=[], textvariable=self.selected_row_variable)
        self.fropts.grid(row=3, column=5)
        self.Label4b = tk.Label(self.f0_2dg, text=f" {maxfacet} row facets max").grid(
            row=3, column=8, sticky='w')
        self.fropts.bind("<<ComboboxSelected>>", self.parmupdate)

        self.selected_col_variable = tk.StringVar(value='-')
        self.Label5 = tk.Label(
            self.f0_2dg, text='Column Facet Variable:').grid(row=4, column=4)
        self.fcopts = ttk.Combobox(
            self.f0_2dg, values=[], textvariable=self.selected_col_variable)
        self.fcopts.grid(row=4, column=5)
        self.Label5b = tk.Label(self.f0_2dg, text=f" {maxfacet} column facets max").grid(
            row=4, column=8, sticky='w')
        self.fcopts.bind("<<ComboboxSelected>>", self.parmupdate)

        self.varlist = []
        self.varno = 0
        self.v1list = []

        self.f1 = tk.Frame(self)
        self.f1.configure(borderwidth=2, relief="ridge", highlightthickness=1)
        # self.testlab = tk.Label(self.f1, text="This is frame f1").grid(row = 0, column=1)
        # , padx = 10 , pady=10)
        self.f1.pack(side=tk.TOP, anchor='nw', expand=True)
        self.f2 = tk.Frame(self)
        self.f2.configure(borderwidth=2, relief="ridge", highlightthickness=1)
        self.f2.pack(side=tk.TOP, anchor='nw', expand=True)
        self.f3 = tk.Frame(self)
        self.f3.configure(borderwidth=2, relief="ridge", highlightthickness=1)
        self.f3.pack(side=tk.TOP, anchor='nw', expand=True)

        self.gp1 = gPlot(self.f3)
        self.gp1.pack_forget()

        # get the data from gdata
        self.syncData()

        return

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
        remaining_varlist = [
            item for item in self.varlist0 if item not in self.current_varlist]
        self.options['values'] = remaining_varlist
        self.options.set("")
        self.parmupdate(None)


    def saveData(self, *args):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[('Text Files', '*.txt'),
                       ('All Files', '*.*'), ('CSV Files', '*.csv')],
            initialfile = f"DG_PlotData_{datetime.now().strftime("%Y-%m-%d@%H-%M-%S")}.csv"
        )
        if (len(self.current_data) == 0): return
        self.current_data.to_csv(file_path)
        gdata.log_It(f"Plotting Data Saved to: {file_path}")
        gdata.code_It(f"#Plotting Data Saved to: {file_path}")
        return

    def doReset(self, DATA, *args):
        while len(self.v1list) > 0:
            self.clearIt()
        self.data = DATA
        self.current_data = pd.DataFrame()
        self.varlist0 = [
            item for item in self.data.columns if is_numeric_dtype(self.data[item])]
        self.marklist0 = [item for item in list(self.data.columns) if len(
            self.data[item].unique()) <= len(markers0)]
        # self.colorlist0 = [item for item in list(self.data.columns) if len(self.data[item].unique()) <=len(basecolors0)]
        # arbitrary limit 1000 different colors
        self.colorlist0 = [item for item in list(
            self.data.columns) if len(self.data[item].unique()) <= 1000]
        maxfacet = min(len(markers0), len(basecolors0))
        self.facetlist0 = [item for item in list(self.data.columns) if len(
            self.data[item].unique()) <= maxfacet]
        self.options['values'] = self.varlist0
        self.mopts['values'] = ['-'] + self.marklist0
        self.copts['values'] = ['-'] + self.colorlist0
        self.fropts['values'] = ['-'] + self.facetlist0
        self.fcopts['values'] = ['-'] + self.facetlist0
        self.selected_color_variable.set('-')
        self.selected_marker_variable.set('-')
        self.selected_row_variable.set('-')
        self.selected_col_variable.set('-')
        self.current_varlist = []
        self.gp1.pack(side=tk.BOTTOM, anchor='sw')  # start the plotting stuff
        self.fname_label.config(text="File: " + self.fpath)
        plt.close('all')
        return


    def syncData(self, *arg):
        if len(gdata.data) > 0:
            self.fpath = gdata.fpath
            self.doReset(gdata.data.copy(deep = True))
        return

    def varupdate(self, event):
        newvar = str(self.selected_variable.get())
        if newvar == '':
            return
        if newvar == '-':
            return

        # add newvar to the list of current variables if it is new
        if newvar in self.current_varlist:
            return
        self.current_varlist.append(newvar)

        # now reset the remaining variable choices
        remaining_varlist = [
            item for item in self.varlist0 if item not in self.current_varlist]
        self.options['values'] = remaining_varlist
        self.options.set("")

        # now create an instance v1, of a  variable object (gVar) to hold variable info and append it to the list
        # of active variables (v1list), then unpack and repack all the variables.
        # print(f"newvar = {newvar}")
        self.v1 = gVar(self.f1, varname=newvar)
        # self.v1.pack(side = tk.LEFT, anchor = 'w')
        self.v1list.append(self.v1)
        # unpack
        for item in self.v1list:
            item.grid_forget()
        # repack
        for idx, item in enumerate(self.v1list):
            r, c = getRowCol(idx, rowlength=ROWLENGTH)
            item.grid(row=r, column=c, sticky='w')
            # item.pack(side = tk.LEFT, anchor = 'w')
            if idx == 0:
                item.mframe.grid_forget()
                item.mframe2.grid_forget()
            elif (idx == 1) & (self.plot_type in ['3D Scatter Plot', '3D Surface Plot']):
                item.mframe.grid_forget()
                item.mframe2.grid_forget()
            elif (idx == 1) & (self.plot_type in ['2D Line/Scatter Plot']):
                item.mframe.grid(row=4, column=0, rowspan=3,
                                 columnspan=2, sticky='w')
                item.mframe2.grid(row=7, column=0, rowspan=3,
                                  columnspan=2, sticky='w')
            elif (idx >= 2) & (self.plot_type in ['3D Scatter Plot', '3D Surface Plot', '2D Line/Scatter Plot']):
                item.mframe.grid(row=4, column=0, rowspan=3,
                                 columnspan=2, sticky='w')
                item.mframe2.grid(row=7, column=0, rowspan=3,
                                  columnspan=2, sticky='w')
            else:
                item.mframe.grid_forget()
                item.mframe2.grid_forget()

        # if there are no variables in v1list then kill the plot choice window
        if (len(self.v1list) == 0):
            for item in self.f3.winfo_children():
                item.destroy()
        self.parmupdate(None)
        return

    # makes the entries in the color variable, marker variable, and facet variables unique
    def parmupdate(self, event):

        current_vars = [v.varname for v in self.v1list]

        current_parms = [self.selected_col_variable.get(), self.selected_row_variable.get(),
                         self.selected_color_variable.get(), self.selected_marker_variable.get()]

        marker_var = [
            item for item in self.marklist0 if item not in current_parms]
        color_var = [
            item for item in self.colorlist0 if item not in current_parms + current_vars]
        facet_var = [
            item for item in self.facetlist0 if item not in current_parms]

        self.mopts['values'] = ['-'] + marker_var
        self.copts['values'] = ['-'] + color_var
        self.fropts['values'] = ['-'] + facet_var
        self.fcopts['values'] = ['-'] + facet_var

        # now adjust the numerical variable choice list to reflect current variable and parameter choices
        remaining_varlist = [
            item for item in self.varlist0 if item not in current_parms + current_vars]

        self.options['values'] = remaining_varlist
        self.options.set("")  # sets text entry for options widget to blank


class gVar(tk.Frame):
    def __init__(self, parent, varname=None):
        super().__init__(master=parent)

        self.clickedGX = tk.StringVar()

        self.configure(borderwidth=2, relief="ridge", highlightthickness=1)
        # gphvars = list(self.master.varlist0)

        # nameing convention for variables
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

        # self.clickedGX = tk.StringVar()
        self.gxlab = tk.Label(self, text=namesuffix + ": " + varname)
        self.gxlab.grid(row=0, column=0, sticky='w', padx=20)
        if is_numeric_dtype(self.master.master.data[varname]):
            vmin = np.nanmin(self.master.master.data[varname])
            vmax = np.nanmax(self.master.master.data[varname])
        else:
            vmin = 0
            vmax = 0

        self.xub = tk.DoubleVar(self, vmax)
        self.gxupper = tk.Label(self, text='Upper lim:').grid(
            row=1, column=0, sticky='w')
        self.gxub = tk.Entry(self, textvariable=self.xub, width=10)
        self.gxub.grid(row=1, column=1, sticky='w')

        self.xlb = tk.DoubleVar(self, vmin)
        self.gxlow = tk.Label(self, text="Lower lim:").grid(
            row=2, column=0, sticky='w')
        self.gxlb = tk.Entry(self, textvariable=self.xlb, width=10)
        self.gxlb.grid(row=2, column=1, sticky='w')

        self.xlabel = tk.StringVar(value=varname)
        self.label = tk.Label(self, text='Axis Label:').grid(
            row=3, column=0, sticky='w')
        self.gxlabel = tk.Entry(self, textvariable=self.xlabel, width=12)
        self.gxlabel.grid(row=3, column=1, sticky='w')

        # First subframe
        self.mframe = tk.Frame(self)
        self.mframe.grid(row=4, column=0, rowspan=3, columnspan=2, sticky='w')

        self.clickedGXmkr = tk.StringVar(value='-')
        self.gxmkrl = tk.Label(self.mframe, text='Marker:')
        self.gxmkrl.grid(row=1, column=0, sticky='w')
        self.gxmkr = tk.OptionMenu(
            self.mframe, self.clickedGXmkr, *(['-'] + marker_names))
        self.gxmkr.grid(row=1, column=1, sticky='w')

        self.clickedGXcol = tk.StringVar(value='-')
        self.gxlabcolor = tk.Label(self.mframe, text="Color:").grid(
            row=1, column=2, sticky='w')
        self.gxcolor = tk.OptionMenu(
            self.mframe, self.clickedGXcol, *(['-'] + basecolors0))
        self.gxcolor.grid(row=1, column=3, sticky='w')

        self.gxszsld = tk.Label(self.mframe, text='Marker Size:')
        self.gxszsld.grid(row=2, column=0, sticky='w')
        self.gxlsz = tk.Scale(self.mframe, from_=0.25,
                              to=100, orient='horizontal', showvalue=True)
        self.gxlsz.grid(row=2, column=1, columnspan=2, sticky='w')
        self.gxlsz.set(5)

        self.gxsmootherscttrlab = tk.Label(
            self.mframe, text="Show scatter plot?").grid(row=3, column=0, sticky='w')
        self.gxsmootherscatter = tk.StringVar(value='Yes')
        self.gxsmthci1 = tk.Radiobutton(
            self.mframe, text="Yes", variable=self.gxsmootherscatter, value='Yes').grid(row=3, column=1, sticky='w')
        self.gxsmthci2 = tk.Radiobutton(
            self.mframe, text="No", variable=self.gxsmootherscatter, value='No').grid(row=3, column=2, sticky='w')

        # Second subframe
        self.mframe2 = tk.Frame(self)
        self.mframe2.grid(row=7, column=0, rowspan=3, columnspan=2, sticky='w')
        self.clickedGXlnstyle = tk.StringVar(value='-')
        self.gxlnstylel = tk.Label(self.mframe2, text='Surf/Line Type:')
        self.gxlnstylel.grid(row=1, column=0, sticky='w')
        self.gxlnstyle = ttk.Combobox(self.mframe2, values=[
                                      '-'] + baselinestyles, textvariable=self.clickedGXlnstyle, width=6)
        self.gxlnstyle.grid(row=1, column=1, sticky='w', padx=5)

        self.clickedGXlncolor = tk.StringVar(value='-')
        self.gxlncolorl = tk.Label(self.mframe2, text=" Color:")
        self.gxlncolorl.grid(row=1, column=2, sticky='w')
        self.gxlncolor = tk.OptionMenu(
            self.mframe2, self.clickedGXlncolor, *(['-'] + basecolors0))
        self.gxlncolor.grid(row=1, column=3, sticky='w', padx=5)

        # self.glinelab = tk.Label(self.mframe2, text = 'Line Plot Parameters:')
        # self.glinelab.grid(row = 4, column = 0, sticky = 'w')

        self.gxestlab = tk.Label(self.mframe2, text='Estimator/Smoother:')
        self.gxestlab.grid(row=2, column=0, sticky='w')
        self.gxlineest = tk.StringVar(value='-')

        self.gxlnest = ttk.Combobox(self.mframe2, values=smootherwl, textvariable=self.gxlineest, width=8)
        self.gxlnest.grid(row=2, column=1, sticky='w', padx=5)

        # self.gxestr1 = tk.Radiobutton(self.mframe2, text = 'none', variable = self.gxlineest, value='None').grid(row = 2, column = 1)
        # self.gxestr1 = tk.Radiobutton(self.mframe2, text = 'mean', variable = self.gxlineest, value='mean').grid(row = 2, column = 2)
        # self.gxestr1 = tk.Radiobutton(self.mframe2, text = 'median', variable = self.gxlineest, value='median').grid(row = 2, column = 3)

        # self.gxsmoothlab = tk.Label(self.mframe2,text="Smoother:")
        # self.gxsmoothlab.grid(row=3, column = 0, sticky = 'w')
        # self.gxsmoother = tk.StringVar(value='None')
        # smthvals = ['None', 'loess', 'polynomial']
        # self.gxlnest = ttk.Combobox(self.mframe2, values = smthvals, textvariable = self.gxsmoother, width = 6)
        # self.gxlnest.grid(row = 3, column =1, sticky = 'w',padx = 5)

        # self.gxsmoother1 = tk.Radiobutton(self.mframe2,text = 'none', variable=self.gxsmoother, value = 'None' ).grid(row = 3, column=1)
        # self.gxsmoother2 = tk.Radiobutton(self.mframe2,text = 'loess', variable=self.gxsmoother, value = 'loess' ).grid(row = 3, column=2)
        # self.gxsmoother3 = tk.Radiobutton(self.mframe2,text = 'polynomial', variable=self.gxsmoother, value = 'polynomial').grid(row = 3, column=3)

        self.gxsmoothercilab = tk.Label(
            self.mframe2, text="Show CI?").grid(row=4, column=0, sticky='w')
        self.gxsmootherci = tk.StringVar(value='No')
        self.gxsmthci1 = tk.Radiobutton(
            self.mframe2, text="Yes", variable=self.gxsmootherci, value='Yes').grid(row=4, column=1, sticky='w')
        self.gxsmthci1 = tk.Radiobutton(
            self.mframe2, text="No", variable=self.gxsmootherci, value='No').grid(row=4, column=2, sticky='w')

        # self.gxsmootherscttrlab = tk.Label(self.mframe2,text = "Show scatter plot?").grid(row = 5, column = 0, sticky = 'w')
        # self.gxsmootherscatter = tk.StringVar(value='Yes')
        # self.gxsmthci1 = tk.Radiobutton(self.mframe2, text = "Yes", variable=self.gxsmootherscatter, value = 'Yes').grid(row=5, column = 1, sticky = 'w')
        # self.gxsmthci2 = tk.Radiobutton(self.mframe2, text = "No", variable=self.gxsmootherscatter, value = 'No').grid(row=5, column = 2, sticky = 'w')

        self.gxpolysmootherorder = tk.StringVar(value='1')
        self.gxpolyorderlab = tk.Label(self.mframe2, text="Polynomial order:").grid(
            row=7, column=0, sticky='w')
        self.gxpolytext = tk.Entry(
            self.mframe2, textvariable=self.gxpolysmootherorder, width=4)
        self.gxpolytext.grid(row=7, column=1, sticky='w')
        self.gxloessfrac = tk.StringVar(value='0.3')
        self.gxloessfraclab = tk.Label(self.mframe2, text='Loess Fraction:').grid(
            row=7, column=2, sticky='w')
        self.gxloessfractext = tk.Entry(
            self.mframe2, textvariable=self.gxloessfrac, width=3)
        self.gxloessfractext.grid(row=7, column=3, stick='w')

        self.mframe.grid_forget()
        self.mframe2.grid_forget()

# smoothing line plot variables:  gxsmootherest, gxsmoother, gxsmootherci, gxsmootherscatter, gxpolysmootherorder


class gPlot(tk.Frame):

    def __init__(self, parent):
        super().__init__(master=parent)

        self.plotchoice = tk.StringVar(value='-')
        self.plotlabel = tk.Label(
            self, text="Plot Type:").grid(row=0, column=0)
        self.plot_options = tk.OptionMenu(
            self, self.plotchoice, *plot_types, command=self.doPlotParms)
        self.plot_options.grid(row=0, column=1)

        self.optionsframe = tk.Frame(
            self, borderwidth=2, relief="ridge", highlightthickness=1)
        self.optionsframe.grid(row=1, column=0, rowspan=6, columnspan=6)

        # self.optionslabel.pack(anchor = 'nw')

        self.meqn = tk.StringVar(None)
        self.teq1 = tk.Entry(self, textvariable=self.meqn, width=80)

    def doPlotParms(self, *args):  # set up the UI for extra information for each type of plot
        # first, clear the options frame
        for item in self.optionsframe.winfo_children():
            item.destroy()
        # plt.close('all')
        plot_type = self.plotchoice.get()
        # setup the facet/marker variable option lists
        self.master.plot_type = plot_type
        self.master.master.plot_type = plot_type
        colvar = self.master.master.selected_color_variable.get()
        if colvar != '-':
            flist = [
                item for item in self.master.master.facetlist0 if item != colvar]
            mlist = [
                item for item in self.master.master.marklist0 if item != colvar]
        else:
            flist = self.master.master.facetlist0
            mlist = self.master.master.marklist0

        # initialize the list of variables
        if len(self.master.master.v1list) == 0:
            self.plotchoice.set(value='-')
            return
        for idx, item in enumerate(self.master.master.v1list):
            r, c = getRowCol(idx, rowlength=ROWLENGTH)
            item.grid(row=r, column=c, sticky='w')
            # item.pack(side = tk.LEFT, anchor = 'w')
            item.mframe.grid(row=4, column=0, rowspan=3,
                             columnspan=2, sticky='w')
            item.mframe2.grid(row=7, column=0, rowspan=3,
                              columnspan=2, sticky='w')

        self.master.master.v1list[0].mframe.grid_forget()
        self.master.master.v1list[0].mframe2.grid_forget()

        if plot_type == 'Histogram':
            if len(self.master.master.v1list) > 1:
                for item in self.master.master.v1list[1:]:
                    item.grid_forget()
            self.master.master.mopts['values'] = ['-'] + mlist
            self.master.master.selected_marker_variable.set('-')
            self.master.master.f0_2d.grid_forget()  # don't show the marker choice
            self.master.master.f0_2dg.grid(
                row=2, column=4, columnspan=4, sticky='w')  # show facet choices
            self.getHistogramParms()
        elif plot_type == 'Boxplot':
            if len(self.master.master.v1list) < 1:
                return
            if len(self.master.master.v1list) > 1:
                for item in self.master.master.v1list[1:]:
                    item.grid_forget()

            self.master.master.mopts['values'] = ['-'] + mlist
            self.master.master.selected_marker_variable.set('-')
            self.master.master.f0_2d.grid_forget()
            self.master.master.f0_2dg.grid(
                row=2, column=4, columnspan=4, sticky='w')
            self.getBoxplotParms()
        elif plot_type == 'ECDF':
            if len(self.master.master.v1list) < 1:
                return
            if len(self.master.master.v1list) > 1:
                for item in self.master.master.v1list[1:]:
                    item.grid_forget()
            self.master.master.mopts['values'] = ['-'] + mlist
            self.master.master.selected_marker_variable.set('-')
            self.master.master.f0_2d.grid_forget()
            self.master.master.f0_2dg.grid(
                row=2, column=4, columnspan=4, sticky='w')
            self.getECDFParms()
        elif plot_type == '2D Line/Scatter Plot':
            if len(self.master.master.v1list) <= 1:
                return
            for idx, item in enumerate(self.master.master.v1list):
                item.gxlnstyle['values'] = ['-'] + baselinestyles
                item.clickedGXlnstyle.set('-')
                item.gxlnest['values'] = smootherwl
                r, c = getRowCol(idx, rowlength=ROWLENGTH)
                item.grid(row=r, column=c, sticky='w')
                # item.pack(side = tk.LEFT, anchor = 'w')
                if idx >= 1:
                    item.mframe.grid(row=4, column=0, rowspan=3,
                                     columnspan=2, sticky='w')
                    item.mframe2.grid(row=7, column=0, rowspan=3,
                                      columnspan=2, sticky='w')
            # self.master.master.f0.pack()
            # reset the row and column facet indicators if doing a single 2d plot
            self.master.master.f0_2d.grid(
                row=2, column=4, columnspan=4, sticky='w')
            self.master.master.fropts['values'] = ['-'] + flist
            self.master.master.fcopts['values'] = ['-'] + flist
            self.master.master.selected_row_variable.set('-')
            self.master.master.selected_col_variable.set('-')
            self.master.master.f0_2dg.grid_forget()
            self.get2DScatterParms()
            return
        elif plot_type == '2D Scatter Grid':
            if len(self.master.master.v1list) > 1:
                for idx, item in enumerate(self.master.master.v1list[1:]):
                    item.gxlnstyle['values'] = ['-'] + baselinestyles
                    item.clickedGXlnstyle.set('-')
                    item.mframe.grid(row=4, column=0, rowspan=3,
                                     columnspan=2, sticky='w')
                    item.mframe2.grid(row=7, column=0, rowspan=3,
                                      columnspan=2, sticky='w')
                    if idx > 0:
                        item._forget()
                    else:
                        item.mframe.grid_forget()
                        item.mframe2.grid_forget()
            else:
                return
            # self.master.master.f0.pack()
            self.master.master.f0_2dg.grid(
                row=2, column=4, columnspan=4, sticky='w')
            # reset the marker variable when facet plotting
            self.master.master.mopts['values'] = ['-'] + mlist
            self.master.master.selected_marker_variable.set('-')
            self.master.master.f0_2d.grid_forget()
            #self.master.master.f0_2d.grid(row=2, column=4, columnspan=4, sticky='w')
            self.get2DScatterGridParms()
            return
        elif plot_type == '3D Scatter Plot':
            if not HAVELOESS2D:
                emsg = "Warning: loess2d package not installed. \n Loess smoothing for 3D plots will not be available."
                emsg = emsg + "\n Install from: https://pypi.org/project/loess/ \nusing: 'pip install loess' in your local python environment."
                gdata.log_It(emsg)
            if len(self.master.master.v1list) > 2: 
                for idx, item in enumerate(self.master.master.v1list):
                    item.gxlnstyle['values'] = ['-'] + ['surface', 'wireframe', 'triangulated']
                    if not HAVELOESS2D: item.gxlnest['values'] = smoothernl
                    item.clickedGXlnstyle.set('-')
                    if idx < 2:
                        item.mframe.grid_forget()
                        item.mframe2.grid_forget()
                    else:
                        r, c = getRowCol(idx, rowlength=ROWLENGTH)
                        item.grid(row=r, column=c, sticky='w')
                        # item.pack(side = tk.LEFT, anchor = 'w')
                        item.mframe.grid(
                            row=4, column=0, rowspan=3, columnspan=2, sticky='w')
                        item.mframe2.grid(
                            row=7, column=0, rowspan=3, columnspan=2, sticky='w')
            else:
                return
            # self.master.master.f0.pack_forget()
            # reset the row and column facet indicators if doing a single 3d plot

            self.master.master.fropts['values'] = ['-'] + flist
            self.master.master.fcopts['values'] = ['-'] + flist
            self.master.master.selected_row_variable.set('-')
            self.master.master.selected_col_variable.set('-')
            # reset  marker variable when doing 3d plot
            self.master.master.mopts['values'] = ['-'] + mlist
            self.master.master.selected_marker_variable.set('-')
            self.master.master.f0_2dg.grid_forget()
            self.master.master.f0_2d.grid_forget()
            self.get3DScatterParms()
            return
        elif plot_type == '3D Surface Plot':  # (not implemented)
            # if len(self.master.master.v1list) > 1:
            #     self.master.master.v1list[1].mframe.grid_forget()
            # self.get3DSurfParms()
            return
        else:
            return
        # self.label = tk.Label(self.optionsframe, text=f"Plot type = {plot_type}").grid(row = 0, column = 0)
        # self.gobutton = tk.Button(self.optionsframe, text="Plot It!", command = self.plotHisto).grid(row=0,column = 6)

        return

###########################################################################
# functions to get extra parameters for the chosen plots
###########################################################################

    def get2DScatterParms(self):

        # self.label3 = tk.Label(self.optionsframe, text="Plot type: 2D Line or Scatter Plot").grid(row = 1, column = 0)
        self.gobutton = tk.Button(
            self.optionsframe, text="Plot It!", command=self.plot2DScatter).grid(row=1, column=6)

        self.titlelabel = tk.StringVar(self)
        self.label = tk.Label(self, text='Plot Title:').grid(
            row=0, column=7, sticky='w')
        self.gxlabel = tk.Entry(self, textvariable=self.titlelabel, width=20)
        self.gxlabel.grid(row=0, column=8, sticky='w')

    def get2DScatterGridParms(self):

        self.regline = tk.StringVar(self, value='No')
        self.reglabel = tk.Label(
            self.optionsframe, text="Show regression line?").grid(row=1, column=0)
        self.regbutton = tk.Radiobutton(
            self.optionsframe, text="Yes", variable=self.regline, value="Yes").grid(row=1, column=1)
        self.regbutton = tk.Radiobutton(
            self.optionsframe, text="No", variable=self.regline, value="No").grid(row=1, column=2)

        # self.label = tk.Label(self.optionsframe, text="Plot type: 2D Line Plot Grid").grid(row = 0, column = 0)
        self.gobutton = tk.Button(self.optionsframe, text="Plot It!",
                                  command=self.plot2DScatterGrid).grid(row=0, column=6)
        self.titlelabel = tk.StringVar(self)
        self.label = tk.Label(self, text='Plot Title:').grid(
            row=0, column=7, sticky='w')
        self.gxlabel = tk.Entry(self, textvariable=self.titlelabel, width=20)
        self.gxlabel.grid(row=0, column=8, sticky='w')

    def get3DScatterParms(self):
        # self.label = tk.Label(self.optionsframe, text="Plot type: 3D Scatter Plot").grid(row = 0, column = 0)
        self.gobutton = tk.Button(self.optionsframe, text="Plot It!",
                                  command=self.plot3DScatter).grid(row=0, column=6, sticky='w')
        self.titlelabel = tk.StringVar(self)
        self.label = tk.Label(self, text='Plot Title:').grid(
            row=0, column=7, sticky='w')
        self.gxlabel = tk.Entry(self, textvariable=self.titlelabel, width=20)
        self.gxlabel.grid(row=0, column=8, sticky='w')
        # self.gxloessfrac = tk.StringVar(value = '0.3')
        # self.gxloessfraclab = tk.Label(self.optionsframe, text = 'Loess Fraction:').grid(row= 1, column = 3, sticky = 'w')
        # self.gxloessfractext = tk.Entry (self.optionsframe, textvariable= self.gxloessfrac, width = 3)
        # self.gxloessfractext.grid(row = 1, column = 4, stick = 'w')

    def get3DSurfParms(self):
        # self.label = tk.Label(self.optionsframe, text="Plot type: 3D Surface Plot").grid(row = 0, column = 0)
        self.gobutton = tk.Button(
            self.optionsframe, text="Plot It!", command=self.plot3DSurf).grid(row=0, column=6)
        self.titlelabel = tk.StringVar(self)
        self.label = tk.Label(self, text='Plot Title:').grid(
            row=0, column=7, sticky='w')
        self.gxlabel = tk.Entry(self, textvariable=self.titlelabel, width=20)
        self.gxlabel.grid(row=0, column=8, sticky='w')

    def getBoxplotParms(self):
        self.selected_boxplot_grouping_variable = tk.StringVar(
            self.optionsframe, value='-')
        self.labelgroup = tk.Label(
            self.optionsframe, text="Box Plot Grouping Variable:").grid(row=0, column=0)
        self.coptsgroup = ttk.Combobox(self.optionsframe, values=[
                                       '-'] + self.master.master.colorlist0, textvariable=self.selected_boxplot_grouping_variable)
        self.coptsgroup.grid(row=0, column=1)

        self.gobutton = tk.Button(
            self.optionsframe, text="Plot It!", command=self.plotBoxplot).grid(row=0, column=6)
        self.titlelabel = tk.StringVar(self)
        self.label = tk.Label(self, text='Plot Title:').grid(
            row=0, column=7, sticky='w')
        self.gxlabel = tk.Entry(self, textvariable=self.titlelabel, width=20)

        self.dodither = tk.StringVar(self.optionsframe, value='No')
        self.ditherlab = tk.Label(self.optionsframe, text="Show Dithered Data Points?").grid(
            row=1, column=0, sticky='w')
        self.ditherbutton = tk.Radiobutton(
            self.optionsframe, text='Yes', variable=self.dodither, value='Yes')
        self.ditherbutton.grid(row=1, column=2, sticky='w')
        self.ditherbutton = tk.Radiobutton(
            self.optionsframe, text='No', variable=self.dodither, value='No')
        self.ditherbutton.grid(row=1, column=3, sticky='w')

        self.ditherseed = tk.StringVar(self.optionsframe, value='12345')
        self.ditherseedlab = tk.Label(self.optionsframe, text="Dither Seed:").grid(
            row=2, column=0, sticky='w')
        self.ditherseedentry = tk.Entry(
            self.optionsframe, textvariable=self.ditherseed, width=10)
        self.ditherseedentry.grid(row=2, column=2, sticky='w')

        self.ditherdotsize = tk.StringVar(self.optionsframe, value='2')
        self.ditherdotlab = tk.Label(self.optionsframe, text="Dither Dot Size:").grid(
            row=2, column=3, sticky='w')
        self.ditherdotentry = tk.Entry(
            self.optionsframe, textvariable=self.ditherdotsize, width=10)
        self.ditherdotentry.grid(row=2, column=5, sticky='w')

        self.gxlabel.grid(row=0, column=8, sticky='w')

    def getECDFParms(self):
        # self.label = tk.Label(self.optionsframe, text="Plot type: ECDF").grid(row = 0, column = 0)
        self.gobutton = tk.Button(
            self.optionsframe, text="Plot It!", command=self.plotECDF).grid(row=0, column=6)
        self.titlelabel = tk.StringVar(self)
        self.label = tk.Label(self, text='Plot Title:').grid(
            row=0, column=7, sticky='w')
        self.gxlabel = tk.Entry(self, textvariable=self.titlelabel, width=20)
        self.gxlabel.grid(row=0, column=8, sticky='w')

    def getHistogramParms(self):
        self.nobins = tk.StringVar(self, value='auto')
        self.binlabel = tk.Label(self.optionsframe, text="# of bins:")
        self.nobins_entry = tk.Entry(
            self.optionsframe, textvariable=self.nobins, width=6)
        self.binlabel.grid(row=0, column=1)
        self.nobins_entry.grid(row=0, column=2)

        self.kdelabel = tk.Label(self.optionsframe, text="Add KDE overlay?").grid(
            row=1, column=0, sticky='w')
        self.dokde = tk.StringVar(self.optionsframe, value='No')
        self.kderadio = tk.Radiobutton(
            self.optionsframe, text='Yes', variable=self.dokde, value='Yes')
        self.kderadio.grid(row=1, column=2, sticky='w')
        self.kderadio = tk.Radiobutton(
            self.optionsframe, text='No', variable=self.dokde, value='No')
        self.kderadio.grid(row=1, column=3, sticky='w')

        # self.label = tk.Label(self.optionsframe, text="Plot type = Histogram").grid(row = 0, column = 0)
        self.gobutton = tk.Button(
            self.optionsframe, text="Plot It!", command=self.plotHistogram).grid(row=0, column=6)
        self.titlelabel = tk.StringVar(self)
        self.label = tk.Label(self, text='Plot Title:').grid(
            row=0, column=7, sticky='w')
        self.gxlabel = tk.Entry(self, textvariable=self.titlelabel, width=20)
        self.gxlabel.grid(row=0, column=8, sticky='w')

###########################################################################
# functions to do the plotting
###########################################################################

    def plot2DScatter(self):
        if (len(self.master.master.v1list) <= 1):
            return
        vx = self.master.master.v1list[0]
        xv = vx.varname
        cv = self.master.master.selected_color_variable.get()
        mv = self.master.master.selected_marker_variable.get()
        # rf = self.master.master.selected_col_variable.get()
        # cf = self.master.master.selected_row_variable.get()

        # get rid of the Nan's in the plotting data
        vars = [cv, mv]
        nuvars = [item.varname for item in self.master.master.v1list]
        vars = vars + nuvars
        active_vars = list(set([item for item in vars if (item != '-')]))
        # print(f"Active columns: {', '.join(active_vars)}")
        df = self.master.master.data.copy(deep = True)
        gdata.code_It(" ")
        gdata.code_It("################################")
        gdata.code_It("## ")

        nobs0 = len(df)
        df.dropna(subset=active_vars, inplace = True)
        nobs = len(df)
        self.master.master.current_data = df #it's ok we don't need to copy the data 
        
        #code to read data in (in the code file) and check # rows in original and plotted data
        lstr0 = f"df = pd.read_csv('{gdata.fpath}',engine='python')"
        lstr1 = "nobs0 = len(df)"
        lstr2 = f"df.dropna(subset={active_vars}, inplace = True)"
        lstr3 = "nobs = len(df)"
        #lstr4 = "print('CHECK: ' + str(nobs) + ' rows out of ' + str(nobs0))"
        gdata.code_It(" ")
        gdata.code_It(lstr0)
        gdata.code_It(lstr1)
        gdata.code_It(lstr2)
        gdata.code_It(lstr3)
        #gdata.code_It(lstr4)

        
        gdata.code_It(f"df.dropna(subset = {active_vars}, inplace = True)")

        # set the title
        ptitle = f"({nobs} rows out of {nobs0})"
        ctitle = f"({nobs} rows out of {nobs0})"
        user_title = self.titlelabel.get()
        if user_title != '':
            ptitle = user_title + "\n" + ptitle
            ctitle = user_title + " \\n " + ctitle
        lg_msg = f" 2D Scatter Plot x= {xv}, color= {cv}, marker= {mv}, Title: {ptitle}"
        gdata.log_It(lg_msg)

        # Now start plotting
        sfig = plt.figure(figsize=(8, 8))
        ax = sfig.subplots()
        gdata.code_It("sfig = plt.figure(figsize = (8,8)) \nax = sfig.subplots()")

        xlab = vx.xlabel.get()

        scatterplotdict = {}
        lineplotdict = {}
        regplotdict = {}

        # iterate through the objects for the "y" variables
        # parameter variables: "data": df, "x":xv, "y":yv, "hue": cv, "marker": ymarker, "color": ycolor, "size":ysize, "linestyle": vystemp,
        #

        # ylowermin = 0
        # yuppermax = 0

        # intialize the axis limits
        xlower = float(vx.gxlb.get())
        xupper = float(vx.gxub.get())

        # yupper = float(self.master.master.v1list[1].gxub.get())
        # ylower = float(self.master.master.v1list[1].gxlb.get())
        yupper = 0.0
        ylower = 0.0
        # print(f"yupper = {yupper} ylower={ylower}")

        # initialize y axis label
        ylab = ''
        #print("*******************\n    Starting Plotting Loop! \n ******************************\n)")
        for idx, item in enumerate(self.master.master.v1list[1:]):
            yv = item.varname                    # y variable column name
            ytemp = item.clickedGXmkr.get()      # the marker type for y in scatterplot
            # the color for the marker for y overrides cv (above)
            ycolor = item.clickedGXcol.get()
            # the size for the marker for y (currently controls all feature sizes)
            ysize = item.gxlsz.get()
            # the line style for y if ='-' then no line
            vystyl = item.clickedGXlnstyle.get()
            lcolor = item.clickedGXlncolor.get()  # the line color for y
            # the estimator for y when multiple point at the same x
            ltemp = item.gxlineest.get()
            # boolean True = show scatter Fales = don't
            showscatter = item.gxsmootherscatter.get()
            # order for a polynomial smoothin (0 none, 1 OLS, 2 etc..)
            polyorder = int(item.gxpolysmootherorder.get())
            # ysmoother = item.gxsmoother.get()#   # smoother choice
            yci = item.gxsmootherci.get()          # smoother ci Yes or No
            loessfrac = float(item.gxloessfrac.get())

            # if ysmoother == None:
            #     item.gxsmoother.set("0")

            if ltemp == '-':  # line estimator
                ltemp = None

            if showscatter == 'Yes':
                showscatter = True
            else:
                showscatter = False

            # set the marker choice, either the plot-wide marker choices in cv or the markerfor the
            # current dependent varible in ytemp.  Note: ytemp != '-' means the user has chosen a marker,
            # marker choice overrides mv.

            # set the marker variable appropriately if none has been chosen
            if (mv == '-'):
                mv = None

            # get the marker choice and override mv
            ymarker = 'o'
            if ytemp != '-':
                mv == None
                ymarker = markerdict[ytemp]

            # set the color choice for the scatter plot dots, either the plot-wide color choices
            # in cv or the color for the current dependent varible in ycolor or
            # the line color in lncolor.  Note ycolor overrides cv
            # If neither have been set, paint it black.

            palettev = None
            line_kw = {}
            huelist = []
            if (cv == '-') & (ycolor != '-'):
                huelist = None
                palettev = None    
                #line_kw={'color': ycolor}
            elif(cv == '-') & (ycolor == '-'):
                huelist = None
                palettev = None
                ycolor = 'black'
                line_kw = {'color': 'black'}
            elif (cv != '-') & (ycolor != '-'):
                huelist = None
                palettev = None
                line_kw = {"color": ycolor}
            else:
                huelist = cv
                palettev = 'bright'
                ycolor = None

            # get the size choice and color choice
            ysize = item.gxlsz.get()
            line_kw["lw"] = ysize/5

            # set the lineplot color

            if lcolor == '-':
                lcolor = "black"

            # set the estimator to use for multiple values at a single  x point
            # when lineplotting
            showline = False
            showsmooth = False
            vci = None
            vloess = False

            if vystyl != '-':
                if ltemp == None:
                    showline = True
                elif ltemp == 'median':
                    showline = True
                    if yci == 'Yes':
                        vci = "ci"
                elif ltemp == 'mean':
                    showline = True
                    if yci == 'Yes':
                        vci = "ci"
                elif ltemp == 'polynomial':
                    showline = False
                    showsmooth = True
                    vloess = False
                    if yci == 'Yes':
                        vci = 95
                elif ltemp == 'loess':
                    vloess = True
                    showline = False
                    showsmooth = True
                    vci = None
                    polyorder = 0

            # adjust line color and type for regplot
            line_kw['ls'] = vystyl
            line_kw['color'] = lcolor
            line_kw['linewidth'] = ysize/5
            # line_kw['markers'] = False

            # finally get labels and titles
            if (ylab != ''):
                ylab = ylab + ", " + item.xlabel.get()
            else:
                ylab = item.xlabel.get()

            # yupper = float(item.gxub.get())
            # ylower = float(item.gxlb.get())

            # parameter keyword dictionary

            # show_ols = item.self.do_ols.get()


# Set the parameters for scatterplot, lineplot and regplot
            scatterplotdict = {"x": xv, "y": yv, "hue": huelist, "palette": palettev, "style": mv,
                               "color": ycolor, "s": ysize, "marker": ymarker}

            lineplotdict = {"x": xv, "y": yv, "color": lcolor, "linewidth": ysize/5, "label": yv,
                            "markers": False, "estimator": ltemp, "errorbar": None, "linestyle": vystyl}

            regplotdict = {"x": xv, "y": yv, "label": yv, "scatter": False, "label": yv,
                           "lowess": vloess, "order": polyorder, "ci":  vci, "line_kws": line_kw}

            # print(f"Showline: {showline}, showsmooth {showsmooth}, showscatter = {showscatter}")

            # if (!showscatter) and (vystyl == '-'):  #show scatter = False and vystyle = '-' skips this plot entirely
            #     showscatter =False
            #     showline = False
            #     showsmooth = False

            if (showscatter):
                # print("scatterplot params: ***>\n =======\n",", ".join([str(k)+" = "+str(scatterplotdict[k]) for k in list(scatterplotdict.keys())]))
                #lstr = "sb.scatterplot(df, ax = ax, " + ", ".join([str(k)+" = "+f"'{scatterplotdict[k]}'" for k in list(scatterplotdict.keys())])+")"
                lstr = "sb.scatterplot(df, ax = ax, **" +f"{scatterplotdict})"
                gdata.code_It(lstr)
                sb.scatterplot(df, ax = ax, **scatterplotdict)
                #gd.sb_scatterplotJM(df, **scatterplotdict)

            if (showline):
                # print("lineplot params showline only ***>:\n =======\n",lineplotdict)
                lstr = "sb.lineplot(df, ax = ax, **{lineplotdict})"
                gdata.code_It(lstr)
                sb.lineplot(df,ax = ax,  **lineplotdict)

            if (showsmooth and polyorder == 0):
                smoothed = sm.nonparametric.lowess(exog=np.array(df[xv]), endog=np.array(df[yv]), frac=loessfrac)
                gdata.log_It(loess_msg)
                dfsmooth = pd.DataFrame({"xs": smoothed[:, 0], "ys": smoothed[:, 1]})
                lineplotdict["x"] = 'xs'
                lineplotdict["y"] = 'ys'
                lineplotdict["estimator"] = None
                
                #setup lowess smoother for code generation
                lstlws0 = f"smoothed = sm.nonparametric.lowess(exog=np.array(df['{xv}']), endog=np.array(df['{yv}']), frac={loessfrac})"
                gdata.code_It(lstlws0)
                lstlws1 = 'dfsmooth = pd.DataFrame({"xs": smoothed[:, 0], "ys": smoothed[:, 1]})'
                gdata.code_It(lstlws1)
                #now code it
                lstr = f"sb.lineplot(data = dfsmooth, ax = ax, **{lineplotdict})"
                gdata.code_It(lstr)
                
                # Compute a lowess smoothing of the data
                sb.lineplot(data=dfsmooth,ax = ax, **lineplotdict)
            elif (showsmooth and polyorder >= 1):
                lstr = f"sb.regplot(df, ax = ax, **{regplotdict})"
                gdata.code_It(lstr)
                sb.regplot(df,ax = ax,  **regplotdict)

            bdl = float(item.gxlb.get())
            bdu = float(item.gxub.get())
            # if we are graphing anything about this variable, include its data range in the ylim calculations
            # ylower and yupper are initialized to yupper=ylower=0 at before this loop
            if (showscatter | showsmooth | showline):
                if (yupper == ylower):
                    ylower = bdl
                    yupper = bdu
                else:
                    if ylower > bdl:
                        ylower = bdl
                    if yupper < bdu:
                        yupper = bdu

        ax.set_xlabel(xlab)
        ax.set_ylabel(ylab)
        ax.legend(bbox_to_anchor=(0.98, 1), loc='upper left', borderaxespad=2)
        # ax.legend()
        ax.set_xlim(xlower, xupper)
        ax.set_ylim(ylower, yupper)
        sfig.suptitle(t=ptitle, y=0.95)
        sfig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        sfig.show()
        
        #generate code from axis and figure settings
        gdata.code_It(f"ax.set_xlabel('{xlab}')")
        gdata.code_It(f"ax.set_ylabel('{ylab}')")
        gdata.code_It("ax.legend(bbox_to_anchor=(0.98, 1), loc='upper left', borderaxespad=2)")
        gdata.code_It(f"ax.set_xlim({xlower}, {xupper})")
        gdata.code_It(f"ax.set_ylim({ylower}, {yupper})")
        gdata.code_It(f"sfig.suptitle(t='{ctitle}', y=0.95)")
        gdata.code_It("sfig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)")
        gdata.code_It("sfig.show()")
        gdata.code_It("#plt.show()")
        
        return
###################################################################################

    def plot2DScatterGrid(self):
        if (len(self.master.master.v1list) <= 1):
            return
        vx = self.master.master.v1list[0]
        vy = self.master.master.v1list[1]
        xv = vx.varname
        yv = vy.varname
        cv = self.master.master.selected_color_variable.get()
        mv = self.master.master.selected_marker_variable.get()
        rf = self.master.master.selected_row_variable.get()
        cf = self.master.master.selected_col_variable.get()
        # if cf == '-' and rf == '-': return
        # find the object for the "y" variable
        ytemp = vy.clickedGXmkr.get()
        doreg = self.regline.get()

        # get the marker choice
        if ytemp == '-':
            ymarker = 'o'
        else:
            ymarker = markerdict[ytemp]
        # get the color choice
        ycolor = vy.clickedGXcol.get()
        if ycolor == '-':
            ycolor = 'black'
        ysize = vy.gxlsz.get()

        # get the plot type
        plot_type = self.plotchoice.get()

        # get rid of NA's report resulting sample size in nobs
        vars = [item for item in [xv, yv, cv, mv, rf, cf] if item != '-']
        if len(self.master.master.v1list) >= 3:
            nuvars = [item.varname for item in self.master.master.v1list[2:]]
            vars = vars + nuvars
        active_vars = list(set([item for item in vars if (item != '-')]))
        df = self.master.master.data.copy(deep = True)
        nobs0 = len(df)        
        df.dropna(subset=active_vars, inplace = True)
        nobs = len(df)
        self.master.master.current_data = df #it's ok we don't need to copy the data 
        gdata.code_It("################################")
        gdata.code_It("## Code for 2D Scatter Plot Grid")

        #code to read data in (in log file) and check # rows in original and plotted data
        lstr0 = f"df = pd.read_csv('{gdata.fpath}',engine='python')"
        lstr1 = "nobs0 = len(df)"
        lstr2 = f"df.dropna(subset={active_vars}, inplace = True)"
        lstr3 = "nobs = len(df)"
        #lstr4 = "print('CHECK: ' + str(nobs) + ' rows out of ' + str(nobs0))"
        gdata.code_It(" ")
        gdata.code_It(lstr0)
        gdata.code_It(lstr1)
        gdata.code_It(lstr2)
        gdata.code_It(lstr3)
        #gdata.code_It(lstr4)


                

        # set the color palette for automatic coloring
        palettenu = 'bright'

        # finally get labels and titles
        xlab = vx.xlabel.get()
        ylab = vy.xlabel.get()

        # get axis limits
        xlower = float(vx.gxlb.get())
        xupper = float(vx.gxub.get())
        ylower = float(vy.gxlb.get())
        yupper = float(vy.gxub.get())

        ptitle = f"({nobs} rows out of {nobs0})"
        ctitle = f"({nobs} rows out of {nobs0})"
        user_title = self.titlelabel.get()
        if user_title != '':
            ptitle = user_title + "\n" + ptitle
            ctitle = user_title + " \\n " + ctitle

        lg_msg = f" 2D Scatter Plot Grid: y= {yv}, x= {xv}, color= {
            cv}, marker= {mv}, rows= {rf}, cols= {cf}, Title: {ptitle}"
        gdata.log_It(lg_msg)


# hue variable to choose marker types.  So I just ignore it. Colors are enough of a problem to manage.
        plotdict = {}
        relplotdict = {}
        
        plotdict['x'] = xv
        plotdict['y'] = yv
        if cv!= '-': 
            plotdict['hue'] = cv
            plotdict['palette'] = palettenu
            if doreg == 'Yes':
                plotdict["scatter_kws"] = {"s": ysize}
            else:
                plotdict["s"] = ysize
        else:
            if doreg == 'Yes':
                plotdict["scatter_kws"] = {"s": ysize, "color":ycolor}
            else:
                plotdict['color'] = ycolor
                plotdict['s'] = ysize
        if (rf != '-'):
            plotdict['row'] = rf
        if (cf != '-'): 
            plotdict['col'] = cf
            
        if doreg == 'Yes':
            #lstr = "g = sb.lmplot(" + ", ".join([str(k)+" = "+str(plotdict[k]) for k in list(plotdict.keys())])+")"
            lstr = f"g = sb.lmplot(df, **{plotdict})"
            gdata.code_It(lstr)
            g = sb.lmplot(df, **plotdict)
        else:
            #lstr = "g = sb.relplot(" + ", ".join([str(k)+" = "+str(plotdict[k]) for k in list(plotdict.keys())])+")"
            lstr = f"g= sb.relplot(df, **{plotdict})"
            gdata.code_It(lstr)
            g = sb.relplot(df, **plotdict)

        g.set(xlim=(xlower, xupper), ylim=(ylower, yupper))
        g.set_axis_labels(xlab, ylab)
        g.figure.suptitle(ptitle, fontsize=12)
        g.figure.subplots_adjust(top=0.9)
        g.figure.show()
        
        #generate code from axis and figure settings
        gdata.code_It(f"g.set(xlim=({xlower}, {xupper}))")
        gdata.code_It(f"g.set(ylim=({ylower}, {yupper}))")
        gdata.code_It(f"g.set_axis_labels('{xlab}', '{ylab}')")
        gdata.code_It(f"g.figure.suptitle('{ctitle}', fontsize=12)")
        gdata.code_It("g.figure.subplots_adjust(top=0.9)")
        gdata.code_It("g.figure.show()")
        gdata.code_It("#plt.show()")

        return




    def plot3DScatter(self):
        if (len(self.master.master.v1list) <= 2):
            return
        # independent variables
        vx = self.master.master.v1list[0]
        vy = self.master.master.v1list[1]
        xv = vx.varname
        yv = vy.varname

        # global plot choices
        # dot color variable
        cv = str(self.master.master.selected_color_variable.get())
        mv = self.master.master.selected_marker_variable.get()  # dot marker variable

        # Clean up the data:
        # get rid of NA's report resulting sample size in nobs
        vars = [cv, mv]
        nuvars = [item.varname for item in self.master.master.v1list]
        vars = vars + nuvars
        active_vars = [item for item in vars if (item != '-')]
        # print(f" Active Variables: {', '.join(active_vars)}")
        df = self.master.master.data.copy(deep=True)
        nobs0 = len(df)
        df.dropna(subset=active_vars, inplace = True)
        gdata.code_It(f"df.dropna(subset = {active_vars}, inplace = True)")
        nobs = len(df)
        self.master.master.current_data = df #it's ok we don't need to copy the data 


        # x and y labels
        xlab = vx.xlabel.get()
        ylab = vy.xlabel.get()

        # x and y bounds and plot title and initial z bounds
        xlower = float(vx.gxlb.get())
        xupper = float(vx.gxub.get())
        ylower = float(vy.gxlb.get())
        yupper = float(vy.gxub.get())
        zlower = float(self.master.master.v1list[2].gxlb.get())
        zupper = float(self.master.master.v1list[2].gxub.get())

        ptitle = f"({nobs} rows out of {nobs0})"
        ctitle = f"({nobs} rows out of {nobs0})"
        user_title = self.titlelabel.get()
        if user_title != '':
            ptitle = user_title + "\n" + ptitle
            ctitle = user_title + " \\n " + ctitle

        # set up the 3D figure
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111, projection='3d')
        str3d = """
##### 3D Scatter Plotting Code #####
fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111, projection='3d')
"""
        gdata.code_It(str3d)
        
        # if coloring the dots, get the colors set up the color list and legend
        colorlist = None
        handles = []
        colorD = {}  # dictionary of cv values to colors
        lpatches = []  # legend patches
        cvpatches = []  # patches created from cv
        
        str3d = """
colorlist = None
handles = []
colorD = {}  # dictionary of cv values to colors
lpatches = []  # legend patches
cvpatches = []  # patches created from cv
color_variable = False"""

        str3d = f"cv = '{cv}'\n" + str3d
        gdata.code_It(str3d)

        if cv != '-':
            colorD, colorlist, cvpatches = grp.getcolor(cv, list(df[cv]))
            gdata.code_It(f"colorD, colorlist, cvpatches = grp.getcolor(cv, list(df[cv]))")

        # initialize the z axis label
        zlab = ''
        showscatter = False
        showsurface = False
        showwireframe = False
        showtriangulated = False
        colorlegend = False

        gridsize = 20  # TODO: make this an adjustable parameter
        
        # now plot the additional vertical axis (z variables) series
        surface_legend_entries = []
        gdata.code_It("surface_legend_entries = []")
        for zitem in self.master.master.v1list[2:]:
            zv = zitem.varname
            ztemp = zitem.clickedGXmkr.get()

            # the color for the marker for y overrides cv (above)
            zcolor = zitem.clickedGXcol.get()
            # the size for the marker for y (currently controls all feature sizes)
            zsize = zitem.gxlsz.get()
            # the surface style for y if ='-' then no surface
            zstyl = zitem.clickedGXlnstyle.get()
            lcolor = zitem.clickedGXlncolor.get()  # the line color for y
            # the estimator for y when multiple point at the same x
            ltemp = zitem.gxlineest.get()
            # boolean True = show scatter False = don't
            showscatter = zitem.gxsmootherscatter.get()
            # order for a polynomial smoothing (0 none, 1 OLS, 2 etc..)
            polyorder = int(zitem.gxpolysmootherorder.get())
            loessfrac = float(zitem.gxloessfrac.get())
            # ysmoother = zitem.gxsmoother.get()#   # smoother choice
            yci = zitem.gxsmootherci.get()          # smoother ci Yes or No
            zcolorsurf = zitem.clickedGXlncolor.get()

            zlegend = None
            scatterplotparms = {}
            surfaceplotparms = {}
            wireframeplotparms = {}
            triagulatedplotparms = {}
            if cv != '-':  #initialize colorlistz  to true if cv exists
                colorlistz = colorlist
            else: # or False as the case may be.
                colorlistz = None
            #Are we producing a scatter plot for this variable?    
            if showscatter == 'Yes':
                # update axis label string
                if zlab == '':
                    zlab = zv
                else:
                    zlab = zlab + ", " + zv

                zlegend = zv
                # set the marker choice
                if ztemp == '-':
                    zmarker = 'o'
                else:
                    zmarker = markerdict[ztemp]
                    
                # set the  coloring vectors
                colorchoice = None
                if zcolor != '-':  # chosen color overrides the cv coloring variable
                    colorchoice = zcolor
                    colorlistz = None
                else:
                    if cv == '-':  # if there is no color variable and no chosen color, use 'blue' and set colorlist to None
                        colorchoice = 'blue'
                        colorlistz = None
                    else:
                        colorchoice = None
                        colorlistz = colorlist

                # if cv != '-' then colorlist exists and if colorchoice is None then we default to colorlist
                # we need to record this for the legend assembly below to add cvpatches to legend

                # add colorchoice to the patch list for the legend for this z if needed
                if (colorchoice is not None):
                    nupatch = mpatches.Patch(color=colorchoice, label=zlegend)
                    lpatches.extend([nupatch])
                    gdata.code_It(f"nupatch = mpatches.Patch(color='{colorchoice}', label='{zlegend}')")
                    gdata.code_It(f"lpatches.extend([nupatch])")

                # Do the scatter plot
                if colorlistz is not None:
                    scatterplotparms = {'color': None, 'marker': zmarker, 's': zsize, 'alpha': 0.8}
                    gdata.code_It(f"ax.scatter3D(df['{xv}'], df['{yv}'], df['{zv}'],c = colorlist, **{scatterplotparms})")                
                    gdata.log_It(f"ax.scatter3D(df['{xv}'], df['{yv}'], df['{zv}'], c=colorlist, **{scatterplotparms})")
                    colorlegend = True
                else:
                    scatterplotparms = {'color': colorchoice, 'marker': zmarker, 's': zsize, 'alpha': 0.8}
                    gdata.code_It(f"ax.scatter3D(df['{xv}'], df['{yv}'], df['{zv}'],c = None, **{scatterplotparms})")                
                    gdata.log_It(f"ax.scatter3D(df['{xv}'], df['{yv}'], df['{zv}'], c = None, **{scatterplotparms})")
                                  
                ax.scatter3D(df[xv], df[yv], df[zv], c = colorlistz, **scatterplotparms)
                
                

                #update the z bounds for graphing
                zlb = float(zitem.gxlb.get())
                zub = float(zitem.gxub.get())
        
                if zlower > zlb:
                    zlower = zlb
                if zupper < zub:
                    zupper = zub

            x = np.array([])
            y = np.array([])
            z = np.array([])
            grouped = pd.DataFrame()

            # if we are plotting a smoothed version of z, set it up
            if zstyl != '-':
                xin = np.array(df[xv])
                yin = np.array(df[yv])
                zin = np.array(df[zv])

                # create 2 1D input arrays
                xg = np.linspace(xin.min(), xin.max(), gridsize)
                yg = np.linspace(yin.min(), yin.max(), gridsize)
                # Use numpy.meshgrid to create the 2D grid arrays

                Xg, Yg = np.meshgrid(xg, yg)
                # use flatten to turn the 2d data arrays into two variables suitable for statsmodels
                Xgf = Xg.flatten()
                Ygf = Yg.flatten()
                Z_predicted = np.empty_like(Ygf)
                Z_predicted_reshaped = np.empty_like(Yg)
                
                cstr = f"""
###################
##    3D Surface Plotting Code for {zv} with surface style {zstyl} 
#       and line estimator/smoother {ltemp}
gridsize = {gridsize} # number of grid points in x and y for surface prediction
xin = np.array(df['{xv}'])
yin = np.array(df['{yv}'])
zin = np.array(df['{zv}'])
# create 2 1D input arrays
xg = np.linspace({xin.min()}, {xin.max()}, {gridsize})
yg = np.linspace({yin.min()}, {yin.max()}, {gridsize})
# Use numpy.meshgrid to create the 2D grid arrays
Xg, Yg = np.meshgrid(xg, yg)
# use flatten to turn the 2d data arrays into two variables suitable for statsmodels
Xgf = Xg.flatten()
Ygf = Yg.flatten()
Z_predicted = np.empty_like(Ygf)
Z_predicted_reshaped = np.empty_like(Yg)
"""
                gdata.code_It(cstr)

                #update the z bounds for graphing

                zlb = float(zitem.gxlb.get())
                zub = float(zitem.gxub.get())

                if zlower > zlb:
                    zlower = zlb
                if zupper < zub:
                    zupper = zub


                if zcolorsurf == '-':
                    zcolor = 'blue'
                else:
                    zcolor = zcolorsurf
                # ltemp is the type of smoothing to plot
                if ltemp == 'polynomial':
                    poly = PolynomialFeatures(degree=polyorder)
                    input_pts = np.stack([xin, yin]).T
                    input_features = poly.fit_transform(input_pts)

                    # Linear regression. note: intercept added to design matrix (input_features)
                    model = LinearRegression(fit_intercept=False)
                    model.fit(input_features, zin)
                    cstr = f""" 
poly = PolynomialFeatures(degree={polyorder})
input_pts = np.stack([xin, yin]).T
input_features = poly.fit_transform(input_pts)

# Linear regression. note: intercept added to design matrix (input_features)
model = LinearRegression(fit_intercept=False)
model.fit(input_features, zin)
"""
                    gdata.code_It(cstr)
                    # log the coefficients and R2
                    # print(";".join(list(dict(zip(poly.get_feature_names_out(), model.coef_.round(4))))))
                    outdict = dict(
                        zip(poly.get_feature_names_out(), model.coef_.round(4)))
                    pstlist = [str(item) + "=" + str(outdict[item])
                               for item in list(outdict.keys())]
                    gdata.log_It("\n".join(pstlist))

                    # log fit
                    gdata.log_It(
                        f"R-squared: {model.score(poly.transform(input_pts), zin):.3f}")

                    # populate the prediction mesh
                    # predictions
                    input_pts_grid = np.stack([Xgf, Ygf]).T
                    Z_predicted = model.predict(poly.transform(input_pts_grid))
                    # z dimension grid points
                    Z_predicted_reshaped = np.reshape(Z_predicted, Xg.shape)
                    # we are now good good to go for a polynomial smoothing plot (surface or wire frame)
                    # the variables are Xg, Yg, Z_predicted_reshaped
                    if zstyl == 'triangulated':
                        x = Xgf
                        y = Ygf
                        z = Z_predicted
                    else:
                        x = Xg
                        y = Yg
                        z = Z_predicted_reshaped

                    cstr = """
# populate the prediction mesh
# predictions
input_pts_grid = np.stack([Xgf, Ygf]).T
Z_predicted = model.predict(poly.transform(input_pts_grid))
# z dimension grid points
Z_predicted_reshaped = np.reshape(Z_predicted, Xg.shape)
# we are now good good to go for a polynomial smoothing plot (surface or wire frame)
# the variables are Xg, Yg, Z_predicted_reshaped
"""
                    gdata.code_It(cstr)
                    if zstyl == 'triangulated':
                        cstr = """
x = Xgf
y = Ygf
z = Z_predicted"""
                        gdata.code_It(cstr)
                    else:
                        cstr = """
x = Xg
y = Yg
z = Z_predicted_reshaped"""
                        gdata.code_It(cstr)
                elif (ltemp == 'loess'):  
                    Z_predicted, wout = loess_2d(
                        x=xin, y=yin, z=zin, xnew=Xgf, ynew=Ygf, degree=1, frac=loessfrac)
                    Z_predicted_reshaped = np.reshape(Z_predicted, Xg.shape)
                    cstr = f"""
Z_predicted, wout = loess_2d(x=xin, y=yin, z=zin, xnew=Xgf, ynew=Ygf, degree=1, frac={loessfrac})
Z_predicted_reshaped = np.reshape(Z_predicted, Xg.shape)"""                 
                    gdata.code_It(cstr)
                    if zstyl == 'triangulated':
                        x = Xgf
                        y = Ygf
                        z = Z_predicted
                        cstr = """
x = Xgf
y = Ygf
z = Z_predicted"""
                        gdata.code_It(cstr)
                    else:
                        x = Xg
                        y = Yg
                        z = Z_predicted_reshaped
                        cstr = """
x = Xg
y = Yg
z = Z_predicted_reshaped"""
                        gdata.code_It(cstr)
                elif ltemp == 'median' or ltemp == 'mean' or ltemp == 'None':
                    dfd = pd.DataFrame({'x': xin, 'y': yin, 'z': zin})
                    gdata.code_It("dfd = pd.DataFrame({'x': xin, 'y': yin, 'z': zin})")
                    if ltemp == 'median':
                        grouped = dfd.groupby(['x', 'y']).median().reset_index()
                        gdata.code_It("grouped = dfd.groupby(['x', 'y']).median().reset_index()")
                    elif ltemp == 'mean':
                        grouped = dfd.groupby(['x', 'y']).mean().reset_index()
                        gdata.code_It("grouped = dfd.groupby(['x', 'y']).mean().reset_index()")
                    else:
                        grouped = dfd
                        gdata.code_It("grouped = dfd")
                    xi = np.array(grouped['x'])
                    yi = np.array(grouped['y'])
                    zi = np.array(grouped['z'])
                    Xi, Yi = np.meshgrid(xi, yi)
                    Zi = griddata((xi, yi), zi, (Xi, Yi), method='cubic')  # linear, nearest
                    cst = """
xi = np.array(grouped['x'])
yi = np.array(grouped['y'])
zi = np.array(grouped['z'])
Xi, Yi = np.meshgrid(xi, yi)
Zi = griddata((xi, yi), zi, (Xi, Yi), method='cubic')  # linear, nearest"""
                    gdata.code_It(cst)
                    if zstyl == 'triangulated':
                        x = xi
                        y = yi
                        z = zi
                        cstr = """
x = xi
y = yi
z = zi"""
                        gdata.code_It(cstr)
                    else:
                        x = Xi
                        y = Yi
                        z = Zi
                        cstr = """
x = Xi
y = Yi
z = Zi"""
                        gdata.code_It(cstr)
            else:
                continue

            # smoother plotting commands here ###########################################################################
            zsurf = None
            if zstyl == 'triangulated':
                triangulatedplotparms = {'color': zcolor, 'label': zv, 'edgecolor': 'lightgrey', 'alpha': 0.5}
                gdata.code_It(f"triangulatedplotparms = {{'color': '{zcolor}', 'label': '{zv}', 'edgecolor': 'lightgrey', 'alpha': 0.5}}")
                try:
                    zsurf = ax.plot_trisurf(x, y, z, **triangulatedplotparms)
                    gdata.code_It(f"zsurf = ax.plot_trisurf(x, y, z, **triangulatedplotparms)")
                except Exception as er:
                    gdata.log_It(f" plot_trisurf() failed! Error:{er}")
                    tk.messagebox.showerror(
                        " ", f"Triangulated surface plot failed! Error:{er}")
                # ax.plot_trisurf(x, y, z, color = zcolor, label = zv, edgecolor = 'lightgrey')
            elif zstyl == 'wireframe':
                wireframeplotparms = {'color': 'lightgrey', 'label': zv, 'edgecolor': zcolor, 'alpha': 0.5}
                gdata.code_It(f"wireframeplotparms = {{'color': '{'lightgrey'}', 'label': '{zv}', 'edgecolor': '{zcolor}', 'alpha': 0.5}}")  
                zsurf = ax.plot_wireframe(x, y, z, **wireframeplotparms)
                gdata.code_It(f"zsurf = ax.plot_wireframe(x, y, z, **wireframeplotparms)")
                # ax.plot_wireframe(x, y, z, color = 'lightgrey', label = zv, edgecolor = zcolor, alpha = 0.5)
            elif zstyl == 'surface':
                surfaceplotparms = {'color': zcolor, 'label': zv, 'edgecolor': 'lightgrey', 'alpha': 0.5}
                gdata.code_It(f"surfaceplotparms = {{'color': '{zcolor}', 'label': '{zv}', 'edgecolor': 'lightgrey', 'alpha': 0.5}}")
                zsurf = ax.plot_surface(x, y, z, **surfaceplotparms)
                gdata.code_It(f"zsurf = ax.plot_surface(x, y, z, **surfaceplotparms)")
    
                # ax.plot_surface(x, y, z, color = zcolor, label = zv, edgecolor = 'lightgrey', alpha = 0.5)
            if zsurf is not None:
                surface_legend_entries.extend([zsurf])
                gdata.code_It("surface_legend_entries.extend([zsurf])")
            zlb = float(zitem.gxlb.get())
            zub = float(zitem.gxub.get())
    
            if zlower > zlb:
                zlower = zlb
            if zupper < zub:
                zupper = zub
                # upper and lower bounds
        #end of loop through z variables   
        
        ax.set_xlabel(xlab)
        ax.set_ylabel(ylab)
        ax.set_zlabel(zlab)
        ax.set_title(ptitle)
        ax.set_xlim(xlower, xupper)
        ax.set_ylim(ylower, yupper)
        ax.set_zlim(zlower, zupper)
        cstr = f"""
ax.set_xlabel('{xlab}')
ax.set_ylabel('{ylab}')
ax.set_zlabel('{zlab}')
ax.set_title('{ctitle}')
ax.set_xlim({xlower},{xupper})
ax.set_ylim({ylower},{yupper})
ax.set_zlim({zlower}, {zupper})"""
        gdata.code_It(cstr)
        if colorlegend:
            lpatches = cvpatches + lpatches
            gdata.code_It("lpatches = cvpatches + lpatches")
            
        scatter_legend = ax.legend(handles=lpatches, loc='upper right', title='Scatter Plot', bbox_to_anchor=(1.05, 1.1))
        gdata.code_It("scatter_legend = ax.legend(handles=lpatches, loc='upper right', title='Scatter Plot', bbox_to_anchor=(1.05, 1.1))")
        ax.add_artist(scatter_legend)
        gdata.code_It("ax.add_artist(scatter_legend)")
        plt.legend(handles=surface_legend_entries, loc='upper left', title='Smoothings', bbox_to_anchor=(0.00, 1.05))
        gdata.code_It("plt.legend(handles=surface_legend_entries, loc='upper left', title='Smoothings', bbox_to_anchor=(0.00, 1.05))")
        gdata.code_It("fig.show()")
        plt.show()
        
        # #write out the legend code
        
        # #write out the plot label and limits code
        # gdata.code_It(f"ax.set_xlabel('{xlab}')")
        # gdata.code_It(f"ax.set_ylabel('{ylab}')")
        # gdata.code_It(f"ax.set_zlabel('{zlab}')")
        # gdata.code_It(f"ax.set_title('{ctitle}')")
        # gdata.code_It(f"ax.set_xlim({xlower},{xupper})")
        # gdata.code_It(f"ax.set_ylim({ylower},{yupper})")
        # gdata.code_It(f"ax.set_zlim({zlower},{zupper})")
        # #code to show the plot
        # gdata.code_It("#fig.show()")
        # gdata.code_It("plt.show()")
        return

    def plot3DSurf():
        # finally get labels and titles
        # xlab = vx.xlabel.get()
        # ylab = vy.xlabel.get()

        pass

    def plotECDF(self):
        # get the variable data
        if (len(self.master.master.v1list) == 0):
            return
        v1 = self.master.master.v1list[0]
        xv = v1.varname
        cv = self.master.master.selected_color_variable.get()
        mv = self.master.master.selected_marker_variable.get()
        rf = self.master.master.selected_col_variable.get()
        cf = self.master.master.selected_row_variable.get()
        plot_type = self.plotchoice.get()

        # get rid of NA's report resulting sample size in nobs
        vars = [xv, cv, mv, rf, cf]
        active_vars = [item for item in vars if (item != '-')]
        
        df = self.master.master.data.copy(deep=True)
        nobs0 = len(df)
        df.dropna(subset=active_vars, inplace = True)
        nobs = len(df)
        self.master.master.current_data = df #it's ok we don't need to copy the data 

        
        #code to read data in (in log file) and check # rows in original and plotted data
        gdata.code_It("################################")
        gdata.code_It("## Code for ECDF Plot")

        lstr0 = f"df = pd.read_csv('{gdata.fpath}',engine='python')"
        lstr1 = "nobs0 = len(df)"
        lstr2 = f"df.dropna(subset={active_vars}, inplace = True)"
        lstr3 = "nobs = len(df)"
        #lstr4 = "print('CHECK: ' + str(nobs) + ' rows out of ' + str(nobs0))"
        gdata.code_It(" ")
        gdata.code_It(lstr0)
        gdata.code_It(lstr1)
        gdata.code_It(lstr2)
        gdata.code_It(lstr3)
        #gdata.code_It(lstr4)


        # finally get labels and titles
        xlab = v1.xlabel.get()

        xupper = float(v1.xub.get())
        xlower = float(v1.xlb.get())

        ptitle = f"({nobs} rows out of {nobs0})"
        ctitle = f"({nobs} rows out of {nobs0})"
        user_title = self.titlelabel.get()
        if user_title != '':
            ptitle = user_title + "\n" + ptitle
            ctitle = user_title + " \\n " + ctitle

        lg_msg = f" Empirical CDF Plot:  x= {xv}, color= {cv}, marker= {mv}, rows= {rf}, cols= {cf}, Title: {ptitle}"
        gdata.log_It(lg_msg)
        
        palettev = 'bright'
        if (rf == '-'): rf = None
        if (cf == '-'): cf = None
        if (cv == '-'):
            cv = None
            palettev = None
        else:
            palettev = 'bright'
        ecdfparms = {'x':xv, 'hue':cv, 'kind':'ecdf', 'row':rf, 'col':cf, 'palette':palettev }
        # now do the plotting
        fg = sb.displot(df,**ecdfparms)
        lstr = f"fg = sb.displot(df, **{ecdfparms})"
        gdata.code_It(lstr)
        # now do the plotting

        fg.set_axis_labels(xlab, 'Cumulative Probability')
        # fg.set(xlim=(xlower,xupper))
        plt.xlim(xlower, xupper)
        plt.suptitle(t=ptitle, y=0.95)
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)

        gdata.code_It(f"fg.set_axis_labels('{xlab}', 'Cumulative Probability')")
        # fg.set(xlim=(xlower,xupper))
        gdata.code_It(f"plt.xlim({xlower}, {xupper})")
        gdata.code_It(f"plt.suptitle(t='{ctitle}', y=0.95)")
        gdata.code_It("plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)")

        plt.show()
        gdata.code_It("#fg.figure.show()")
        gdata.code_It("plt.show()")
        return

    def plotBoxplot(self):
        # get the seed for dithering
        DOTSIZE = int(self.ditherdotsize.get())
        RSEED = int(self.ditherseed.get())
        np.random.seed(RSEED)
        # get the variable data
        if (len(self.master.master.v1list) == 0):
            return
        v1 = self.master.master.v1list[0]
        xv = v1.varname
        cv = self.master.master.selected_color_variable.get()
        mv = self.master.master.selected_marker_variable.get()
        rf = self.master.master.selected_col_variable.get()
        cf = self.master.master.selected_row_variable.get()
        gv = self.selected_boxplot_grouping_variable.get()
        ditherparm = self.dodither.get()
        # print(f"Dither: {ditherparm}")

        plot_type = self.plotchoice.get()

        # get rid of NA's report resulting sample size in nobs
        vars = [xv, cv, mv, rf, cf, gv]

        active_vars = list(set([item for item in vars if (item != '-')]))
        df = self.master.master.data.copy(deep = True)
        nobs0 = len(df)
        df.dropna(subset=active_vars, inplace = True)
        nobs = len(df)
        self.master.master.current_data = df #it's ok we don't need to copy the data 

        gdata.code_It("################################")
        gdata.code_It("## Code for Box Plot")

        #code to read data in (in log file) and check # rows in original and plotted data
        lstr0 = f"df = pd.read_csv('{gdata.fpath}',engine='python')"        
        lstr1 = "nobs0 = len(df)"
        lstr2 = f"df.dropna(subset={active_vars}, inplace = True)"
        lstr3 = "nobs = len(df)"
        #lstr4 = "print('CHECK: ' + str(nobs) + ' rows out of ' + str(nobs0))"
        gdata.code_It(" ")
        gdata.code_It(lstr0)
        gdata.code_It(lstr1)
        gdata.code_It(lstr2)
        gdata.code_It(lstr3)
        #gdata.code_It(lstr4)



        # finally get labels and titles
        ylab = v1.xlabel.get()
        xlab = cv

        ptitle = f"({nobs} rows out of {nobs0})"
        ctitle = f"({nobs} rows out of {nobs0})"

        user_title = self.titlelabel.get()
        if user_title != '':
            ptitle = user_title + "\n" + ptitle
            ctitle = user_title + " \\n " + ctitle 

        lg_msg = f" #1 Box Plot x= {cv}, y= {xv}, color= {
            cv}, gv = {gv}, rows= {rf}, cols= {cf}"
        # print(lg_msg)
        gdata.log_It(lg_msg)

        rfp = None  # row facet
        cfp = None  # column facet
        cvp = None  # color variable
        gvp = None  # grouping or x variable
        yvp = xv  # y variable (values to use for boxplot)
        palettep = None  # palette identifier (string)

        if rf != '-':
            rfp = rf
        if cf != '-':
            cfp = cf
        if cv != '-':
            cvp = cv
            palettep = 'bright'
        if gv != '-':
            gvp = gv
        # if cv is set but gv is not, set gv = cv
        if (cv != '-') & (gv == '-'):
            gvp = cv
            gv = cv

        if (gv != '-') & (cv != '-') & (gv != cv) & (ditherparm == 'Yes'):
            dmsg = f"color = {cv};  grouping = {
                gv}.  When color and grouping \nvariables don't match dithering is unpredictable. \nContinue?"
            dithercheck = messagebox.askyesno("Dither Issue", dmsg)
            if (not dithercheck):
                return

        if (ditherparm == 'Yes'):  # outliers are redundant when dithering (I always wanted to say that)
            fliersp = False
        else:
            fliersp = True

        lg_msg = f"Box Plot  x= {gvp}, y= {yvp}, hue= {cvp}, rows= {rfp}, cols= {
            cfp}, palette= {palettep}, | gv = {gv}, dither = {ditherparm}"
        gdata.log_It(lg_msg)
        # now do the plotting
        boxparms = {'x':gvp, 'y':yvp, 'hue':cvp, 'row':rfp, 'col':cfp, 'palette': palettep, 'kind':'box', 'legend':'full', 'showfliers': fliersp }
        try:
            # fg = sb.catplot(df, x=gvp, y=yvp, hue=cvp, row=rfp, col=cfp,
            #                 palette=palettep, kind='box', showfliers=fliersp,)
            fg = sb.catplot(df,**boxparms)
            lstr = f"fg=sb.catplot(df,**{boxparms})"
            gdata.code_It(lstr)
            
        except Exception as er:
            print("Plotting Error: " + str(er))
            return
        if ditherparm == 'Yes':
            np.random.seed(RSEED)
            ditherparms = {'y':yvp, 'x':gvp, 'jitter': True, 'alpha':0.6, 'size':DOTSIZE, 'color':'black'}
            #fg.map_dataframe(sb.stripplot, y=yvp, x=gvp, jitter=True, alpha=0.6, size=DOTSIZE, color='black')
            fg.map_dataframe(sb.stripplot,**ditherparms)
            gdata.code_It(f"np.random.seed({RSEED})")
            gdata.code_It(f"fg.map_dataframe(sb.stripplot, **{ditherparms})")

        fg.set_axis_labels(xlab, ylab)
        gdata.code_It(f"fg.set_axis_labels('{xlab}', '{ylab}')")
        plt.suptitle(t=ptitle, y=0.95)
        gdata.code_It
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        gdata.code_It("plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)")

        plt.show()
        gdata.code_It("plt.show()")
        gdata.code_It
        return

    def plotHistogram(self, *args):  # finally we're going to make a plot happen!
        # get the variable data
        if (len(self.master.master.v1list) == 0):
            return
        v1 = self.master.master.v1list[0]
        xv = v1.varname
        cv = self.master.master.selected_color_variable.get()
        mv = self.master.master.selected_marker_variable.get()
        rf = self.master.master.selected_col_variable.get()
        cf = self.master.master.selected_row_variable.get()

        plot_type = self.plotchoice.get()

        vars = [xv, cv, mv, rf, cf]

        active_vars = [item for item in vars if (item != '-')]

        df = self.master.master.data.copy(deep=True)
        nobs0 = len(df)
        df.dropna(subset=active_vars, inplace = True)
        nobs = len(df)
        self.master.master.current_data = df #it's ok we don't need to copy the data 

        gdata.code_It("################################")
        gdata.code_It("## Code for Histogram Plot")

        
        #code to read data in (in log file) and check # rows in original and plotted data
        lstr0 = f"df = pd.read_csv('{gdata.fpath}',engine='python')"
        lstr1 = "nobs0 = len(df)"
        lstr2 = f"df.dropna(subset={active_vars}, inplace = True)"
        lstr3 = "nobs = len(df)"
        #lstr4 = "print('CHECK: ' + str(nobs) + ' rows out of ' + str(nobs0))"
        gdata.code_It(" ")
        gdata.code_It(lstr0)
        gdata.code_It(lstr1)
        gdata.code_It(lstr2)
        gdata.code_It(lstr3)
        #gdata.code_It(lstr4)



        xupper = float(v1.xub.get())
        xlower = float(v1.xlb.get())

        # set some local histogram parameters
        # override bins
        nbins = self.nobins.get()
        if nbins != 'auto':
            nbins = int(nbins)
        # add a kde plot
        KDE = False
        if self.dokde.get() == 'Yes':
            KDE = True

        # dfig = self.master.master.fig
        # axh = self.master.master.ax
        # axh.clear()

        # finally get labels and titles
        xlab = v1.xlabel.get()

        ptitle = f"({nobs} rows out of {nobs0})"
        ctitle = f"({nobs} rows out of {nobs0})"
        user_title = self.titlelabel.get()
        if user_title != '':
            ptitle = user_title + "\n" + ptitle
            ctitle = user_title + " \\n " + ctitle
        
        palettev = 'bright'
        if rf == '-': rf = None
        if cf == '-': cf = None
        if cv == '-': 
            cv = None
            palettev= None

        histparms = {'x': xv, 'hue': cv, 'row': rf, 'col':cf,  'kde': KDE, 'bins': nbins, 'palette': palettev, 'facet_kws': dict(margin_titles = True)}
        # now do the plotting
        
        fg = sb.displot(df,**histparms)
        
        gdata.code_It(f"fg=sb.displot(df, **{histparms})")
        fg.set_axis_labels(xlab, 'Count')
        fg.set(xlim=(xlower, xupper))
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        plt.suptitle(t=ptitle, y=0.95)
        
        gdata.code_It(f"fg.set_axis_labels('{xlab}', 'Count')")
        gdata.code_It(f"fg.set(xlim=({xlower}, {xupper}))")
        gdata.code_It("plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)")
        gdata.code_It(f"plt.suptitle(t='{ctitle}', y=0.95)")
 
        plt.show()
        gdata.code_It("plt.show()")
        gdata.code_It("#fg.figure.show()")
        return


if __name__ == "__main__":
    gdata = gd.globalData()

    class solo(tk.Tk):
        def __init__(self):
            super().__init__()
            self.title("Data Plot Stand Alone App")
            self.geometry("400x50+0+0")
            self.onButton = tk.Button(
                self, text="Get Data", command=self.getData).pack(side=tk.LEFT, padx=10)
            self.goPlt = tk.Button(self, text="Plot Data", command=self.pltD).pack(
                side=tk.LEFT, padx=10)
            self.offButton = tk.Button(
                self, text="Graceful Exit", command=self.quit).pack(side=tk.LEFT, padx=10)

            # gst = goPivot(self)

        def pltD(self, *args):
            if len(gdata.data) == 0:
                return
            self.gst = goPlot()
            self.gst.syncData()

        def quit(self, *args):
            plt.close('all')
            self.destroy()
            return

        def getData(self, *args):
           # self.dfDisplay()
           # file_types = [("CSV Files", "*.csv"), ("Text Files", "*.txt"), ("All Files", "*.*")]
            file_types = [("CSV Files", "*.csv"), ("Excel Files",
                                                   "*.xlsx"), ("Stata Files", "*.dta")]
            file_path = filedialog.askopenfilename(
                filetypes=file_types, title="Select a File")
            if file_path != '':
                df_in = pd.read_csv(file_path)
                self.fpath = file_path
                gdata.reset_Data(file_path, df_in)
            return

    app = solo()
    app.mainloop()

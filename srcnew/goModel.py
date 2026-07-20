#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 27 21:49:03 2025

@author: Knucklehead and Copilot (for  refactoring)
"""# Refactored: Tkinter app as a class

from patsy import dmatrices, NAAction
from sklearn.metrics import roc_curve, auc
from datetime import datetime

import pandas as pd
from pandas.api.types import is_numeric_dtype

import Regression as rg

import Graphics as grp
from statsmodels.graphics.regressionplots import influence_plot, plot_leverage_resid2

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

import matplotlib
import matplotlib.pyplot as plt


# from matplotlib.backends.backend_tkagg import (
#     FigureCanvasTkAgg, # interface between Figure class and Tkinter's Canvas
#     NavigationToolbar2Tk # built-in toolbar for the figure
#     )

import seaborn as sb
#sb.set_style("darkgrid", {"grid.color": ".6", "grid.linestyle": ":"})

#import globalData as gd
#import goDataFilter as godf
#import goPlot as gopt

from globalData import gdata

"""
Notes:
    
    gdata.fitdata is not None signals model is current, and fit succesfully -- whether appropriate to the data or not.
    gdata.fitdata is None signals model has been edited and not re-fitted, model fit failed, or any other event that might
        put model plotting out of sync with the intended model.   In particuar changeIndVar, changeDepVar and clearModel all 
        trigger gdata.fitdata being reset to None.  Anything that needs a fitted model consistent with the model displayed
        needs to have gdata.fitdata is not None.
"""
        
# basecolors0 = ['red',  'blue', 'green', 'goldenrod', 'violet','cyan', 
#                'yellow','grey','gold','magenta',
#                'silver','orange','olive','khaki','thistle']

basecolors0 = ['blue', 'red',  'green', 'yellow', 'magenta', 'cyan', 'violet', 
               'orange',  'goldenrod','grey','gold','silver','orangered', 'darkolivegreen',
               'olive','khaki','thistle','lightsteelblue','slateblue','black','darkviolet',
               'brown', 'indigo', 'hotpink', 'lavender']


basecolorsalpha = ['red',  'blue', 'green', 'goldenrod', 'violet', 'yellow','grey','gold','magenta','coral']
basecolors = [matplotlib.colors.to_rgba(item,alpha = None) for item in basecolorsalpha]
protected_names = ['Residuals','Predictions','Deviance_Resid']
   


class mdlStack():
    def __init__(self):
        self.model_string_stack = []
        self.ivar_stack = []
        self.dvar_stack = []
        self.stack_level = -1
    
    def dump_stack(self):
        dumpstring = "\n".join(self.model_string_stack)
        return dumpstring
    
    def clear_stack(self):
        self.model_string_stack = []
        self.ivar_stack = []
        self.dvar_stack = []
        self.stack_level = -1
        

mtypes = ['OLS', 'GAMMA', 'LOGIT', 'PROBIT', 'POISSON', 'NEGATIVE BINOMIAL']



links = {'GAMMA':[ 'Log', 'Identity', 'InversePower'],
         'POISSON':['Log', 'Identity', 'Sqrt'],
         'NEGATIVE_BINOMIAL': ['Log', 'Identity', 'Power', 'CLogLog', 'NegativeBinomial'],
         'PROBIT': ['InverseNormal'],
         'LOGIT': ['Logit'],
         'OLS': ['Identity']
         }

G1types = ['Histogram', 'CDF', 'Box Plot' ]
G2Options= ['Response Curve','Lower CI','Upper CI','ROC']

markers = ['Dot', 'Line']

#class RegressionApp(tk.Tk):
class RegressionApp(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("Linear Models Tools")
        self.geometry('%dx%d+%d+%d' % (1180, 550, 0, 0))
        self.protocol("WM_DELETE_WINDOW", self.exit_closing)

        gdata.inputdata = pd.DataFrame()
        gdata.model_vars = ['-']
        gdata.fname = 'None'
        gdata.model_string = '~'

        
        #model stack
        self.mstk = mdlStack()
        
        # Variables
        self.datafilename = tk.StringVar(self)
        self.datafilename.set(gdata.fname)
        self.ModelStr = tk.StringVar(self)
        self.clickedX = tk.StringVar(self)
        self.clickedY = tk.StringVar(self)
        self.clickedX.set('-')
        self.clickedY.set('-')
        self.clickedGC = tk.StringVar(self)
        self.meqn = tk.StringVar(self,value='')
        self.Pr = tk.IntVar(self)
        self.Rs = tk.IntVar(self)
        self.selected_model = tk.StringVar(self, mtypes[0])
        self.nbparm_alpha = tk.StringVar(self, '')
        self.siglev = tk.StringVar(self, str(0.05))
        self.gbins = tk.StringVar(self)
        self.xlb = tk.StringVar(self)
        self.xub = tk.StringVar(self)
        self.ylb = tk.StringVar(self)
        self.yub = tk.StringVar(self)
        self.zlb = tk.StringVar(self)
        self.zub = tk.StringVar(self)
        self.selected_plot1da = tk.StringVar(self, G1types[0])
        self.selected_plot1db = tk.StringVar(self, 'No')
        self.selected_response = tk.IntVar(self, 0)
        self.selected_ci = tk.IntVar(self, 0)
        self.selected_pi = tk.IntVar(self, 0)
        self.clickedResidX = tk.StringVar(self)
        self.clickedPredictX = tk.StringVar(self)
        self.clickedDependentX = tk.StringVar(self)
        self.clickedLink = tk.StringVar(self,'Identity')

        # Build UI
        self.build_frames()
        
        #instantiate current data.
        self.syncData()
        
        return


    def build_frames(self):
        # Frame 1
        self.mf1 = tk.Frame(self, borderwidth=2, relief="ridge", highlightthickness=0)
        self.mf1.pack(fill='x', padx=10, pady=5, expand=False)
        RRow = 0
        tk.Label(self.mf1, text="File: ", font=('Arial', 14, 'bold')).grid(row=RRow, column=1, sticky='w', padx=10)
        tk.Label(self.mf1, textvariable=self.datafilename).grid(row=RRow, column=2, columnspan=5, padx=10, sticky='w')

        RRow = 1
        tk.Label(self.mf1, text='Model: ', bg="blue", fg="white", font=('Arial', 14, 'bold')).grid(row=RRow, column=0, sticky='w', padx=10)
        tk.Entry(self.mf1, textvariable=self.meqn, width=80).grid(row=RRow, column=1, columnspan=5, sticky='w', padx=10)

        RRow = 2
        tk.Label(self.mf1, text="Dependent Variable:").grid(row=RRow, column=0, sticky='w', padx=10)
        numeric_columns = [item for item in gdata.inputdata.columns if is_numeric_dtype(gdata.inputdata[item])]
        self.cy = ttk.Combobox(self.mf1, values=numeric_columns, textvariable=self.clickedY)
        self.cy.grid(row=RRow, column=1, sticky='w')
        self.cy.bind("<<ComboboxSelected>>", self.changeDepVar)
        tk.Label(self.mf1, text="Independent Variables:").grid(row=RRow, column=2, sticky='e')
        self.cx = ttk.Combobox(self.mf1, values=gdata.model_vars, textvariable=self.clickedX)
        self.cx.grid(row=RRow, column=3, sticky='w')
        #self.cx.grid(row=RRow, column=0, sticky='w')
        self.cx.bind("<<ComboboxSelected>>", self.changeIndepVar)
        bf1 = tk.Frame(self.mf1)
        bf1.grid(row=RRow, column=4, columnspan=3)
        tk.Button(bf1, text='Clear Model', command=self.clearModel).pack(side=tk.LEFT)
        tk.Button(bf1, text="Save", command=self.saveModel).pack(side=tk.LEFT)
        tk.Button(bf1, text='Recall', command=self.pullModel).pack(side=tk.LEFT)

        # Frame 2
        self.mf2 = tk.Frame(self, borderwidth=2, relief="ridge", highlightthickness=0)
        self.mf2.pack(fill='x', padx=10, pady=5)
        RRow = 0
        tk.Label(self.mf2, text="Model Type:", font=('Arial', 14, 'bold')).grid(row=RRow, column=0, sticky='w', padx=10)
        col = 1
        for item in mtypes:
            tk.Radiobutton(self.mf2, text=item, variable=self.selected_model, value=item,command = self.model_choice).grid(row=RRow, column=col, sticky='w')
            col += 1
        RRow = 1
        
        self.over_dispLabel = tk.Label(self.mf2, text="Overdispersion:")
        #over_dispLabel.grid(row=RRow, column=8, sticky='e')
        self.over_dispLabel.grid_forget()
        
        self.over_disp_ent = tk.Entry(self.mf2, textvariable=self.nbparm_alpha, width=3)
        #over_disp_ent.grid(row=RRow, column=7, sticky='w')
        self.over_disp_ent.grid_forget()
        
        self.over_dispParmLabel = tk.Label(self.mf2, text="(>=0, no entry triggers estimation of o.d. param)")
        #over_dispParmLabel.grid(row=RRow, column=8, sticky='w')
        self.over_dispParmLabel.grid_forget()
        
        self.linkfrm = tk.Frame()
        
        self.linklab = tk.Label(self.mf2, text="Link:") #TODO: complete this
        self.linklab.grid(row=RRow, column=3, sticky='e')
        #self.linklab.grid_forget()
        self.link = ttk.Combobox(self.mf2, values=links[self.selected_model.get()], textvariable=self.clickedLink)
        self.link.grid(row=RRow, column=4, columnspan = 2,sticky='w')
        self.link.bind("<<ComboboxSelected>>", self.setLink)

        
        tk.Label(self.mf2, text="Signficance level:").grid(row=RRow, column=0, sticky='e', padx=20)
        tk.Entry(self.mf2, textvariable=self.siglev, width=3).grid(row=RRow, column=1, sticky='w')

        RRow = 2
        tk.Button(self.mf2, text="Run Model", command=self.runModel).grid(row=RRow, column=0)
        tk.Button(self.mf2, text="Report", command=self.showReport).grid(row=RRow, column=1)
        tk.Button(self.mf2, text="Log", command=self.showLog).grid(row=RRow, column=2)
        self.buttonSaveDes = tk.Button(self.mf2, text="Save Model Fit Output", command=self.saveDes)
        self.buttonSaveDes.grid(row=RRow, column=4, columnspan = 2)
        tk.Button(self.mf2, text="Save Model Input Data Only", command=self.saveDmatOnly).grid(row=RRow, column=6)
        tk.Button(self.mf2, text="Forecast using the model.", command = self.forecast).grid(row = RRow, column = 7)

        # Frame 3
        self.mf3 = tk.Frame(self, borderwidth=2, relief="ridge", highlightthickness=0)
        self.mf3.pack(fill='x', padx=10, pady=5, expand=False)
        RRow = 0
        msg = '                                                                               '
        msg1 = msg + msg + msg + msg
        tk.Label(self.mf3, text=msg1, fg="white").grid(row=RRow, column=0, columnspan=10, sticky='w', padx=10)
        tk.Label(self.mf3, text='Graphics: ', bg="blue", fg="white").grid(row=RRow, column=0, sticky='w', padx=10)
        tk.Label(self.mf3, text=" Mark Data with:").grid(row=RRow, column=1, sticky='w')
        self.gc = tk.OptionMenu(self.mf3, self.clickedGC, ['-'], command=self.makePlotc)
        self.gc.grid(row=RRow, column=2, sticky='w')
        tk.Label(self.mf3, text='Pen Size:').grid(row=RRow, column=3, sticky='w')
        self.gpen = tk.Scale(self.mf3, from_=1.0, to=50.0, orient='horizontal', showvalue=True)
        self.gpen.grid(row=RRow, column=4)
        self.gpen.set(5)

        # Graphing options
        self.grp0 = tk.Frame(self.mf3, borderwidth=2, relief="flat", highlightthickness=0)
        self.grp0.grid(row=4, column=0, columnspan=6, rowspan=4)
        self.grp2d = tk.Frame(self.grp0, borderwidth=1, relief=tk.RIDGE)
        self.grp3d = tk.Frame(self.grp0, borderwidth=1, relief=tk.RIDGE)
        self.grp3d.pack(side=tk.LEFT, fill='x', padx=20, anchor='w', expand=True)
        
        tk.Label(self.grp2d, text=' 2 & 3 dimension model plots').grid(row=0, column=0, sticky='w')
        tk.Button(self.grp2d, text="Model Plot", command=self.modelplot).grid(row=1, column=0)
        #tk.Checkbutton(self.grp2d, text="Resp.", variable=self.selected_response, onvalue=1, offvalue=0, height=3, width=5).grid(row=1, column=1, padx=5)
        tk.Checkbutton(self.grp2d, text="CI", variable=self.selected_ci, onvalue=1, offvalue=0, height=3, width=3).grid(row=1, column=2, padx=5)
        self.pint = tk.Checkbutton(self.grp2d, text="PI", variable=self.selected_pi, onvalue=1, offvalue=0, height=3, width=3)
        #self.pint.grid(row=1, column=3, padx=10)
        self.pint.grid_forget()
        #self.grp2d.pack(side=tk.LEFT, expand=True, anchor='w')
        self.grp2d.pack_forget()
        tk.Label(self.grp3d, text='Model Plotting Tools').grid(row=0, column=0, sticky='w')
        self.rocbutton= tk.Button(self.grp3d, text='ROC-AUC', command=self.doroc)
        self.rocbutton.grid(row=1, column=0)
        self.rocbutton.grid_forget()
        tk.Button(self.grp3d, text='Correlations', command=self.docorr).grid(row=1, column=2)
        tk.Button(self.grp3d, text='Leverage', command=self.doleverage).grid(row=2, column=0)
        self.influencebutton = tk.Button(self.grp3d, text='Influence', command=self.doinfluence)
        self.influencebutton.grid(row=2, column=2)
        self.influencebutton.grid_forget()
        tk.Label(self.grp3d, text="Plot residuals against:").grid(row=3, column=0)
        self.residualmenu = tk.OptionMenu(self.grp3d, self.clickedResidX, ['-'], command=self.doresidual)
        self.residualmenu.grid(row=3, column=1, columnspan=2)
        tk.Label(self.grp3d, text="Plot fitted values against:").grid(row=4, column=0)
        self.predictmenu = tk.OptionMenu(self.grp3d, self.clickedPredictX, ['-'], command=self.dopredict)
        self.predictmenu.grid(row=4, column=1, columnspan=2)
        tk.Label(self.grp3d, text="Fitted and Actual against:").grid(row=5, column=0)
        self.dependentmenu = tk.OptionMenu(self.grp3d, self.clickedDependentX, ['-'], command=self.showFit)
        self.dependentmenu.grid(row=5, column=1, columnspan=2)
        #self.plotbutton = tk.Button(self.grp3d, text="Plot",command = self.doModelPlot)
        #self.plotbutton.grid(row=6, column = 1, sticky = 'e')
        self.plothint = tk.Label(self.grp3d, text="To refresh plot, re-choose variable").grid(row = 6, column =1)
        self.mf3.pack_forget()

      # Frame 4
        RRow = 0
        self.mf4 = tk.Frame(self, borderwidth=1, relief="ridge", highlightthickness=0, padx=10, pady=5)
        tk.Label(self.mf4, text = "Forecast:", bg="blue", fg="white").grid(row=RRow, column=0, sticky='w', padx=10)

        # Toplevel windows
        self.repwin = tk.Toplevel(self)
        self.repwin.title("Report Viewer \n(most recent at top)")
        self.repwin.geometry("800x300")
        self.repwin.wm_protocol("WM_DELETE_WINDOW", self.hideRep)
        self.text_area = scrolledtext.ScrolledText(self.repwin, wrap=tk.WORD, width=100, height=40)
        self.text_area.pack(padx=10, pady=5)
        self.repwin.withdraw()
        self.logwin = tk.Toplevel(self)
        self.logwin.title("Log File Viewer")
        self.logwin.wm_protocol("WM_DELETE_WINDOW", self.hideLog)
        self.log_area = scrolledtext.ScrolledText(self.logwin, wrap=tk.WORD, width=100, height=40)
        self.log_area.pack(padx=10, pady=5)
        self.logwin.withdraw()
        

 
    # Example for getData, updateData, etc. You need to refactor all functions to methods and update references accordingly.
    
    def setLink(self,*args):
        gdata.link = self.clickedLink.get()
        return
    
    def model_choice(self, *args):
        mdl = self.selected_model.get()
        RRow = 1
        if mdl == 'NEGATIVE BINOMIAL':
            self.over_dispLabel.grid(row=RRow, column=6, sticky='e')
            self.over_disp_ent.grid(row=RRow, column=7, sticky='w')
            self.over_dispParmLabel.grid(row=RRow, column=8, sticky='w')
            self.linklab.grid(row = RRow, column = 3,sticky='w')
            self.link.grid(row = RRow, column = 4, columnspan = 2,sticky = "w")
            self.link['values'] = links['NEGATIVE_BINOMIAL']
            self.clickedLink.set('Log')
        elif (mdl == 'GAMMA'):
            self.linklab.grid(row = RRow, column = 3,sticky='w')
            self.link.grid(row = RRow, column = 4,columnspan = 2, sticky = "w")
            self.link['values'] = links['GAMMA']
            self.over_dispLabel.grid_forget()
            self.over_disp_ent.grid_forget()
            self.over_dispParmLabel.grid_forget()
            self.clickedLink.set('Log')
        elif (mdl == 'POISSON'):
            self.linklab.grid(row = RRow, column =3,sticky='w')
            self.link.grid(row = RRow, column = 4,columnspan = 2, sticky  = "w")
            self.link['values'] = links['POISSON']
            self.over_dispLabel.grid_forget()
            self.over_disp_ent.grid_forget()
            self.over_dispParmLabel.grid_forget()
            self.clickedLink.set('Log')
        else:
            self.over_dispLabel.grid_forget()
            self.over_disp_ent.grid_forget()
            self.over_dispParmLabel.grid_forget()
            #self.link.grid_forget()
            #self.linklab.grid_forget()
            self.link['values'] = links[mdl]
            self.clickedLink.set(links[mdl][0])
        return
    
    def hideRep(self, *args):
        self.repwin.withdraw()
        return

    def hideLog(self, *args):
        self.logwin.withdraw()
        return
    
    
    def syncData(self, *args):
        if (len(gdata.data)>0):
            filename = gdata.fpath
            gdata.inputdata = gdata.data.copy(deep = True)
            gdata.fname = gdata.fpath
            gdata.model_vars = ['-'] + list(gdata.inputdata.columns)
            gdata.fitdata = None
            gdata.model_string = '~'
            self.cy['values'] = gdata.model_vars
            self.cx['values'] = gdata.model_vars
            self.datafilename.set(filename)
            self.text_area.delete("1.0",tk.END)
            self.clearModel()
            plt.close('all')
        else:
            return
        return
    def forecast(self, *args):
        #open the forecast window
        #self.mf4.pack(side=tk.TOP) 
        self.mf4.pack(fill='x', padx=10, pady=5, expand=False)            

        return
    # def updateData(self, *args):
    #     gdata.data = pd.DataFrame()
    #     gdata.fpath = ''
    #     self.getData()
    #     return
    
    def saveModel(self, *args):
        self.mstk.model_string_stack.append(self.meqn.get())
        self.mstk.ivar_stack.append(gdata.indvars)
        self.mstk.dvar_stack.append(gdata.depvar)
        return
    
    def pullModel(self, *args):
        if len(self.mstk.model_string_stack) == 0 :
            return
        if self.mstk.stack_level <= -len(self.mstk.model_string_stack):
            self.mstk.stack_level = -1 #we're at the end reset the stack level
        else:
            self.mstk.stack_level -= 1 #decrement stack level
        mstring = self.mstk.model_string_stack[self.mstk.stack_level]
        self.meqn.set(mstring)
        gdata.model_string = mstring
        gdata.indvars = self.mstk.ivar_stack[self.mstk.stack_level]
        gdata.depvar = self.mstk.dvar_stack[self.mstk.stack_level]
        return
    
    def changeIndepVar(self, *args):
        xstr = str(self.clickedX.get())
        if xstr == "-":
            return
        elif gdata.depvar == xstr:
            messagebox.showerror(' ', f"The variable {xstr} is also the dependent variable.  \n This model is self-explanatory. \nYou're making this too easy!")
            return
        else:
            if xstr not in gdata.indvars:
                if len(gdata.indvars) == 0:
                    gdata.model_string += xstr
                else:
                    gdata.model_string += '+' + xstr
                gdata.indvars.add(xstr)
        self.meqn.set(gdata.model_string)
        c0 = set()
        current_varset = c0.union(gdata.indvars, set([gdata.depvar]))
        remaining_varlist = ['-'] + [item for item in list(gdata.inputdata.columns) if item not in current_varset]
        self.cx['values'] = remaining_varlist
        
        #complexity: dependent variable must be a number
        numeric_columns = [item for item in gdata.inputdata.columns if is_numeric_dtype(gdata.inputdata[item])]
        remaining_varlist = ['-'] + [item for item in numeric_columns if item not in current_varset]
        self.cy['values'] = remaining_varlist
         
        gdata.fitdata = None
        return
    
    def changeDepVar(self, *args):
        ystr = str(self.clickedY.get())
        if ystr == gdata.depvar:
            return
        elif ystr == "-":
            return
        else:
            gdata.depvar = ystr
            if len(gdata.model_string.split("~")) < 2:
                gdata.model_string = ystr + '~'
            else:
                gdata.model_string = ystr + '~' + gdata.model_string.split("~")[1]
            
        self.meqn.set(gdata.model_string)
        c0 = set([''])
        current_varset = c0.union(gdata.indvars, set([gdata.depvar]))
        remaining_varlist = ['-'] + [item for item in gdata.inputdata.columns if item not in current_varset]
        self.cx['values'] = remaining_varlist
        
        #complexity: dependent variable must be a number
        numeric_columns = [item for item in gdata.inputdata.columns if is_numeric_dtype(gdata.inputdata[item])]
        remaining_varlist = ['-'] + [item for item in numeric_columns if item not in current_varset]
        self.cy['values'] = remaining_varlist
        
        gdata.fitdata = None
        return
    
    def clearModel(self):
        gdata.depvar = ""
        gdata.indvars = set([])
        gdata.model_string = '~'
        self.meqn.set(gdata.model_string)
        self.clickedY.set(gdata.model_vars[0])
        self.clickedX.set(gdata.model_vars[0])
        gdata.fitdata = None
        if (self.buttonSaveDes.winfo_ismapped()):
            self.buttonSaveDes.grid_forget()
        self.cx['values'] = list(gdata.inputdata.columns)
        numeric_columns = [item for item in gdata.inputdata.columns if is_numeric_dtype(gdata.inputdata[item])]
        self.cy['values'] = list(numeric_columns)
        return
    
    def runModel(self, *args):
        gdata.model_type = str(self.selected_model.get())
        gdata.link = str(self.link.get())
        gdata.sig_level = 0.05
        temp = self.siglev.get()
        gdata.code_It(f"depvar = '{gdata.depvar}'")
        gdata.code_It(f"indvars = {list(gdata.indvars)}")
        try:
            gdata.sig_level = float(temp)
        except Exception as er:
            messagebox.showwarning("nh", f"{er}: Significance level must be a number between 0 and 1. \n you entered :{temp}\n Defaulting to 0.05")
            gdata.sig_level = 0.05
        if gdata.sig_level <= 0 or gdata.sig_level >= 1:
            messagebox.showwarning("nh", f"Significance level must be a number between 0 and 1. \n you entered :{temp}\n Defaulting to 0.05")
            gdata.sig_level = 0.05
        gdata.model_string = str(self.meqn.get())
        mdlist = gdata.model_string.split("~")
        if (mdlist[0] == '') or (mdlist[1] == ''): 
            messagebox.showwarning("nh", f"Incomplete Model specification: {gdata.model_string}. You need a dependent and one or more independent variables. \nTry again!")
            return
        #tempods: temporary overdispersion: holder for the tkinter input string (Negative Binomial only)
        tempods = ''
        #default overdispersion parameter 
        tempod = 1.0
        if gdata.model_type == 'NEGATIVE BINOMIAL':
            tempods = self.nbparm_alpha.get()
            if tempods == '':
                tempod = -1
            else:
                tempod = float(self.nbparm_alpha.get())
            if tempod < 0:
                tempod = -1
            #if tempod > 2.0:
                #tempod = 2.0
            gdata.overdispersion = tempod
        gdata.fitdata = None
####################################################################
########### Run the model
        gdata.log_It("\n:Model:\n")
        gdata.log_It(f"Fitting the model: {gdata.model_string} type = {gdata.model_type}")
        rtemp = rg.goModel()
####################################################################
        mdl_res, res = rtemp #retrieve fitting data and results 
        if mdl_res is not None:           
####################################################################
####################################################################
########### Stash model data and results in the global data structure
            gdata.model_res = res
            gdata.model_data = mdl_res.copy(deep = True)
####################################################################
####################################################################
            #update the report window aka text_area
            repstr = ''

            #yhat = res.fittedvalues
            repstr = grp.do_Report(res = res, model_string = gdata.model_string, alpha = gdata.sig_level, model_type = gdata.model_type)
          
            self.text_area.insert('1.0', '\n' + repstr)
            gdata.log_It('\n'+str(repstr))
            gdata.code_It(f"print(grp.do_Report(res = res, model_string = '{gdata.model_string}', alpha = {gdata.sig_level}, model_type = '{gdata.model_type}'))")
            #self.log_area.insert(tk.END, rlog)
            gphv = list(mdl_res.columns)
            #gphvars = [item for item in gphv if len(mdl_res[item].unique()) <= len(basecolors0)]
            gphvars = gphv
            gphvars.insert(0, "-")
            #nuvars = list(mdl_res.columns)
            mdlvars = list(res.params.index)
            #print(f"mdlvars: {', '.join(mdlvars)} \n nuvars: {', '.join(nuvars)}")
            gdata.modelres = res
            gdata.fitdata = mdl_res.copy(deep = True)

            #gdata.put_Data(mdl_res.copy(deep = True))
            
            #adjust the grahics choices based on the model type    
            self.update_option_menu_colors(gphvars)
            self.update_option_menu_vars(mdlvars + ['Predictions'])
            if (not self.buttonSaveDes.winfo_ismapped()):
                self.buttonSaveDes.grid(row = 2, column = 10)
            self.mf3.pack()
            if gdata.model_type in ['LOGIT','PROBIT']:
                self.rocbutton.grid(row = 1, column=0)
            else:
                self.rocbutton.grid_forget()
            if gdata.model_type in ['OLS']:
                self.influencebutton.grid(row = 2, column = 2)
                self.pint.grid(row=1, column=3, padx=10)
            else:
                self.influencebutton.grid_forget()
                self.pint.grid_forget()
            if (len(gdata.indvars)<=2):
                if not (self.grp2d.winfo_ismapped()):
                    self.grp2d.pack()
            if (len(gdata.indvars)>2):
                if (self.grp2d.winfo_ismapped()):
                    self.grp2d.pack_forget()
                
            #add model graphics to generated code
            gdata.code_It('#### Model Graphics Options (comment or uncomment as needed)####') 
        else:
            # emsg = "Model Fit Failed.  Check the log file,"
            # emsg += "\nmodel formula, model type, data."
            # emsg += "\nVariable names may contain only letters,numbers and underscores and no leading numbers. "
            # emsg += "\nRename non-conforming variable names or enclose in Q(\"..\") "
            # emsg += "\nOtherwise, check with Dr. Knucklehead."
            # messagebox.showerror(" ",emsg)
            gdata.fitdata = None
            if (self.buttonSaveDes.winfo_ismapped()):
                self.buttonSaveDes.grid_forget()
            return
        return
    
    def showReport(self, *args):
        if self.repwin.winfo_viewable(): 
            self.repwin.lift()
            return
        #self.repwin.update()
        self.repwin.deiconify()
        return
    
    def showLog(self, *args):
        if self.logwin.winfo_viewable(): 
            self.logwin.lift()
            self.log_area.delete("1.0", tk.END)
            self.log_area.insert(tk.END, gdata.logstr) 
            return
        #self.logwin.update()
        self.logwin.deiconify()
        self.log_area.delete("1.0", tk.END)
        self.log_area.insert(tk.END, gdata.logstr) 
        return
    
    def makePlotc(self, *args):
        return
    
    def update_option_menu_colors(self, vnames):
        self.gc['menu'].delete(0, 'end')
        new_options = vnames
        for item in new_options:
            self.gc['menu'].add_command(label=item, command=tk._setit(self.clickedGC, item, self.makePlotc))
        self.clickedGC.set('-')
        return
    
    def update_option_menu_vars(self, vnames):
        self.residualmenu['menu'].delete(0,'end')
        self.predictmenu['menu'].delete(0,'end')
        self.dependentmenu['menu'].delete(0,'end')
        new_options = vnames
        for item in new_options:
            self.residualmenu['menu'].add_command(label=item, command=tk._setit(self.clickedResidX, item, self.doresidual))
            #for these two graphics, graphing against predictions is not relevant
            if item != 'Predictions':
                self.predictmenu['menu'].add_command(label=item, command=tk._setit(self.clickedPredictX, item, self.dopredict))
            if item != 'Predictions':
                self.dependentmenu['menu'].add_command(label=item, command=tk._setit(self.clickedDependentX, item, self.showFit))
        self.clickedResidX.set('-')
        self.clickedPredictX.set('-')
        self.clickedDependentX.set('-')
        return
    
    def showFit(self, *args):
        grp.showFit(res = gdata.modelres, xname = self.clickedDependentX.get(), colorvar = self.clickedGC.get(), dsize = float(self.gpen.get()) )
        cstr = f"grp.showFit(res = res, xname = '{self.clickedDependentX.get()}', colorvar = '{self.clickedGC.get()}', dsize = {float(self.gpen.get())} )"
        gdata.code_It(cstr)
        return
    
    def dopredict(self, *args):
        grp.dopredict(res = gdata.modelres, xname = self.clickedPredictX.get(), colorvar = self.clickedGC.get(), dsize = float(self.gpen.get()) )
        cstr = f"grp.dopredict(res = res, xname = '{self.clickedPredictX.get()}', colorvar = '{self.clickedGC.get()}', dsize = {float(self.gpen.get())} )"
        gdata.code_It(cstr)
        return
    
    def doresidual(self, *args):
        xvresid = self.clickedResidX.get()
        if xvresid == 'Predictions': 
            xnms = None
        else:
            xnms = xvresid
        grp.doresidual(gdata.modelres, mtype = gdata.model_type, xname = xnms, 
                    cvresid = self.clickedGC.get(), dsize = float(self.gpen.get()))
        cstr=f"grp.doresidual(res = res, mtype = '{gdata.model_type}', xname = '{xnms}', cvresid = '{self.clickedGC.get()}', dsize = {float(self.gpen.get())})"
        gdata.code_It(cstr) 
        return
     
    def doroc(self, *args):
        if (gdata.model_type not in  ['LOGIT', 'PROBIT']): 
            return
        if (gdata.fitdata is None):
            return
        gdata.code_It("grp.doroc(MODEL=res)")
        prediction_res = gdata.modelres.get_prediction(transform = True)
        res_frame= prediction_res.summary_frame(alpha = 0.05)

        #fpr, tpr, thresholds = roc_curve(gdata.fitdata[gdata.depvar], res_frame['mean']) 
        fpr, tpr, thresholds = roc_curve(gdata.modelres.model.endog, res_frame['mean']) 
        roc_auc = auc(fpr, tpr)
        fig = plt.figure(figsize = (8,8))
        ax = fig.add_subplot()
        ax.plot(fpr, tpr)
        ax.plot([0, 1], [0, 1], 'k--')
        ax.set_xlim([0.0, 1.0])
        ax.set_ylim([0.0, 1.05])
        ax.set_xlabel('False Positive Rate')
        ax.set_ylabel('True Positive Rate')
        ax.set_title(f"ROC  Model: {gdata.model_string}, \nAUC={round(roc_auc,5)}")
        fig.show()
        return
    
    def docorr(self, *args):
        if (gdata.fitdata is None):
            return
        corrvar0 = list(gdata.indvars)
        corrvar0.insert(0,gdata.depvar)
        sb.pairplot(gdata.fitdata[corrvar0])
        plt.show()
        return
    def doinfluence(self, *args):
        influence_plot(gdata.modelres) 
        plt.show()
        return
    def doleverage(self, *args):
        plot_leverage_resid2(gdata.modelres) 
        plt.show()
        return


    def modelplot(self):
        if (gdata.fitdata is None):
            messagebox.showerror(" ","You need to fit a model before you can plot a model. Not my rule, check with Dr. Knucklehead.")
            return
        if len(gdata.indvars) == 1:
            xv = list(gdata.indvars)[0]
            if not(is_numeric_dtype(gdata.fitdata[xv])):
                messagebox.showerror(" ",f"To display the model, all of the variables must be numerical. xv={xv}")
                return
            yv = '-'
            zv = gdata.depvar
        elif len(gdata.indvars) == 2:
            xv = list(gdata.indvars)[0]
            yv = list(gdata.indvars)[1]
            zv = gdata.depvar
            if not (is_numeric_dtype(gdata.fitdata[xv]) and is_numeric_dtype(gdata.fitdata[yv]) and is_numeric_dtype(gdata.fitdata[zv])):
                messagebox.showerror(" ",f"To display the model, all of the variables must be numerical. xv={xv}, yv={yv}, zv = {zv}")
                return
        else:
            messagebox.showerror(' ',"I can only graph models with one or two independent variables.")    
            return
        cv = self.clickedGC.get()
        bci = False
        bpi = False
        if self.selected_ci.get() == 1:
            bci = True
        if self.selected_pi.get() == 1:
            bpi = True
        dsize = float(self.gpen.get())
        grp.modelplot(gdata.modelres, depvar = zv, indvars = gdata.indvars, color_var = cv, 
                       showCI = bci, showPI = bpi, MTYPE = gdata.model_type, dsize = dsize)
        cstr = f"grp.modelplot(res, depvar = '{gdata.depvar}', indvars = {list(gdata.indvars)},color_var = '{self.clickedGC.get()}',"
        cstr += f" showCI = {bci}, showPI = {bpi}, MTYPE = '{gdata.model_type}', dsize = {dsize})"
        gdata.code_It(cstr)
        return


    def exit_closing(self):
        plt.close('all')
        gdata.modelData_Clear()
        self.destroy()
        
    def saveDes(self, *args):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[('Text Files', '*.txt'), ('All Files', '*.*'), ('CSV Files', '*.csv')],
            initialfile = f"DG_Fitted_{datetime.now().strftime('%Y-%m-%d@%H-%M-%S')}.csv"
        )
        if file_path.endswith(('.csv','.CSV')):
            gdata.fitdata.to_csv(file_path)
        elif file_path.endswith(('.dta','.DTA')):
            gdata.fitdata.to_stata(file_path)
        return
    
    
    def saveDmatOnly(self, *args):
        depv, dfrm = dmatrices(gdata.model_string, gdata.inputdata, return_type = 'dataframe', NA_action=NAAction(NA_types=[]))
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes = [('CSV Files','*.csv')],
            initialfile = f"DG_ModelInput_{datetime.now().strftime('%Y-%m-%d@%H-%M-%S')}.csv"
        )
        data = pd.concat([depv, dfrm], axis=1)
        if file_path.endswith(('.csv','.CSV')):
            data.to_csv(file_path)
        elif file_path.endswith(('.dta','.DTA')):
            data.to_stata(file_path)
        return


if __name__ == "__main__":

    class solo(tk.Tk):

        def __init__(self):
            super().__init__()
            self.title("Models Stand Alone App")
            self.geometry("700x50+0+0") 
            self.onButton = tk.Button(self, text = "Get Data", command = self.getData).pack(side = tk.LEFT, padx = 10)
            self.goPivot  = tk.Button(self, text = "Fit Model", command = self.goModel).pack(side = tk.LEFT, padx = 10)
            self.offButton = tk.Button(self, text="Graceful Exit", command = self.quit).pack(side = tk.LEFT, padx = 10)
            self.modelOn = False

            
            #gst = goPivot(self)
        
        def goModel(self,*args):
            if len(gdata.data) == 0:
                return
            if self.modelOn:
                self.gst.destroy()
            self.gst = RegressionApp()
            self.modelOn = True
            #self.gst.syncData()

                        
        def quit(self,*args):
            plt.close('all')
            gdata.modelData_Clear()
            self.destroy()
            self.modelOn = False
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
                if self.modelOn:
                    #self.dstat.syncData()
                    gdata.modelData_Clear()
                    self.gst.destroy()
                    plt.close('all')
                    self.gst = RegressionApp()

            return
            

    app = solo()
    app.mainloop()

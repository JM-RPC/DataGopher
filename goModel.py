# Refactored: Tkinter app as a class

from patsy import dmatrices, NAAction
from sklearn.metrics import roc_curve, auc
from datetime import datetime
#mport statsmodels.api  as sm
#import statsmodels.formula.api as smf
from statsmodels.graphics.regressionplots import plot_partregress_grid, plot_leverage_resid2, influence_plot, plot_fit

import pandas as pd
from pandas.api.types import is_numeric_dtype
#import DataRead as dr
import Regression as rg
from Regression import imdl  #provides model data shared between goModel.py and Regression.py only.
import Graphics as grp




import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

import numpy as np

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, # interface between Figure class and Tkinter's Canvas
    NavigationToolbar2Tk # built-in toolbar for the figure
    )

import seaborn as sb
#sb.set_style("darkgrid", {"grid.color": ".6", "grid.linestyle": ":"})

from mpl_toolkits.mplot3d import Axes3D

import sys

import globalData as gd
import goDataFilter as godf
import goPlot as gopt

from globalData import gdata

"""
Notes:
    
    imdl.fitdata is not None signals model is current, and fit succesfully -- whether appropriate to the data or not.
    imdl.fitdata is None signals model has been edited and not re-fitted, model fit failed, or any other event that might
        put model plotting out of sync with the intended model.   In particuar changeIndVar, changeDepVar and clearModel all 
        trigger imdl.fitdata being reset to None.  Anything that needs a fitted model consistent with the model displayed
        needs to have imdl.fitdata is not None.
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
    
def getcolor(cvar, col_data):
    #dfc = pd.DataFrame(col_data).astype('str')
    dfc = pd.DataFrame(col_data)
    #choicesCo = list(dfc[dfc.columns[0]].astype('str').unique())
    #choicesCo.sort()
    choicesCo = list(dfc[dfc.columns[0]].unique())
    choicesCo.sort()
    #choicesCo_str = [str(item) for item in choicesCo]
    if (len(choicesCo) < len(basecolors0)):
        colorD = {item : basecolors0[choicesCo.index(item)]  for item in choicesCo}
        colorlist = [colorD[item] for item in col_data]
        lpatches = [mpatches.Patch(color = colorD[item],label = cvar + ', ' + str(item)) for item in colorD.keys()]
    else:
        cmap = plt.cm.plasma
        #colorNos = [choicesCo.index(item) for item in col_data]
        colorD = {item : cmap(choicesCo.index(item)/len(choicesCo)) for item in choicesCo}
        colorlist = [colorD[item] for item in col_data]
        lpatches = [mpatches.Patch(color = colorD[item],label = cvar +  ', ' + str(item)) for item in choicesCo]
        #patch = mpatches.Patch(color = colorD[item], label = cv + ', ' + str(item))
    return colorD, colorlist, lpatches
 

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
        
# df = imdl.inputdata        
#mstk = mdlStack()
# modelvars = list(df.columns)
# modelvars.insert(0,'-')
# gphvars = modelvars
# mdl_res = None
# res = None
# rlog = None

mtypes = ['OLS', 'GAMMA', 'LOGIT', 'PROBIT', 'POISSON', 'NEGATIVE BINOMIAL']


# links = {'GAMMA':['Inverse', 'Log', 'Identity', 'InversePower'],
#          'POISSON':['Log', 'Identity', 'Sqrt'],
#          'NEGATIVE_BINOMIAL': ['Log', 'Identity', 'Power', 'cloglog', 'NegativeBinomial'],
#          'PROBIT': ['InverseNormal'],
#          'LOGIT': ['Logit'],
#          'OLS': ['Identity']
#          }
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

        imdl.inputdata = pd.DataFrame()
        imdl.model_vars = ['-']
        imdl.fname = 'None'
        imdl.model_string = '~'

        
        #model stack
        self.mstk = mdlStack()
        
        # Variables
        self.datafilename = tk.StringVar(self)
        self.datafilename.set(imdl.fname)
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
        self.nbparm_alpha = tk.StringVar(self, str(1.0))
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
        numeric_columns = [item for item in imdl.inputdata.columns if is_numeric_dtype(imdl.inputdata[item])]
        self.cy = ttk.Combobox(self.mf1, values=numeric_columns, textvariable=self.clickedY)
        self.cy.grid(row=RRow, column=1, sticky='w')
        self.cy.bind("<<ComboboxSelected>>", self.changeDepVar)
        tk.Label(self.mf1, text="Independent Variables:").grid(row=RRow, column=2, sticky='e')
        self.cx = ttk.Combobox(self.mf1, values=imdl.model_vars, textvariable=self.clickedX)
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
        
        self.over_dispParmLabel = tk.Label(self.mf2, text="(0.1-2.0)")
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

        # Frame 3
        self.mf3 = tk.Frame(self, borderwidth=1, relief="solid", highlightthickness=0, padx=10, pady=10)
        self.mf3.pack(fill='x', side=tk.TOP, padx=10, pady=5)
        RRow = 0
        msg = '                                                                       '
        msg1 = msg + msg + msg + msg
        tk.Label(self.mf3, text=msg1, fg="white").grid(row=RRow, column=0, columnspan=11, sticky='w', padx=10)
        tk.Label(self.mf3, text='Graphics: ', bg="blue", fg="white").grid(row=RRow, column=0, sticky='w', padx=10)
        tk.Label(self.mf3, text=" Mark Data with:").grid(row=RRow, column=1, sticky='w')
        self.gc = tk.OptionMenu(self.mf3, self.clickedGC, ['-'], command=self.makePlotc)
        self.gc.grid(row=RRow, column=2, sticky='w')
        tk.Label(self.mf3, text='Pen Size:').grid(row=RRow, column=3, sticky='w')
        self.gpen = tk.Scale(self.mf3, from_=0.25, to=100, orient='horizontal', showvalue=True)
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
        tk.Checkbutton(self.grp2d, text="Resp.", variable=self.selected_response, onvalue=1, offvalue=0, height=3, width=5).grid(row=1, column=1, padx=5)
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

        # Toplevel windows
        self.repwin = tk.Toplevel(self)
        self.repwin.title("Report Viewer \n(most recent at top)")
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
        imdl.link = self.clickedLink.get()
        return
    
    def model_choice(self, *args):
        mdl = self.selected_model.get()
        #print(f"Model chosen: {mdl}")
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
            imdl.inputdata = gdata.data.copy(deep = True)
            imdl.fname = gdata.fpath
            imdl.model_vars = ['-'] + list(imdl.inputdata.columns)
            imdl.fitdata = None
            imdl.model_string = '~'
            self.cy['values'] = imdl.model_vars
            self.cx['values'] = imdl.model_vars
            self.datafilename.set(filename)
            self.text_area.delete("1.0",tk.END)
            self.clearModel()
            plt.close('all')
        else:
            return
        return
    
    # def updateData(self, *args):
    #     gdata.data = pd.DataFrame()
    #     gdata.fpath = ''
    #     self.getData()
    #     return
    
    def saveModel(self, *args):
        self.mstk.model_string_stack.append(self.meqn.get())
        self.mstk.ivar_stack.append(imdl.indvars)
        self.mstk.dvar_stack.append(imdl.depvar)
        return
    
    def pullModel(self, *args):
        if len(self.mstk.model_string_stack) == 0 : return
        if self.mstk.stack_level <= -len(self.mstk.model_string_stack):
            self.mstk.stack_level = -1 #we're at the end reset the stack level
        else:
            self.mstk.stack_level -= 1 #decrement stack level
        mstring = self.mstk.model_string_stack[self.mstk.stack_level]
        self.meqn.set(mstring)
        imdl.model_string = mstring
        imdl.indvars = self.mstk.ivar_stack[self.mstk.stack_level]
        imdl.depvar = self.mstk.dvar_stack[self.mstk.stack_level]
        return
    
    def changeIndepVar(self, *args):
        xstr = str(self.clickedX.get())
        if xstr == "-":
            return
        elif imdl.depvar == xstr:
            messagebox.showerror(' ', f"The variable {xstr} is also the dependent variable.  \n This model is self-explanatory. \nYou're making this too easy!")
            return
        else:
            if xstr not in imdl.indvars:
                if len(imdl.indvars) == 0:
                    imdl.model_string += xstr
                else:
                    imdl.model_string += '+' + xstr
                imdl.indvars.add(xstr)
        self.meqn.set(imdl.model_string)
        c0 = set()
        current_varset = c0.union(imdl.indvars, set([imdl.depvar]))
        remaining_varlist = ['-'] + [item for item in list(imdl.inputdata.columns) if item not in current_varset]
        self.cx['values'] = remaining_varlist
        
        #complexity: dependent variable must be a number
        numeric_columns = [item for item in imdl.inputdata.columns if is_numeric_dtype(imdl.inputdata[item])]
        remaining_varlist = ['-'] + [item for item in numeric_columns if item not in current_varset]
        self.cy['values'] = remaining_varlist
         
        imdl.fitdata = None
        return
    
    def changeDepVar(self, *args):
        ystr = str(self.clickedY.get())
        if ystr == imdl.depvar:
            return
        elif ystr == "-":
            return
        else:
            imdl.depvar = ystr
            if len(imdl.model_string.split("~")) < 2:
                imdl.model_string = ystr + '~'
            else:
                imdl.model_string = ystr + '~' + imdl.model_string.split("~")[1]
            
        self.meqn.set(imdl.model_string)
        c0 = set([''])
        current_varset = c0.union(imdl.indvars, set([imdl.depvar]))
        remaining_varlist = ['-'] + [item for item in imdl.inputdata.columns if item not in current_varset]
        self.cx['values'] = remaining_varlist
        
        #complexity: dependent variable must be a number
        numeric_columns = [item for item in imdl.inputdata.columns if is_numeric_dtype(imdl.inputdata[item])]
        remaining_varlist = ['-'] + [item for item in numeric_columns if item not in current_varset]
        self.cy['values'] = remaining_varlist
        
        imdl.fitdata = None
        return
    
    def clearModel(self):
        imdl.depvar = ""
        imdl.indvars = set([])
        imdl.model_string = '~'
        self.meqn.set(imdl.model_string)
        self.clickedY.set(imdl.model_vars[0])
        self.clickedX.set(imdl.model_vars[0])
        imdl.fitdata = None
        if (self.buttonSaveDes.winfo_ismapped()): self.buttonSaveDes.grid_forget()
        self.cx['values'] = list(imdl.inputdata.columns)
        numeric_columns = [item for item in imdl.inputdata.columns if is_numeric_dtype(imdl.inputdata[item])]
        self.cy['values'] = list(numeric_columns)
        return
    
    def runModel(self, *args):
        imdl.model_type = str(self.selected_model.get())
        imdl.link = str(self.link.get())
        imdl.sig_level = 0.05
        temp = self.siglev.get()

        try:
            imdl.sig_level = float(temp)
        except:
            messagebox.showwarning("nh", f"Significance level must be a number between 0 and 1. \n you entered :{temp}\n Defaulting to 0.05")
            imdl.siglev = 0.05
        if imdl.sig_level <= 0 or imdl.sig_level >= 1:
            messagebox.showwarning("nh", f"Significance level must be a number between 0 and 1. \n you entered :{temp}\n Defaulting to 0.05")
            imdl.sig_level = 0.05
        imdl.model_string = str(self.meqn.get())
        mdlist = imdl.model_string.split("~")
        if len(mdlist) < 2: 
            messagebox.showwarning("nh", f"Incomplete Model specification: {imdl.model_string}. You need a dependent and one or more independent variables. \nTry again!")
            return
        if imdl.model_type == 'NEGATIVE BINOMIAL':
            temp = float(self.nbparm_alpha.get())
            if temp < 0: temp = 0
            if temp > 2.0: temp = 2.0
            imdl.overdispersionparm = temp
        imdl.fitdata = None
####################################################################
########### Run the model
        gdata.log_It("\n:Model:\n")
        gdata.log_It(f"Fitting the model: {imdl.model_string} type = {imdl.model_type}")
        rtemp = rg.goModel()
####################################################################
        mdl_res, res, rlog = rtemp #retrieve fitting data, results and log file
        #gdata.log_It(rlog)#transfer the model log to the global log
        #imdl.clearlog() #clear the model log
        #self.log_area.insert(tk.END, gdata.logstr) 
        if mdl_res is not None:           
####################################################################
####################################################################
########### Stash model data and results in the global data structure
            gdata.model_res = res
            gdata.model_data = mdl_res.copy(deep = True)
####################################################################
####################################################################

            if imdl.model_type in ['OLS']:
                strbuf = "==============================================================================="
                strdisclaimer = "Partition of sums of squares for OLS only valid when your model fits an intercept.  Check the report."
                strss = f"SSE = {res.ssr} \nSSR = {res.centered_tss - res.ssr} \nSST = {res.centered_tss} \n"
                se_str = f"Std. Err. of Regression: {np.sqrt(res.mse_resid)} \n" + strbuf +"\n"
                anova_str = strbuf + "\n" + se_str + "\n" + strbuf +"\n" + strss + "\n" +strbuf + "\n" + strdisclaimer + "\n" +strbuf
            else:
                anova_str = ''
            self.text_area.insert('1.0', '\n'+str(res.summary(alpha = imdl.sig_level)) + '\n' + anova_str)
            #self.log_area.insert(tk.END, rlog)
            gphv = list(mdl_res.columns)
            #gphvars = [item for item in gphv if len(mdl_res[item].unique()) <= len(basecolors0)]
            gphvars = gphv
            gphvars.insert(0, "-")
            nuvars = list(mdl_res.columns)
            mdlvars = list(res.params.index)
            #print(f"mdlvars: {', '.join(mdlvars)} \n nuvars: {', '.join(nuvars)}")
            imdl.modelres = res
            imdl.fitdata = mdl_res.copy(deep = True)

            #gdata.put_Data(mdl_res.copy(deep = True))
            
            #adjust the grahics choices based on the model type    
            self.update_option_menu_colors(gphvars)
            self.update_option_menu_vars(mdlvars + ['Predictions'])
            if (not self.buttonSaveDes.winfo_ismapped()): self.buttonSaveDes.grid(row = 2, column = 10)
            self.mf3.pack()
            if imdl.model_type in ['LOGIT','PROBIT']:
                self.rocbutton.grid(row = 1, column=0)
            else:
                self.rocbutton.grid_forget()
            if imdl.model_type in ['OLS']:
                self.influencebutton.grid(row = 2, column = 2)
                self.pint.grid(row=1, column=3, padx=10)
            else:
                self.influencebutton.grid_forget()
                self.pint.grid_forget()
            if (len(imdl.indvars)<=2):
                if not (self.grp2d.winfo_ismapped()): self.grp2d.pack()
            if (len(imdl.indvars)>2):
                if (self.grp2d.winfo_ismapped()): self.grp2d.pack_forget()
        else:
            emsg = "Model Fit Failed.  Check the log file,"
            emsg += "\nmodel formula, model type, data."
            emsg += "\nVariable names may contain only letters,numbers and underscores and no leading numbers. "
            emsg += "\nRename non-conforming variable names or enclose in Q(\"..\") "
            emsg += "\nOtherwise, check with Dr. Knucklehead."
            messagebox.showerror(" ",emsg)
            imdl.fitdata = None
            if (self.buttonSaveDes.winfo_ismapped()): self.buttonSaveDes.grid_forget()
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
        xvdependent = self.clickedDependentX.get()
        if (xvdependent == '') or (xvdependent == '-'): return       

        cvdependent = self.clickedGC.get()
        dsize = float(self.gpen.get())/20.0
        fig, ax = plt.subplots()
        plot_fit(imdl.modelres, xvdependent, vlines = False, ax = ax, markersize=dsize)
        for line in ax.lines:
            if line.get_linestyle() == 'None' and line.get_marker() != 'None': # Identify scatter plot
                line.set_markersize(dsize) # Set desired marker size

        #plt.ylabel(ylabstr)
        plt.show()
        return
    
    def dopredict(self, *args):
        xvpredict = self.clickedPredictX.get()
        if (xvpredict == '') or (xvpredict == '-'): return
        cvpredict = self.clickedGC.get()
        dsize = float(self.gpen.get())
        prediction_res = imdl.modelres.get_prediction(transform = True)
        res_frame= prediction_res.summary_frame(alpha = 0.05)
        ylabstr = "Est. Mean Response"
        #plt.clf()
        fig, ax = plt.subplots()
        if (cvpredict != '') and (cvpredict != '-'): 
            sb.scatterplot(imdl.fitdata, ax= ax, x = xvpredict, y = res_frame['mean'], hue = cvpredict, palette = 'bright',s = dsize )
        else:
            sb.scatterplot(imdl.fitdata, ax = ax, x = xvpredict, y = res_frame['mean'], color = 'blue', s = dsize)
        if imdl.model_type in ['LOGIT', 'PROBIT']:
            plt.axhline(y=0, color='black', linestyle='-')
            plt.axhline(y=0.2, color = 'black', linestyle = 'dashed',linewidth = 0.5)
            plt.axhline(y=0.4, color = 'black', linestyle = 'dashed',linewidth = 0.5)
            plt.axhline(y=0.5, color = 'black', linestyle = 'dotted',linewidth = 0.5)
            plt.axhline(y=0.6, color = 'black', linestyle = 'dashed',linewidth = 0.5)
            plt.axhline(y=0.8, color = 'black', linestyle = 'dashed',linewidth = 0.5)
            plt.axhline(y=1.0, color = 'black', linestyle = '-',linewidth = 0.5)
            plt.ylim((0, 1))
        plt.ylabel(ylabstr)
        plt.show()
        return
    
    def doresidual(self, *args):
        xvresid = self.clickedResidX.get()
        if (xvresid == '') or (xvresid == '-'): return
        #residlim = max(np.abs(imdl.fitdata['Residuals']))
        cvresid = self.clickedGC.get()
        dsize = float(self.gpen.get())
        if imdl.model_type != 'OLS': #if it's not OLS it's GLM
            vres = imdl.modelres.resid_deviance
            ylabstr = 'Deviance Residual'
        else:
            vres = imdl.modelres.resid
            ylabstr = 'Residual'
        residlim = max(np.abs(vres))
        fig, ax = plt.subplots()
        #plt.clf()
        if (cvresid != '') and (cvresid != '-'): 
            sb.scatterplot(imdl.fitdata, x = xvresid, y = vres, hue = cvresid, palette = 'bright',s = dsize )
        else:
            sb.scatterplot(imdl.fitdata, x = xvresid, y = vres, color = 'blue', s = dsize)   
        plt.axhline(y=0, color='black', linestyle='-')
        plt.ylim((-residlim, residlim))
        plt.ylabel(ylabstr)
        plt.show()
        return
    
    def doModelPlot(self, *args):
        self.doresidual()
        self.dopredict()
        self.showFit()
    
    def doroc(self, *args):
        if (imdl.model_type not in  ['LOGIT', 'PROBIT']): 
            return
        if (imdl.fitdata is None): return
        
        prediction_res = imdl.modelres.get_prediction(transform = True)
        res_frame= prediction_res.summary_frame(alpha = 0.05)

        fpr, tpr, thresholds = roc_curve(imdl.fitdata[imdl.depvar], res_frame['mean']) 
        roc_auc = auc(fpr, tpr)
        fig = plt.figure(figsize = (8,8))
        ax = fig.add_subplot()
        ax.plot(fpr, tpr)
        ax.plot([0, 1], [0, 1], 'k--')
        ax.set_xlim([0.0, 1.0])
        ax.set_ylim([0.0, 1.05])
        ax.set_xlabel('False Positive Rate')
        ax.set_ylabel('True Positive Rate')
        ax.set_title(f"ROC  Model: {imdl.model_string}, \nAUC={round(roc_auc,5)}")
        fig.show()
        return
    
    def docorr(self, *args):
        if (imdl.fitdata is None): return
        corrvar0 = list(imdl.indvars)
        corrvar0.insert(0,imdl.depvar)
        sb.pairplot(imdl.fitdata[corrvar0])
        plt.show()
        return
    def doinfluence(self, *args):
        influence_plot(imdl.modelres) 
        plt.show()
        return
    def doleverage(self, *args):
        plot_leverage_resid2(imdl.modelres) 
        plt.show()
        return
    def modelplot(self):
        if (imdl.fitdata is None):
            messagebox.showerror(" ","You need to fit a model before you can plot a model. Not my rule, check with Dr. Knucklehead.")
            return
        if len(imdl.indvars) == 1:
            xv = list(imdl.indvars)[0]
            if not(is_numeric_dtype(imdl.fitdata[xv])):
                messagebox.showerror(" ",f"To display the model, all of the variables must be numerical. xv={xv}")
                return
            yv = '-'
            zv = imdl.depvar
        elif len(imdl.indvars) == 2:
            xv = list(imdl.indvars)[0]
            yv = list(imdl.indvars)[1]
            zv = imdl.depvar
            if not(is_numeric_dtype(imdl.fitdata[xv]) & is_numeric_dtype(imdl.fitdata[yv]) & is_numeric_dtype(imdl.fitdata[zv])):
                messagebox.showerror(" ",f"To display the model, all of the variables must be numerical. xv={xv}, yv={yv}, zv = {zv}")
                return
        else:
            messagebox.showerror(' ',"I can only graph models with one or two independent variables.  For larger models you'll have to make do with residual plots.")    
            return
        xvar, yvar, znew, Ci_lb1, Ci_ub1, Pi_lb1, Pi_ub1 = grp.doTrend()
        dsize = float(self.gpen.get())
        if len(imdl.indvars)==1:
            fig = plt.figure(figsize = (8,8)) 
            ax = fig.add_subplot()
            xv = list(imdl.indvars)[0]
            zv = imdl.depvar
            cv = self.clickedGC.get()
            if cv == '-':
                sb.scatterplot(imdl.fitdata, x = xv, y = zv, ax = ax,s = dsize, color = 'black')
            else:
                sb.scatterplot(imdl.fitdata, x = xv, y= zv, ax = ax, s = dsize, hue = cv, palette = 'bright' )
            dftemp = pd.DataFrame({xv:xvar, zv:znew})
            if (self.selected_response.get() == 1):
                sb.lineplot(dftemp, x = xv, y = zv, ax = ax, color = 'red', linewidth = dsize/2)
            if (self.selected_ci.get() == 1):
                sb.lineplot(dftemp, x = xv, y = Ci_lb1, ax = ax, color = 'green', linewidth = dsize/2)
                sb.lineplot(dftemp, x = xv, y = Ci_ub1, ax = ax, color = 'green', linewidth = dsize/2)
            if (imdl.model_type == 'OLS') & (self.selected_pi.get() == 1):
                sb.lineplot(dftemp, x = xv, y = Pi_lb1, ax = ax, color = 'blue', linewidth = dsize/2)
                sb.lineplot(dftemp, x = xv, y = Pi_ub1, ax = ax, color = 'blue', linewidth = dsize/2)
            fig.show()
        elif len(imdl.indvars) == 2:
            fig = plt.figure(figsize = (8,8))
            ax = fig.add_subplot(111, projection='3d')
            xv = list(imdl.indvars)[0]
            yv = list(imdl.indvars)[1]
            zv = imdl.depvar
            cv = self.clickedGC.get()
            xdat = imdl.fitdata[xv]
            ydat = imdl.fitdata[yv]
            zdat = imdl.fitdata[zv]
            ax.set_xlabel(xv)
            ax.set_ylabel(yv)
            ax.set_zlabel(zv)
            if (cv == '-') or (cv == ''):
                ax.scatter(xdat, ydat, zdat ,marker='o', color = 'black', s = dsize)
            else:
                colordat = imdl.fitdata[cv]
                colorD, colorlist ,lpatches= getcolor(cv,list(colordat))
                #colorvar,colorD = grp.getcolorM(colordat)
                ax.scatter(xdat, ydat, zdat ,marker='o', c = colorlist, s = dsize)
                if colorD != {}:
                    handles , labels = ax.get_legend_handles_labels()
                    handles.extend(lpatches)
                    ax.legend(handles = handles)
                    #for item in colorD.keys():
                        #patch = mpatches.Patch(color = colorD[item], label = cv + ', ' + str(item))
                        #handles.extend([patch])
                        #ax.legend(handles = handles)                    
            if (self.selected_response.get() == 1):
                ax.plot_surface(xvar,yvar,znew, alpha = 0.8, color = 'cyan', edgecolor = 'grey')
            if (self.selected_ci.get() == 1):
                ax.plot_surface(xvar,yvar,Ci_ub1, alpha = 0.4, color ='goldenrod', edgecolor = 'grey')
                ax.plot_surface(xvar,yvar,Ci_lb1, alpha = 0.4, color ='goldenrod', edgecolor = 'grey')            
            if (imdl.model_type == 'OLS') & (self.selected_pi.get() == 1):
                ax.plot_surface(xvar,yvar,Pi_ub1, alpha = 0.2, color = 'magenta', edgecolor = 'grey')                
                ax.plot_surface(xvar,yvar,Pi_lb1, alpha = 0.2, color = 'magenta', edgecolor = 'grey')                
            fig.show()
        else:
            return
        return
    def exit_closing(self):
        plt.close('all')
        imdl.modelData_Clear()
        self.destroy()
        
    def saveDes(self, *args):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[('Text Files', '*.txt'), ('All Files', '*.*'), ('CSV Files', '*.csv')],
            initialfile = f"gS_Fitted_{str(datetime.now()).replace(' ','_')}.csv"
        )
        if file_path.endswith(('.csv','.CSV')):
            imdl.fitdata.to_csv(file_path)
        elif file_path.endswith(('.dta','.DTA')):
            imdl.fitdata.to_stata(file_path)
        return
    
    
    def saveDmatOnly(self, *args):
        depv, dfrm = dmatrices(imdl.model_string, imdl.inputdata, return_type = 'dataframe', NA_action=NAAction(NA_types=[]))
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes = [('CSV Files','*.csv')],
            initialfile = f"gS_Input_{str(datetime.now()).replace(' ','_')}.csv"
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
            if len(gdata.data) == 0: return
            if self.modelOn:
                self.gst.destroy()
            self.gst = RegressionApp()
            self.modelOn = True
            #self.gst.syncData()

                        
        def quit(self,*args):
            plt.close('all')
            imdl.modelData_Clear()
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
                    imdl.modelData_Clear()
                    self.gst.destroy()
                    plt.close('all')
                    self.gst = RegressionApp()

            return
            

    app = solo()
    app.mainloop()

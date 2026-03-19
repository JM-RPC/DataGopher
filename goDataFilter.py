#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 27 21:49:03 2025

@author: John
"""

from patsy import dmatrices, dmatrix, NAAction
import tkinter as tk
from tkinter import  messagebox
#from tkinter import scrolledtext
from tkinter import filedialog, ttk

import pandas as pd
import numpy as np
#from numpy.random import default_rng
from datetime import datetime
from pandas.api.types import is_numeric_dtype
import globalData as gd
from globalData import gdata

#import TableDisplayb as ptd
#import TableDisplaya as ptd
import TableDisplayc as ptc

import Listwidget as lw


def doDesign(MODEL_STRING = '', DATA = None, APPEND = True):
    if (MODEL_STRING == '') or (DATA is None):
        return
    else:
        MODEL_STRING += '- 1' #kill the intercept term in the resulting design matrix
    try:
        nudf = dmatrix(MODEL_STRING, data = DATA, return_type = 'dataframe', NA_action=NAAction(NA_types=[]))
        gdata.log_It(f"nudf = dmatrix({MODEL_STRING}, data=dataframe, return_type = /'dataframe/', NA_action = NAAction(NA_types=[])")
    except Exception as er:
        emsg = f"Variable transformation failed error{er}"
        emsg += "\nCheck the log file,"
        emsg += "\nmodel formula, model type, data."
        emsg += "\nVariable names may contain only letters,numbers and underscores and no leading numbers. "
        emsg += "\nRename non-conforming variable names or enclose in Q(\"variable name\") "
        emsg += "\nOtherwise, check with Dr. Knucklehead."
        messagebox.showerror(" ",emsg)
        return None
    infcount = sum(nudf[nudf.columns[0]].isin([-np.inf,+np.inf]))
    if infcount > 0:
        emsg = f"Variable transformation produced {infcount} infinite values.\n Convert to NA? (Yes = continue, No = start over)"
        ynbool = messagebox.askyesno(" ",emsg)
        if ynbool:
            nudf.replace([np.inf, -np.inf], np.nan, inplace=True)
        else:
            return None
    if APPEND:     #merge the new design matrix with the original data
        originalcols = list(DATA.columns)
        newcols = list(nudf.columns)
        addcols = [item for item in newcols if item not in originalcols]
        dfout = pd.concat([DATA, nudf[addcols]], axis = 1)
    else:
        dfout = nudf
    return dfout



    
class goData(tk.Toplevel):
#class goData(tk.Tk):
    def __init__(self,parent):
        super().__init__(master=parent)
    #def __init__(self,parent):
        #super().__init__(master=parent)
        
        

        self.title("Data Wrangler Prototype") 
        self.geometry('1080x680+0+0')
        self.filepath = ''
        self.outdata = pd.DataFrame()
################This is the global copy of the data##############
        # if not gdata.data.empty:
        #     self.data = gdata.data.copy(deep = True)
        #     #self.data0 = gdata.data.copy(deep = True)   
        #     self.filepath = gdata.fpath
        # else:   
        #     #self.data0 = pd.DataFrame() #spare copy of the original data
        #     self.data = pd.DataFrame() #the current data
##################################################################
       
        self.data = pd.DataFrame() #the current data

        self.filelabel = tk.Label(self,text = self.filepath)
        self.filelabel.grid(row = 0, column = 0, rowspan = 6,  sticky ='n', padx = 10)

        self.save_button = tk.Button(self,text="Save Data", command = self.saveData)
        self.save_button.grid(row = 0, column = 3, sticky = 'w')
        
        #self.filter_button = tk.Button(self, text="Revert Data", command = self.revertData)
        #self.filter_button.grid(row = 0, column = 4)
        self.protocol("WM_DELETE_WINDOW", self.exit_closing)

      
        bdry = '                                                                                                     '
        self.bdryrow = tk.Label(self, text = bdry).grid(row = 1, column = 0, columnspan = 5)
        self.bdryrow = tk.Label(self, text = bdry).grid(row = 6, column = 0, columnspan = 5)
        self.bdryrow = tk.Label(self,text = bdry).grid(row = 11, column = 0, columnspan = 5)

        self.pframe = ttk.Frame(self)
        self.pframe.grid(row=12, column = 0, columnspan = 5)
        self.dfrm = ptc.DataFrameTreeView(self.pframe)
        self.dfrm.pack(side = tk.TOP, pady=20, padx=20, fill = tk.BOTH, expand = True)
        
        # Configure grid weights to allow expansion
        self.rowconfigure(12, weight=1)
        for i in range(5):
            self.columnconfigure(i, weight=1)
        
        self.transformer_ind = False
        self.renameit_ind = False
        self.filterer_ind = False
        self.reFormer_ind = False
        
        self.syncData()
        
        return
        

    def doQuit(self):
        self.destroy()
        return 
    
    def exit_closing(self):
        #plt.close('all')
        self.destroy()  # This closes the Tkinter window    

    
    def newData(self, *args):
        gdata.data = pd.DataFrame()
        self.getData()
        return

    def revertData(self, *args):
        pass
        #not currently used. It's less confusing to simply read the data in again if you get stuck
        #restore from disk
        #if len(self.data0) == 0: return
        #self.data = self.data0.copy(deep = True)
        #self.dfrm.do_display(self.data)
        
    def saveData(self, *args):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[('Text Files', '*.txt'), ('All Files', '*.*'), ('CSV Files', '*.csv')],
            #initialfile = f"goData_{str(datetime.now()).replace(' ','_')}.csv"
            initialfile = f"DG_Data_{datetime.now().strftime("%Y-%m-%d@%H*%M*%S")}.csv"
        )
        #if (file_path == ''): return
        gdata.log_It(f"data.to_csv({file_path}, index=False)")
        #self.data.to_csv(file_path, index=False)
        self.data.to_csv(file_path, index=False)
        
        #force a reset to synchronize on the newly saved data
        gdata.reset_Data(nupath=file_path, data_in=self.data)
        gdata.log_It(f"Data Synchronized to saved file: {file_path})")
        self.filelabel.config(text = gdata.fpath + f"   #Rows = {len(gdata.data)} #Columns = {len(gdata.data.columns)}")
        if len(gdata.data) <= 5000000:
            numna = len(gdata.data) - len(gdata.data.dropna())            
            gdata.log_It(f"New Data File: {file_path}, Rows= {len(gdata.data)}, Columns={len(gdata.data.columns)}, {numna} rows have missing data. \n")
        else:
            gdata.log_It(f"New Data File: {file_path}, Rows= {len(gdata.data)}, Columns={len(gdata.data.columns)}, {numna} rows have missing data. \n")        
        return
    
    #broadcast data triggers the classes dstat (goModel.py), dpivot (gopivotb.py), ddraw (goplot.py) to resync with gdata.data
    #this broadcasts any changes to the data from filtering, renaming, reforming or creating new variables to everybody else.
    def broadcastData(self, *args):
        if self.master.regOn:
            self.master.dstat.syncData()
        if self.master.pivotOn:
            self.master.dpivot.syncData()
        if self.master.plotOn:
            self.master.ddraw.syncData()
        
    def syncData(self,*args):
        #syncrhonize everything inside goData to the data file contained in 
        #gdata.data -- if it is not empty.
        #restart transformer, renamer, and filterer
        #print(f"data filter: syncData called file:{gdata.fpath}, rows = {len(gdata.data)} ")
        
        #if gdata.data is empty, then stand down otherwise copy it into a local (goDataFilter only)
        #data frame
        if not gdata.data.empty:
            self.data =  gdata.data
            #self.data0 = gdata.data
            file_path = gdata.fpath
        else:
            return
        #gdata is live, self.data has been synced, 
        #now restart instances of dataTransformer, dataRename, dataFilter, reFormData  as needed
        if self.transformer_ind:
            self.transformer.destroy()
            self.transformer_ind = False
        self.transformer = dataTransform(self)
        self.transformer_ind = True
        self.transformer.grid(row = 2, column = 0, columnspan = 5, sticky = 'w')
        
        if self.renameit_ind:
            self.renameit.destroy()
            self.renameit_ind = False
        self.renameit = dataRename(self)
        self.renameit.grid(row = 4, column = 0, columnspan = 5,sticky = 'w')
        self.renameit_ind = True
            
        if self.filterer_ind:
            self.filterer.destroy()
            self.filterer_ind = False
        self.filterer = dataFilter(self)
        self.filterer.grid(row = 6, column = 0, columnspan = 5, sticky = 'w')
        self.filterer_ind = True
        
        if self.reFormer_ind:
            self.reFormer.destroy()
            self.reFormer_ind = False
        self.reFormer = reFormData(self)
        self.reFormer.grid(row = 8, column = 0, columnspan = 5, sticky = 'w')
        self.reFormer_ind = True

        self.dfrm.do_display(self.data)
            
        self.filelabel.config(text = gdata.fpath + f"   #Rows = {len(gdata.data)} #Columns = {len(gdata.data.columns)}")
        
        self.transformer.options['values'] = list(self.data.columns)
        self.filterer.options['values'] = list(self.data.columns)
        self.renameit.options['values'] = list(self.data.columns)
        self.reFormer.row_widget.resetList(NUCHOICES=list(self.data.columns))
        self.reFormer.col_widget.resetList(NUCHOICES=list(self.data.columns))
        self.master.varlist0 = list(self.data.columns)

        return
        
    def goRename(self):
        self.renameit = dataRename(self)
        self.renameit.grid(row = 5, column = 0, columnspan = 5)
 
class reFormData(tk.Frame):
    def __init__(self,parent):
        super().__init__(master = parent)
        self.configure(borderwidth=2, relief="ridge", highlightthickness=2)
        #self.title('ReForm Data')

        if len(gdata.data) > 0:
            colnames = list(gdata.data.columns)
            numcolnames = [item for item in colnames if is_numeric_dtype(gdata.data[item])]
        else:
            colnames = []
            numcolnames = []
            return

        self.rowlist = []
        self.collist = []
        self.vallist = []
        self.ptable = None
        
        #self.f1 = ttk.Frame(self)
        
        #rows
        self.fw = ttk.Frame(self)
        
        self.reFormlabel = tk.Label(self.fw,text = "Re-Shape Data:", fg = 'white', bg = 'blue')
        self.reFormlabel.grid(row  = 0, column = 0, sticky = 'w')
        
        self.syncButton = tk.Button(self.fw, text = "Do Re-Shape", command = self.doreForm).grid(row=0, column=1, sticky= 'w',pady = 10, padx = 10)
        

        self.row_widget = lw.goList(self.fw,TEXT = "ID Variables:", CHOICES = colnames)
        self.row_widget.grid(row = 1, column = 0, columnspan = 3,sticky = 'w')
        self.col_widget = lw.goList(self.fw,TEXT = "Value Variables:", CHOICES = colnames)
        self.col_widget.grid(row = 1, column = 4,columnspan = 3,sticky= 'w')

        self.fw.pack(side =tk.TOP)   
        #self.f1.pack()
        
    def saveData(self,*args):
        pass
    
    def doreForm(self,*args):
        ########################################
        ##  Get the data frame
        self.data = self.master.data
        ########################################
        dfnew = pd.DataFrame()
        idv = self.row_widget.rowlist
        valv = self.col_widget.rowlist
        if bool(set(idv) & set(valv)):
            messagebox.showerror("  ", "Error: ID and Value Choices must be disjoint.")
            return
        gdata.log_It(f"Attempting data reshape: ")
        gdata.log_It(f"dfnew = pandas.melt(data, id_vars = {idv}, value_vars = {valv})")
        try:
            dfnew = pd.melt(self.data, id_vars = idv, value_vars = valv)
        except Exception as er:
            emsg = f"Variable transformation failed error{er}\n "
            emsg += "Make sure that the ID variables don't have too many outcomes."
            emsg += "Make sure that the Value variables are numeric"
            messagebox.showerror("  ",emsg)
            return
            
        ########################################################## 
        ###  Display the results           
        #self.master.dfrm.do_display(self.master.data)  
        self.master.dfrm.do_display(dfnew)
        #self.master.filelabel.config(text = gdata.fpath + f"   #Rows = {len(gdata.data)} #Columns = {len(gdata.data.columns)}")
        self.master.filelabel.config(text = gdata.fpath + f"   #Rows = {len(dfnew)} #Columns = {len(dfnew.columns)}")
        
        ###########################################################
        ##### Update global data structures
        gdata.log_It(f"...Success!  number of rows: {len(dfnew)} number of columns: {len(dfnew.columns)}")
        self.data = dfnew.copy(deep = True)
        self.master.data = dfnew.copy(deep = True) #move transformed data back to parent
        gdata.put_Data(self.master.data) #update global copy of the data
        self.master.syncData()
        
        # self.master.transformer.options['values'] = list(self.data.columns)
        # self.master.filterer.options['values'] = list(self.data.columns)
        # self.master.renameit.options['values'] = list(self.data.columns)
        #self.row_widget.resetList(NUCHOICES=list(self.data.columns))
        #self.col_widget.resetList(NUCHOICES=list(self.data.columns))
        # self.master.varlist0 = list(self.data.columns)
        self.master.broadcastData(self)





class dataRename(tk.Frame):
    def __init__(self,parent):
        super().__init__(master = parent)
        #self.reButton = tk.Button(self, text = 'Rename a Variable', command= self.setupRename)
        #self.reButton.grid(row =0, column=0)
        #self.setupRename()
        self.configure(borderwidth=2, relief="ridge", highlightthickness=2)
        self.renamelabel = tk.Label(self,text = "Rename Variables:", fg = 'white', bg = 'blue')
        self.renamelabel.grid(row  = 0, column = 0, columnspan =5)
        varlist0 = list(self.master.data.columns)
        self.selected_variable  = tk.StringVar()
        self.vname = tk.StringVar()
        self.Label0 = tk.Label(self,text = "Rename Variables:", fg = 'white', bg = 'blue')
        self.Label0.grid(row = 0, column = 0)
        
        self.Label1 = tk.Label(self, text='Select variable:').grid(row = 0, column = 1, sticky ='e')
        self.options = ttk.Combobox(self, values=varlist0,textvariable = self.selected_variable)
        self.options.grid(row = 0, column = 2)
        
        self.Label2 = tk.Label(self, text = 'New name:').grid(row =0, column = 3)
        self.options.bind("<<ComboboxSelected>>", self.nameupdate)
        
        self.nuname = tk.Entry(self,textvariable = self.vname, width = 20)
        self.nuname.grid(row = 0, column = 4)
        
        self.nbutton = tk.Button(self,text = 'Change Name', command = self.goChange)
        self.nbutton.grid(row = 0, column=5)
        
    def nameupdate(self, *args):
        self.vname.set(self.selected_variable.get())
        
    def goChange(self, *args):
        if self.vname.get() in list(self.master.data.columns):
            messagebox.showerror("  ", "Sorry, that name is aready in use.  Try again.")
            return
        ##############Change the required master data and options in transformer  and filterer
        gdata.log_It(f"data.rename(columns= {self.selected_variable.get()}: {self.vname.get()}, inplace = True)")
        self.master.data.rename(columns = {self.selected_variable.get():self.vname.get()}, inplace = True)
        
        gdata.put_Data(self.master.data)
        #self.master.data = self.data.copy(deep = True) #move transformed data back to parent
        self.master.broadcastData(self)
        gdata.log_It(f"Changed variable name from: {self.selected_variable.get()} to:{self.vname.get()}")

        #change the list options in the filter, transform, rename, and reform widgets   
        self.master.transformer.options['values'] = list(self.master.data.columns)
        self.master.filterer.options['values'] = list(self.master.data.columns)
        self.options['values'] = list(self.master.data.columns)
        self.selected_variable.set('')
        self.master.dfrm.do_display(self.master.data)    
        self.master.reFormer.row_widget.resetList(NUCHOICES=list(self.master.data.columns))
        self.master.reFormer.col_widget.resetList(NUCHOICES=list(self.master.data.columns))

        

class dataTransform(tk.Frame):
    def __init__(self,parent,DFRAME = None):  
        super().__init__(master = parent)
        self.filepath = ''
        #self.pack(fill="x", expand=True)
        self.configure(borderwidth=2, relief="ridge", highlightthickness=2)

################This is the master copy of the data##############
        #self.data = self.master.data.copy(deep = True)
        self.varlist0 = list(self.master.data.columns) #the original column names 
##################################################################
        
        self.test_label = tk.Label(self, text="Create New Variables:", fg = 'white', bg = 'blue')
        self.test_label.grid(row=2, column=0, sticky = 'w')
        
        self.selected_variable  = tk.StringVar()
        self.Label = tk.Label(self, text='Select Variables:').grid(row = 2, column = 1, sticky ='e')
        self.options = ttk.Combobox(self, values=self.varlist0,textvariable = self.selected_variable)
        self.options.grid(row = 2, column = 2, columnspan = 3)
        self.options.bind("<<ComboboxSelected>>", self.varupdate)
        self.my_buttona = tk.Button(self,text='Clear Selections',command= self.clear_selection )
        self.my_buttona.grid(row=2, column = 5, sticky = 'e',padx=10)
        self.my_buttonb = tk.Button(self, text  = "Add Variable", command= self.run_dmatrices)
        self.my_buttonb.grid(row = 2, column = 6, sticky = 'e',padx=10)

         
        self.meqn = tk.StringVar(None)
        self.teq1 = tk.Entry(self,textvariable = self.meqn, width = 80)
        self.teq1.grid(row = 3, column = 0, columnspan=8, sticky = 'e',padx=10)
        
               
    def run_dmatrices(self, *args):
        mstr = self.meqn.get()        
        res = doDesign(MODEL_STRING = mstr, DATA = self.master.data)  
        if (res is not None):
            self.master.dfrm.do_display(res)
            #self.data = res.copy(deep = True)    
            gdata.log_It(f"doDesign(MODEL_STRING = {mstr}, Data = dataframe)")
############Updating master copy of data and the variable options lists in dataFilter and dataTransform########################           
            #self.master.data = self.data.copy(deep = True) #move transformed data back to parent
            self.master.data = res.copy(deep=True)
            gdata.put_Data(self.master.data)
            
        #change the list options in the filter, transform, rename, and reform widgets   

            self.master.filterer.options['values'] = list(self.master.data.columns)
            self.master.renameit.options['values'] = list(self.master.data.columns)
            self.master.reFormer.row_widget.resetList(NUCHOICES=list(self.master.data.columns))
            self.master.reFormer.col_widget.resetList(NUCHOICES=list(self.master.data.columns))
            self.options['values'] = list(self.master.data.columns)
            self.master.varlist0 = list(self.master.data.columns)
            self.master.broadcastData(self)
            #update number of  rows and columns on data Wrangle Data panel
            self.master.filelabel.config(text = gdata.fpath + f"   #Rows = {len(gdata.data)} #Columns = {len(gdata.data.columns)}")
        else:
            gdata.log_It(f"Wrangle DATA: Variable Transformation {mstr} Failed.")
            #reset the list options in the filter, transform, rename, and reform widgets   
            self.meqn.set('')
            self.master.filterer.options['values'] = list(self.master.data.columns)
            self.master.renameit.options['values'] = list(self.master.data.columns)
            self.master.reFormer.row_widget.resetList(NUCHOICES=list(self.master.data.columns))
            self.master.reFormer.col_widget.resetList(NUCHOICES=list(self.master.data.columns))
            self.options['values'] = list(self.master.data.columns)
            self.master.varlist0 = list(self.master.data.columns)
            self.master.broadcastData(self)
            #update number of  rows and columns on data Wrangle Data panel
            self.master.filelabel.config(text = gdata.fpath + f"   #Rows = {len(gdata.data)} #Columns = {len(gdata.data.columns)}")

##################################################################
        return

    def clear_selection(self,*args):
        self.meqn.set('')
        self.options['values']= list(self.master.data.columns)
        return
    
    def varupdate(self,event):
        varlist0 = list(self.master.data.columns)
        current_varlist = str(self.meqn.get()).split('+')
        #nuisance: apparently, if split finds an empty string it returns [''], not []
        if current_varlist[0] == '': current_varlist.pop(0)
        newvar = str(self.selected_variable.get())
        #add newvar to the list of current variables if it is new
        if newvar in current_varlist:
            return
        current_varlist.append(newvar)
        self.meqn.set("+".join(current_varlist))
        #now reset the remaining options
        remaining_varlist = [item for item in varlist0 if item not in current_varlist]
        self.options['values'] = remaining_varlist
        self.options.set("")


class dataFilter(tk.Frame):
    def __init__(self, parent, DATA_in = None):  
        super().__init__(master = parent)
        self.configure(borderwidth=2, relief="ridge", highlightthickness=2)
        #self.configure(borderwidth=2, relief="flat", highlightthickness=2)
        self.config(width = 800, height = 450)# this doesn's seem to do anything

        #parent data is now accessible in self.parent.zzz
        self.filterindicator = tk.StringVar(self,'No')
############This is the master copy of data ########################           
        self.data = self.master.data
####################################################################
        self.varlist0 = list(self.master.data.columns)
        self.varlistnum = [item for item in self.data.columns if is_numeric_dtype(self.data[item])]
        self.nudata = pd.DataFrame()
        
      
        self.fltr_type=tk.StringVar(self)
        self.fl0 = tk.Frame(self)
        #self.fl0.configure(borderwidth=2, relief="flat", highlightthickness=1)

        self.label0 = tk.Label(self.fl0, text="Filtering: ", fg = "white", bg = 'blue').pack(side = tk.LEFT)        
        self.label = tk.Label(self.fl0, text='Filter Type:').pack(side = tk.LEFT)
         
        self.fltrradio = tk.Radiobutton(self.fl0,text = 'Numeric', variable = self.fltr_type, value = 'Numeric', command = self.update_ftype)
        self.fltrradio.pack(side = tk.LEFT)
        self.fltrradio = tk.Radiobutton(self.fl0,text = 'Categorical', variable = self.fltr_type, value = 'Categorical', command = self.update_ftype)
        self.fltrradio.pack(side = tk.LEFT, expand = True, fill = tk.X)

        self.fl0.pack(side = tk.TOP)
        
        self.fl1 = tk.Frame(self)
        self.fl1.configure(borderwidth=2, relief="flat", highlightthickness=1)
        self.selected_variable  = tk.StringVar()  #We are filtering on this variable.
        
        self.Label = tk.Label(self.fl1, text='Filter Variable:').pack(side = tk.LEFT)
        self.options = ttk.Combobox(self.fl1, values=self.varlist0,textvariable = self.selected_variable)
        self.options.pack(side = tk.LEFT)
        #self.pack(side = tk.TOP, anchor = 'w')
        self.options.bind("<<ComboboxSelected>>", self.varupdate)
        
        self.filterItButton = tk.Button(self.fl1,text = 'Apply Filter', command = self.do_filter)
        self.filterItButton.pack(side = tk.LEFT)

        self.fl1.pack(side =tk.TOP)
        self.fl1.pack_forget()
        
    def update_ftype(self, *args):
        # if the selected filter type is numeric, then eliminate non-numerical variables from consideration
        fltr_type = self.fltr_type.get()
        self.selected_variable.set('')
        varlist0 = list(self.master.data.columns)
        if fltr_type == 'Numeric' :
            self.options['values'] = [item for item in varlist0 if is_numeric_dtype(self.master.data[item])]
            self.fl1.pack(side = tk.TOP)
        elif fltr_type == 'Categorical' :
            self.options['values'] = varlist0
            self.fl1.pack(side = tk.TOP)
        else:
            return
        
    def do_cancel(self, *args):
        self.flt.destroy() 
        self.selected_variable.set('')
        self.fltr_type.set('')
        return

    def do_filter(self, *args):
        filtervar = self.selected_variable.get()
        self.configure(borderwidth=2, relief="ridge", highlightthickness=2)
        #self.configure(borderwidth=2, relief="flat", highlightthickness=2)

        if filtervar == '':
            messagebox.showerror(' ',"Choose a variable on which to filter before filtering.")
            self.fl1.pack_forget()
            self.fltr_type.set('')
            return           
############This is the master copy of the current data ########################           
        self.data = self.master.data.copy(deep = True)
####################################################################
        if self.fltr_type.get() == 'Categorical' :
            #filterlist = self.flt.meqn.get().split(',')
            filterlist = self.flt.invalues
            filtervar = self.selected_variable.get() 
            #TODO: find a better way to keep the index in sync with choice list
            rowchoice = pd.Series(map(lambda x:str(x),self.data[filtervar])).isin(filterlist)
            rowchoice.index = self.data.index
            self.nudata = self.data.loc[rowchoice]
            gdata.log_It(f"Filtering on: {filtervar} Permissable values: {','.join(filterlist)}")

        else:
            try:
                filterlower = float(self.flt.lowerlim.get())
                filterupper = float(self.flt.upperlim.get())
            except: #if the float cast fails, revert to the upper and lower limits of the variable (no filtering)
                messagebox.showerror(' ', "Numerical filter upper or lower bound could not be interpreted.  Reverting to variable upper and lower bounds.")
                filterlower = np.nanmin(self.data[filtervar])
                self.flt.lowerlim.set(str(filterlower))
                filterupper = np.nanmax(self.data[filtervar])
                self.flt.upperlim.set(str(filterupper))
               
            if self.flt.in_or_out.get() == "Inside":
                self.nudata = self.data.loc[((self.data[filtervar] >= filterlower) & (self.data[filtervar] <= filterupper))]
                gdata.log_It(f"Filtering on: {filtervar} accepting values between: {filterlower} to {filterupper} inclusive.")
            else:
                self.nudata = self.data.loc[~((self.data[filtervar] >= filterlower) & (self.data[filtervar] <= filterupper))]
                gdata.log_It(f"Filtering on: {filtervar} accepting values NOT between: {filterlower} and {filterupper} inclusive.")

                
############Updating master copy of data ######################## 
        self.master.filelabel.config(text = gdata.fpath + f"   #Rows = {len(self.nudata)} #Columns = {len(self.nudata.columns)}")

        gdata.log_It(f"Filter finished. Rows remaining: {len(self.nudata)}")
                  
        self.master.dfrm.do_display(self.nudata)
        self.master.data = self.nudata.copy(deep = True)
        gdata.put_Data(self.nudata)
        self.master.broadcastData(self)
        #self.flt.destroy()
#################################################################
        return
                
    def varupdate(self, event):
        vnm = self.selected_variable.get()
        filter_type = self.fltr_type.get()
        #self.flt.in_or_out.set('')
        if vnm == '' : return
        if (self.filterindicator.get() == 'Yes'): self.flt.destroy()
        rownames = list(self.master.data[vnm].unique())
        if filter_type == 'Numeric':
            self.flt = fVar_num(self, self.master)
            self.flt.in_or_out.set('Inside')
            self.flt.pack(side = tk.TOP)
            self.filterindicator.set('Yes')
            return
        elif filter_type == 'Categorical':
            self.flt = fVar_cat(self,self.master)
            self.flt.in_or_out.set('Include')
            self.flt.pack(side = tk.TOP, anchor = 'w')
            self.filterindicator.set('Yes')
            #self.fltCat.pack(tk.TOP, anchor = 'w', expand = True)
        else:
            return
        return

class fVar_num(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(master = parent)
        self.configure(borderwidth=2, relief="flat", highlightthickness=1)

        #self.master = master
        #self.mainself = mainslf        
        self.lowerlim = tk.StringVar()
        self.upperlim = tk.StringVar()
        #xv = vname
        xv = self.master.selected_variable.get()
        self.xmin = np.nanmin(self.master.master.data[xv])
        self.xmax = np.nanmax(self.master.master.data[xv])
        
        self.lowerlim.set(str(self.xmin))
        self.upperlim.set(str(self.xmax))
        
        self.cancelbutton = tk.Button(self,text='Cancel Filter', command = self.do_cancel)
        self.cancelbutton.grid(row = 0, column = 4)
        
        self.fltlab = tk.Label(self, text= f"Limits for {xv}").grid(row = 0, column = 0)
        self.minlabel = tk.Label(self, text = "Min: " + str(self.xmin) ).grid(row = 0, column = 1)
        self.maxlabel = tk.Label(self, text = "Max: " + str(self.xmax)).grid(row = 0, column = 3)
        
        self.lblab = tk.Label(self, text = "Lower Filter Limit:").grid(row = 1, column = 0)       
        self.lbfltr = tk.Entry(self,textvariable = self.lowerlim, width = 20)
        self.lbfltr.grid(row = 1, column = 1)
        self.ubfltr = tk.Label(self,text = "Upper Filter Limit:").grid(row = 1, column=2)
        self.ubfltr = tk.Entry(self,textvariable = self.upperlim, width = 20)
        self.ubfltr.grid(row = 1, column = 3)
        
        self.inoroutLabel = tk.Label(self, text="Filter Action:").grid(row =3, column = 0, sticky = 'w')
        self.in_or_out=tk.StringVar(self)
        self.fltrradio2 = tk.Radiobutton(self,text = 'Inside the specified bounds', variable = self.in_or_out, value = 'Inside')
        self.fltrradio2.grid(row=3, column = 1, sticky = 'w')
        self.fltrradio2 = tk.Radiobutton(self,text = 'Outside the specified bounds', variable = self.in_or_out, value = 'Outside')
        self.fltrradio2.grid(row = 3, column = 2, sticky = 'w')

    def do_cancel(self):
        self.master.fl1.pack_forget()
        self.destroy()
        
class fVar_cat(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(master = parent) 
        self.xv = self.master.selected_variable.get()
        #self.valuelist0 = list(map(lambda x: str(x),self.master.data[self.xv].unique()))
        self.valuelist0 = list(self.master.data[self.xv].unique())
        if len(self.valuelist0) > 500:
                messagebox.showerror(' ', f"The variable {self.xv} takes on {len(self.valuelist0)} different values.  That seems like a lot. Could I interest you in a different filter variable?")
                self.destroy()
                return

        #self.xvalues = self.master.master.data[self.xv]
        self.filter_values = []
        self.value_list = self.valuelist0
        
        self.cancelbutton = tk.Button(self,text='Cancel Filter', command = self.do_cancel)
        self.cancelbutton.pack(side = tk.RIGHT, anchor = 'n')
       
        self.catf0 = tk.Frame(self)              
        self.inoroutLabel = tk.Label(self.catf0 , text="Filter Action:").grid(row =0, column = 0, sticky = 'w')
        self.in_or_out=tk.StringVar(self)
        self.fltrradio2 = tk.Radiobutton(self.catf0 ,text = 'Default: All Included', variable = self.in_or_out, value = 'Include', command = self.update_fopts)
        self.fltrradio2.grid(row=0, column = 1, sticky = 'w')
        self.fltrradio2 = tk.Radiobutton(self.catf0 ,text = 'Default: All Excluded', variable = self.in_or_out, value = 'Exclude', command = self.update_fopts)
        self.fltrradio2.grid(row = 0, column = 2, sticky = 'w')
        self.catf0.pack()
        
        self.selected_in = tk.StringVar()
        self.selected_out = tk.StringVar()
        
        self.catf = tk.Frame(self)
        self.catselect_in_label = tk.Label(self.catf, text = "Remove")
        self.catselect_in_label.grid(row= 0, column =1)
        self.catselect_out_label = tk.Label(self.catf,text = "Add")
        self.catselect_out_label.grid(row = 0, column = 2)
        
        self.catselect_in = ttk.Combobox(self.catf, values=[], textvariable = self.selected_in)
        self.catselect_in.bind("<<ComboboxSelected>>", self.varupdate_in)
        self.catselect_in.grid(row = 1, column = 1, padx = 10)
        self.catselect_out = ttk.Combobox(self.catf, values = [], textvariable = self.selected_out)
        self.catselect_out.bind("<<ComboboxSelected>>", self.varupdate_out)
        self.catselect_out.grid(row = 1, column = 2, padx = 10)
        
        self.meqn = tk.StringVar(None)
        self.teq1label = tk.Label(self.catf,text="Row values selected:").grid(row = 2, column=0, sticky = 'e', padx = 5)
        self.teq1 = tk.Entry(self.catf,textvariable = self.meqn, width = 90)
        self.teq1.grid(row = 2, column = 1, columnspan=6, sticky = 'w',padx=10)        
        self.catf.pack()
        
        self.invalues = list(map(lambda x: str(x),self.valuelist0)) 
        self.catselect_in['values'] = self.invalues
        self.outvalues = []
        self.catselect_out['values'] = self.outvalues
        
    def do_cancel(self):
        self.master.fl1.pack_forget()
        self.destroy()

    def update_fopts(self,*args):
        #note: categorical variables could be characters or numbers (e.g. zip codes). 
        # selected_in.get() and selected_out.get() below always return strings. 
        #convert everything to strings for filtering logic for categorical filter
        self.valuelist0 = list(self.master.data[self.xv].unique())
        if len(self.valuelist0) > 500:
                messagebox.showerror(' ', f"The variable {self.xv} takes on {len(self.valuelist0)} different values.  That seems like a lot. Could I interest you in a different filter variable?")
                self.destroy()
                return
        invalues  =  list(map(lambda x: str(x),self.valuelist0))
        if self.in_or_out.get() == 'Include': 
            self.invalues = invalues
            self.catselect_in['values'] = invalues
            self.outvalues = []
            self.catselect_out['values'] = self.outvalues
            self.meqn.set(', '.join(invalues))
        else:
            self.invalues = []
            self.outvalues = invalues
            self.catselect_in['values'] = []
            self.catselect_out['values']= self.outvalues
            self.meqn.set('')
        
    def varupdate_in(self,event):
        nuvar = self.selected_in.get()
        if (nuvar in self.outvalues): return
        if not(nuvar in self.invalues): return
        self.invalues.remove(nuvar)
        self.outvalues.append(nuvar)
        self.catselect_in['values'] = self.invalues
        self.catselect_out['values'] = self.outvalues
        self.meqn.set(", ".join(self.invalues))
        self.selected_in.set('')
       
    def varupdate_out(self,event):
        nuvar = self.selected_out.get() #this will always be a string
        if not(nuvar in  self.outvalues): return
        if (nuvar in  self.invalues): return
        self.outvalues.remove(nuvar)
        self.invalues.append(nuvar)
        self.catselect_in['values'] = self.invalues
        self.catselect_out['values'] = self.outvalues
        self.meqn.set(", ".join(self.invalues))

        self.selected_out.set('')







if __name__ == "__main__":
    
    gdata = gd.globalData()
    class solo(tk.Tk):
        def __init__(self):
            super().__init__()
            self.geometry("450x50+0+0")
            self.onButton = tk.Button(self, text = "Get Data", command = self.getData).pack(side = tk.LEFT, padx = 10)
            self.goPivot  = tk.Button(self, text = "Filter Data", command = self.filterD).pack(side = tk.LEFT, padx = 10)
            self.offButton = tk.Button(self, text="Graceful Exit", command = self.quit).pack(side = tk.LEFT, padx = 10)
            self.pivotOn = False
            self.regOn = False
            self.plotOn = False

            
            #gst = goPivot(self)
        
        def filterD(self,*args):
            if len(gdata.data) == 0: return
            self.gst = goData(self)
            self.gst.syncData()
                        
        def quit(self,*args):
            self.destroy()
            return 
        
        def getData(self,*args):
           #self.dfDisplay()
           #file_types = [("CSV Files", "*.csv"), ("Text Files", "*.txt"), ("All Files", "*.*")]
            file_types = [("CSV Files", "*.csv"),("Excel Files", "*.xlsx"), ("Stata Files", "*.dta")]
            file_path = filedialog.askopenfilename(filetypes=file_types, title="Select a File")
            if file_path != '':
                #cautious reading
                try:
                    df_temp= pd.read_csv(file_path, engine= 'python', header=None, nrows=1)
                    inputheader =  df_temp.iloc[0].fillna(' ')
                    headercols = len(inputheader)
                    df_in = pd.read_csv(file_path, skiprows = 1, header=None) # header=0 is default
                    if len(df_in.columns) != headercols:
                         # This case might happen if the header line had a different count from the first data line
                         #print("Header column count does not match the first column count.")
                         messagebox.showerror(title= '  ', message=f"Column label count ({headercols}) does not match the data column count {len(df_in.columns)}. Proceeding, not end well. Check data and try again.")
                    else:
                         df_in.columns = inputheader
                         print(f"Dataframe loaded successfully with {headercols} columns per row.")
                         messagebox.showerror(title= '  ', message=f"Dataframe loaded successfully with {headercols} columns per row.")
                except pd.errors.ParserError as e:
                    print(f"Error reading CSV: {e}")
                    messagebox.showerror(title = '  ',message=f"Error reading CSV: {e}" )
                    # The error message will often indicate the problematic row number
                #df_in = pd.read_csv(file_path)
                self.fpath = file_path
                #self.doReset(df_in)
                gdata.reset_Data(file_path, df_in)
            return
            

    app = solo()
    app.mainloop()
    
        

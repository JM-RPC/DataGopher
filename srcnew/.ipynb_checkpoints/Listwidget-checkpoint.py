#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 23 11:05:26 2025

@author: Knucklehead
"""


import numpy as np 

import pandas as pd
from pandas.api.types import is_numeric_dtype
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

import globalData as gd
from   globalData import gdata



class goList(tk.Frame):
    def __init__(self, parent, TEXT = '', CHOICES = []):  
        super().__init__(master = parent)
        self.configure(borderwidth=2, relief="ridge", highlightthickness=1)
        self.choices = CHOICES
        self.rowlist = []
        self.rowchoices = tk.StringVar(self)
        self.rowslabel = tk.Label(self,text=TEXT)
        self.rowslabel.grid(row = 0, column=0, sticky = 'e', padx = 5)
        self.teq1 = tk.Entry(self,textvariable = self.rowchoices, width = 30)
        self.teq1.grid(row = 0, column = 1, columnspan=6, sticky = 'w',padx=10) 
        
        self.selected_row_in = tk.StringVar(self)
        self.selected_row_out = tk.StringVar(self)
        
        self.f1rowlabin = tk.Label(self, text = "Add "+TEXT)
        self.f1rowlabin.grid(row = 1, column = 0)
        
        self.rowselect_in = ttk.Combobox(self, values=self.choices, textvariable = self.selected_row_in, width = 10)
        self.rowselect_in.bind("<<ComboboxSelected>>", self.varupdate_row_in)
        self.rowselect_in.grid(row = 1, column = 1, padx = 10)
        
        self.f1rowlabout = tk.Label(self, text = "Delete " + TEXT)
        self.f1rowlabout.grid(row = 1, column = 2)
        
        self.rowselect_out = ttk.Combobox(self, values=[], textvariable = self.selected_row_out, width = 10)
        self.rowselect_out.bind("<<ComboboxSelected>>", self.varupdate_row_out)
        self.rowselect_out.grid(row = 1, column = 3, padx = 10)
 

    def varupdate_row_in(self, *args):
        nuvar = self.selected_row_in.get()
        if nuvar == '' :return
        if nuvar in self.rowlist: return
        self.rowlist.append(nuvar)
        self.selected_row_in.set('')
        rowchoices = [item for item in self.choices if item not in self.rowlist]
        self.rowselect_in['values'] = rowchoices
        self.rowselect_out['values'] = self.rowlist
        self.rowchoices.set(', '.join(self.rowlist))
        return
    
    def varupdate_row_out(self, *args):
        oldvar = self.selected_row_out.get()
        if oldvar == '': return
        if oldvar not in self.rowlist: return
        self.rowlist.remove(oldvar)
        self.selected_row_out.set('')
        rowchoices = [item for item in self.choices if item not in self.rowlist]
        self.rowselect_out['values'] = self.rowlist
        self.rowselect_in['values'] = rowchoices
        self.rowchoices.set(', '.join(self.rowlist))
        
    def resetList(self, NUTEXT=None, NUCHOICES=None):
        if NUTEXT is not None:
            self.rowslabel.config(text = NUTEXT)
            self.f1rowlabin.config(text = "Add " + NUTEXT)
            self.f1rowlabout.config(text = "Delete " + NUTEXT)
            
        if NUCHOICES is not None:
            self.choices = NUCHOICES
            self.rowlist = []
            self.rowselect_in['values'] = NUCHOICES
            self.rowselect_out['values'] = []
            self.rowchoices.set('')
            self.selected_row_in.set('')
            self.selected_row_out.set('')
            
    def getList(self):
        return(self.rowlist)
        
    

if __name__ == "__main__":
    class goSub(tk.Toplevel):
        def __init__(self, TEXT = '', CHOICES = []):
            super().__init__()
            self.lab = tk.Label(self,text = "Top level").pack(pady = 20)
            self.sframe = tk.Frame(self)
            self.framelab =  tk.Label(self.sframe,text = "frame level").pack(pady = 20)
            self.listwidg = goList(self.sframe,TEXT = TEXT, CHOICES = CHOICES)
            self.listwidg.pack()
            self.sframe.pack()

    class solo(tk.Tk):
        def __init__(self):
            super().__init__()
            self.listwidgetstatus = 'off'
            self.fr1 = tk.Frame(self)
            self.onButton = tk.Button(self.fr1, text = "Get Data", command = self.getData).pack(side = tk.LEFT, padx = 10)
            self.syncButton = tk.Button(self.fr1, text="Sync Data", command = self.syncData).pack(side = tk.LEFT, padx = 10)
            self.goPivotButton  = tk.Button(self.fr1, text = "List Widget", command = self.pivD).pack(side = tk.LEFT, padx = 10)
            self.getListButton = tk.Button(self.fr1, text = "Get List",command = self.getList).pack(side = tk.LEFT, padx = 10)
            self.offButton = tk.Button(self.fr1, text="Graceful Exit", command = self.quit).pack(side = tk.LEFT, padx = 10)
            self.fr1.pack(side = tk.TOP)
            self.listLabel = tk.Label(self, text = "List: ")
            self.listLabel.pack(side = tk.BOTTOM, anchor = 'w')
            
            #gst = goPiv(self)
        
        def pivD(self,*args):
            if self.listwidgetstatus == 'on':
                self.gst.lift()
                return
            self.gst = goSub(TEXT = "Items:", CHOICES=['A','B', 'C','D','E','F','G'])
            self.listwidgetstatus = 'on'
            return

        def syncData(self, *args):
            if self.listwidgetstatus == "off": 
                messagebox.showerror(" ","Dr. Knucklehead sez: You must have a List Widget before you can sync with it.")
                return
            if not gdata.data.empty:
                self.gst.listwidg.resetList(NUTEXT = 'Columns:', NUCHOICES = list(gdata.data.columns))    
            else:
                messagebox.showerror(" ","Dr. Knucklehead sez: \nyou must Get Data before you can Sync Data.")
        
        def getList(self, *args):
            if self.listwidgetstatus == "off": 
                messagebox.showerror(" ","Dr. Knucklehead sez: \n To get a List you must have a List Widget..and it must have a list.")    
                return
            rlist = self.gst.listwidg.getList()
            self.listLabel.config(text = "List: " + ", ".join(rlist))
            
            
        def quit(self,*args):
            #plt.close('all')
            self.destroy()
            return 
        
        def getData(self,*args):
           #self.dfDisplay()
           #file_types = [("CSV Files", "*.csv"), ("Text Files", "*.txt"), ("All Files", "*.*")]
           if len(gdata.data) > 0:
               self.fpath = gdata.fpath
               #self.doReset(gdata.data)               
           else:
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

    #fileGetWindow = dr.fileBrowsePreview()
    #df = fileGetWindow.data
    #filename = fileGetWindow.filepath
    import globalData as gd

    
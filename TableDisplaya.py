#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  5 19:20:36 2025

@author: John
"""

import tkinter as tk
from tkinter import ttk
import pandas as pd
import os
import globalData as gd
from globalData import gdata
from tkinter import filedialog, ttk

class displayFrame_txt(tk.Frame):    
    def __init__(self,parent,Pivot_Table = None):  
        super().__init__(master = parent)
        #make the window spiffy
        self.configure(borderwidth=2, relief="flat", highlightthickness=0)
        #self.config(width = 800, height = 450)
        self.pack(side = tk.TOP) 
        #self.grid(row=5, column = 0, columnspan = 5)
        titlestr = f"                                       Preview                                             "
        self.titlelabel = tk.Label(self,text = titlestr, fg = 'white', bg = 'blue').pack(side = tk.TOP, expand = True, fill = tk.X)
        # now make it scroll
        self.filepath = ""
        self.showdata = ""
        self.hscroll = tk.Scrollbar(self, orient = 'horizontal')
        self.hscroll.pack(side = tk.BOTTOM, fill = tk.X)
        self.vscroll = tk.Scrollbar(self)
        self.vscroll.pack(side = tk.RIGHT, fill = tk.Y)
        
        self.txtbx = tk.Text(self, width = 140, height = 30, wrap = tk.NONE, xscrollcommand = self.hscroll.set, yscrollcommand = self.vscroll.set)
        self.txtbx.pack()

        self.txtbx.pack(side=tk.BOTTOM, fill=tk.X, expand = True)
        self.hscroll.config(command=self.txtbx.xview)
        self.vscroll.config(command=self.txtbx.yview)
        
        if Pivot_Table is not None:
            self.do_display(PT=Pivot_Table)


    def do_display(self,PT = None):
        if PT is None:
            return
        else:
            tbltxt = f" rows = {len(PT)} \n" + PT.to_string(max_rows=1000)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_columns', None)  # Display all columns
        pd.set_option('display.width', 1000)       # Set a wide display width
        self.txtbx.delete("1.0","end")
        self.txtbx.insert(tk.END,tbltxt)        
        return 
    
    
if __name__ == "__main__":
    

    class solo(tk.Tk):
        def __init__(self):
            super().__init__()
            self.geometry("900x300+0+0") 
            self.title("Table Display Standalone")
            
            self.f0 = tk.Frame()
            self.onButton = tk.Button(self.f0, text = "Get Data", command = self.getData).pack(side = tk.LEFT, padx = 10)
            #self.goPivot  = tk.Button(self.f0, text = "DisplayPivotTable", command = self.showData_1).pack(side = tk.LEFT, padx = 10)
            self.goPivot  = tk.Button(self.f0, text = "displayFrame_txt", command = self.showData_2).pack(side = tk.LEFT, padx = 10)
            #self.goPivot  = tk.Button(self.f0, text = "DataFrameTreeView", command = self.showData_3).pack(side = tk.LEFT, padx = 10)
            self.offButton = tk.Button(self.f0, text="Graceful Exit", command = self.quit).pack(side = tk.LEFT, padx = 10)
            self.f0.pack(side = tk.TOP)
            



            # self.f1 = tk.Frame(self)
            # self.tbldisp = DisplayPivotTable(self.f1)
            # print("Packing DisplayPivotTable")
            # self.tbldisp.pack()            
            # self.f1.pack(side=tk.BOTTOM)

            self.f2 = tk.Frame(self)
            self.txdisp = displayFrame_txt(self.f2)
            print("Packing: displayFrame_txt")
            self.txdisp.pack()            
            self.f2.pack(side=tk.BOTTOM)

            
            # self.f3 = tk.Frame(self)
            # self.dfdisp = DataFrameTreeView(self.f3)
            # print("Packing: DataFrameTreeView")
            # self.dfdisp.pack()            
            # self.f3.pack(side= tk.BOTTOM)



            #gst = goPivot(self)
        
        def showData_1(self,*args):
            if len(gdata.data) == 0: return
            self.tbldisp.do_display(gdata.data)

        def showData_2(self,*args):
            if len(gdata.data) == 0: return
            self.txdisp.do_display(gdata.data)


        def showData_3(self,*args):
            if len(gdata.data) == 0: return
            self.dfdisp.do_display(gdata.data)



                        
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



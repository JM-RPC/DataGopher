#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 21 14:45:30 2025

@authors: Knucklehead & GitHub Copilot (AI-assisted)


"""

import tkinter as tk
from tkinter import ttk
import pandas as pd
from globalData import gdata





class DataFrameTreeView(tk.Frame):
    def __init__(self, parent):
        super().__init__(master = parent)
        #self.pack(fill="both", expand=True)



        # Create a Frame to hold the Treeview and Scrollbars
        self.tree_frame = tk.Frame(self)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)

        # Treeview: note show='headings' (we use explicit columns)
        self.tree = ttk.Treeview(self.tree_frame, selectmode='extended', show='headings')
        self.tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Add Vertical Scrollbar
        self.vsb = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.config(yscrollcommand=self.vsb.set)

        # Add Horizontal Scrollbar
        self.hsb = ttk.Scrollbar(self.tree_frame, orient="horizontal", command=self.tree.xview)
        self.hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.config(xscrollcommand=self.hsb.set)
        
        # Alternating row tag
        self.tree.tag_configure('oddrow', background='#F0F0F0')

        # Sort order tracking
        self.sort_order = {}

        # Bind click event for sorting
        self.tree.bind("<Button-1>", self.handle_click)

        # # Sort order tracking
        # self.sort_order = {}

        # # Bind click event for sorting
        # self.tree.bind("<Button-1>", self.handle_click)




    def do_display(self, dframe = pd.DataFrame()):
        #rows = len(dframe)
        #if rows == 0:
            #return
       
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        
        
        # Format the index header based on number of levels
        #index_header = "Index\n\n"


        # Configure Treeview columns and headings
        
        formatted_columns = list(dframe.columns)
        
        # Configure columns, including the index column
        columns =  formatted_columns
        self.tree['columns'] = columns
        self.tree['show'] = 'headings'
        
        # Define data column headings with formatting
        for i, col in enumerate(formatted_columns):
            # Determine column width based on content
            max_width = len(str(col)) * 10
            for value in dframe.iloc[:, i]:
                width = len(str(value)) * 10
                max_width = max(max_width, width)
            
            # IMPORTANT: stretch=False here as well
            self.tree.column(columns[i], 
                        anchor='center', 
                        width=min(max_width, 300),
                        minwidth=100,
                        stretch=False)
            self.tree.heading(columns[i], 
                            text=str(col),
                            anchor='center'
                            )
  
        #print(f"Inserting rows: {len(dframe)}")
        # Insert DataFrame rows into Treeview
        for index, row in dframe.iterrows():
            self.tree.insert("", "end", 
                             values=list(row),
                             tags=('oddrow',) if index % 2 else ())
            
        # Apply style to Treeview
        style = ttk.Style()
        style.configure("Treeview",
                    rowheight=25,
                    font=('Arial', 10))
        style.configure("Treeview.Heading",
                    font=('Arial', 10, 'bold'))
             
        # Force a geometry update so the scrollbar becomes active when needed
        self.update_idletasks()

        
 
    def handle_click(self, event):
        if self.tree.identify_region(event.x, event.y) == "heading":
            column = self.tree.identify_column(event.x)
            column_id = int(column[1]) - 1  # Convert column index to number
            self.sort_treeview(column_id)

        

    def sort_treeview(self, col):
        if col not in self.sort_order:
            self.sort_order[col] = False
        reverse = self.sort_order[col]
        lx = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        lx.sort(reverse=reverse)
        for index, (val, k) in enumerate(lx):
            self.tree.move(k, '', index)
        self.sort_order[col] = not reverse
        

if __name__ == "__main__":
    
    from tkinter import filedialog
    #import os
    #import globalData as gd


    class solo(tk.Tk):
        def __init__(self):
            super().__init__()
            self.geometry("900x500+100+100") 
            self.title("Table Display Standalone")
            
            self.f0 = tk.Frame()
            self.onButton = tk.Button(self.f0, text = "Get Data", command = self.getData).pack(side = tk.LEFT, padx = 10)
            #self.goPivot  = tk.Button(self.f0, text = "DisplayPivotTable", command = self.showData_1).pack(side = tk.LEFT, padx = 10)
            #self.goPivot  = tk.Button(self.f0, text = "displayFrame_txt", command = self.showData_2).pack(side = tk.LEFT, padx = 10)
            self.goPivot  = tk.Button(self.f0, text = "DataFrameTreeView", command = self.showData_3).pack(side = tk.LEFT, padx = 10)
            self.offButton = tk.Button(self.f0, text="Graceful Exit", command = self.quit).pack(side = tk.LEFT, padx = 10)
            self.f0.pack(side = tk.TOP)
            



            # self.f1 = tk.Frame(self)
            # self.tbldisp = DisplayPivotTable(self.f1)
            # print("Packing DisplayPivotTable")
            # self.tbldisp.pack()            
            # self.f1.pack(side=tk.BOTTOM)

            # self.f2 = tk.Frame(self)
            # self.txdisp = displayFrame_txt(self.f2)
            # print("Packing: displayFrame_txt")
            # self.txdisp.pack()            
            # self.f2.pack(side=tk.BOTTOM)

            
            self.f3 = tk.Frame(self)
            
            #self.f3.pframelab = tk.StringVar(self.f3,"This space available.")
            #self.f3.dfrmtitle = ttk.Label(self.f3, text = self.f3.pframelab.get())
            #self.f3.dfrmtitle.pack(side=tk.TOP)

            self.dfdisp = DataFrameTreeView(self.f3)
            print("Packing: DataFrameTreeView")
            self.dfdisp.pack()            
            self.f3.pack(side= tk.BOTTOM)



            #gst = goPivot(self)
        
        # def showData_1(self,*args):
        #     if len(gdata.data) == 0: return
        #     self.tbldisp.do_display(gdata.data)

        # def showData_2(self,*args):
        #     if len(gdata.data) == 0: return
        #     self.txdisp.do_display(gdata.data)


        def showData_3(self,*args):
            if len(gdata.data) == 0:
                return
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
    #import globalData as gd

        

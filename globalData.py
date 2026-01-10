#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  6 16:36:46 2025

@author: John
"""
import pandas as pd
import numpy as np
from datetime import datetime


class globalData():
    def __init__(self, data_in=pd.DataFrame()):
        self.data = data_in.copy(deep=True)
        #self.data0 = data_in.copy(deep = True)
        self.fpath = ''
        self.model_res = None
        self.model_data = None
        self.datatable = None
        self.logstr = ''
        #self.x2 = 0
        #self.x3 = 0
        
    def reset_Data(self, nupath = '', data_in = pd.DataFrame()):
        #reset the globalData object to contain the data set in data_in
        #data0 = the backup copy never changes only used to restore when needed
        #data = the working data set
        #self.data0 = data_in.copy(deep=True)
        self.data = data_in.copy(deep=True)
        self.fpath = nupath
        self.datatable = None
        return
    
    def put_Data(self, data_in=pd.DataFrame()):
        #Saves a changed (via new variables or filtering) into the working data set
        self.data = data_in.copy(deep=True)
        return

    def get_Data(self):
        #gets the working data set
        return (self.data)

    def show_Data(self):
        if len(self.data) > 0:
            self.data.head(10)
        return
            
    def restore_Data(self):
        #restores the working data set from the global data set.
        return(self.data)
    
    def log_It(self, msg = ''):
        self.logstr += "\n" + str(datetime.now()) + ": " + msg
        
    def log_Init(self):
        self.logstr = "\n" + str(datetime.now()) + ": Session Init"
        
    def log_Get(self):
        return(self.logstr)
    

gdata = globalData()


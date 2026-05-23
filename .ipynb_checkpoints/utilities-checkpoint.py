import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
import os

from tkinter import filedialog, messagebox, scrolledtext, ttk

def getData(self):
    df = None
    #filetypes = [("CSV Files", "*.csv")]
    filetypes = [("CSV files","*.csv"),("Excel files","*.xlsx"),("Old Excel files", "*.xls"),("Stata files","*.dta")]
    filepath = filedialog.askopenfilename(title="Open Data File",filetypes=filetypes)
    if filepath:
        if filepath.endswith('.csv'):
            try:
                df_temp= pd.read_csv(filepath, engine= 'python', header=None, nrows=1)
                inputheader = df_temp.iloc[0].copy(deep = True)
                headercols = len(inputheader)
                colnamelist = list(inputheader)
                headerNAs = sum(inputheader.isna())
                if headerNAs > 0:
                    naCol = [idx for idx, item in enumerate(inputheader.isna()) if item]
                    messagebox.showerror(" ",f"Columns: {naCol} do not have names. Temporary names have been assigned.")
                    for ix in naCol:
                        iy=0
                        dummyname = f"_*_{ix}_missing({iy})"
                        while dummyname in colnamelist:
                            iy += 1
                            dummyname = f"_*_{ix}_missing({iy})"
                        inputheader[ix] = str(dummyname)
                headercols = len(inputheader)
                df = pd.read_csv(filepath, skiprows = 1, header=None) # header=0 is default
                if len(df.columns) != headercols:
                     # Header line has a different length from the first data line
                     print(inputheader)
                     print(df.columns)
                     messagebox.showerror(title= '  ', message=f"Column label count ({headercols}) does not match the data column count {len(df.columns)}. Proceeding will not end well. Check data and try again.")
                     return
                else:
                     #df.columns = [str(item) for item in inputheader] #make sure all column names are strings
                     df.columns = inputheader
                     lstr = f"df = pd.read_csv('{filepath}',engine='python')"
            except pd.errors.ParserError as e:
                print(f"Error reading CSV: {e}")
                messagebox.showerror(title = '  ',message=f"Error reading CSV: {e}" )
                return
            except UnicodeDecodeError as ef:
                messagebox.showerror(" ", f"Error Reading CSV: {ef}. Recode data as utf-8")
                return
            except Exception as exr:                 
                messagebox.showerror("Error Reading CSV:",f"Failed to read CSV file:\n{exr}")
                return
        elif filepath.endswith(('.xlsx','.xls')):
            try:
                df = pd.read_excel(filepath)
            except Exception as e:
                messagebox.showerror("Error",f"Failed to read Excel file:\n{e}")
                return
        elif filepath.endswith('.dta'):
            try:
                df = pd.read_stata(filepath)
            except Exception as e:
                messagebox.showerror("Error",f"Failed to read Stata file:\n{e}")
                return
        else:
            messagebox.showerror("Error","Unsupported file type. Please select a CSV, Excel or Stata .dta file.")
            return
        
        if df.empty:
            messagebox.showwarning("Warning","The selected file is empty or could not be read.")
            return
        suminf = sum([sum(df[item].isin([-np.inf,+np.inf])) for item in df.columns])
        listinf = [item for item in df.columns if sum(df[item].isin([-np.inf, +np.inf])) >0]
        if suminf > 0:
            emsg = f"Data file contains {suminf} infinite values in columns: {",".join(listinf)}\n Convert to NA? (Yes = convert, No = do not convert)"
            ynbool = messagebox.askyesno(" ",emsg)
            if ynbool:
                df.replace([np.inf, -np.inf], np.nan, inplace=True)     
        success_msg = f"Data loaded successfully from file {fpath} \n{df.shape[0]} rows and {df.shape[1]} columns."
        success_msg = success_msg + f"\n{len(df) - len(df.dropna())} rows contain missing data."
        messagebox.showinfo("Info",success_msg)
            
        badnames = [checkName(item) for item in df.columns if checkName(item) is not None]
        if len(badnames) > 0: 
            badnames_str = " ], [ ".join(badnames)
            mstr  = "Found nonconforming variable names:\n" + "[" + badnames_str + "]\n"
            mstr += "Variable names may consist of letters, numbers \nand underscores,"
            mstr += "no initial numerals, other symbols or included spaces.  "
            mstr += "Variables with non-conforming names may \nbe excluded from modelling and plotting.\n"
            mstr += "\n You can fix the non-conforming names by renaming those \n variables with 'Wrangle Data' module,"
            mstr += "saving the \nrenamed data and then reloading the data. \n"
            mstr += "Or, you may proceed and take your chances....YOU HAVE BEEN WARNED...\n"

            messagebox.showinfo(" ", mstr)
    else:
        messagebox.showinfo("Info","No file selected.")
    return(df)     

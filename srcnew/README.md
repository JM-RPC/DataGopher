# DataGopher
Python GUI application for statistical modeling and data visualization

DataGopher consists of four main applications, each one occupying a separate window and triggered by an appropriately named button: "Wrangle Data", "Pivot Data", "Plot Data", and  "Models".  Each button triggers  a python tkinter application located in a similarly named file.  The design philosophy is to provide the thinnest possible GUI layer between the python functions and the user.  This allows non-programmers to take advantage of python's tested, robust, scalable, and (best of all), FREE data science tools in a manageable open source package.

The "Get Data" button does what it says.  It opens a file chooser dialog box and allows you to choose from Excel .csv, .xlsx, and .xls files as well as some stata .dta files (compatibility with stata data files depends on which stat verison saved the file).   This feature could easily be extended to other file types.

The "Models" button makes various linear and generalized linear models available: OLS for linear regression, logit and probit for modeling binary response variables, negative binomial and Poisson which can be appropriate for positive integer response variables and gamma which is sometimes useful for positive continuous response variables.   These are but a few of the modelling options available in python's statsmodels module, you should use the model that best fits your modelling task rather than choosing a model based on it's availabliity on a menu or the type of the response variable it expects.  "Models" also offers some of the typical plots for visualizing the model being fit. Models resides in the file goModel.py.

The "Plot Data" button, much as the name suggestes, makes various plotting capabilities drawn from matplotlib and seaborn available (and resides in the file goPlot.py). 

The "Wrangle Data"  button offers variable transformation, row filtering, and variable renaming capabilities and is based on pandas and patsy (in the file goDataFilter.py).

The "Pivot Data" button offers  a spreadsheet style pivot table capability (and resides in the file goPivotb.py). 

The application keeps a running log of everything you've done.   If you want to preserve this log, the "Save Log" button is the button for you.

The right-most button, labeled "Graceful Exit", does exactly what it says.  It shuts down the DataGopher app and cleans up all remaining windows.
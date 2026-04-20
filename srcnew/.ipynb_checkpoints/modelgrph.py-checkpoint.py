import pandas as pd
from pandas.api.types import is_numeric_dtype
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
matplotlib.use('TkAgg')
import numpy as np
import statsmodels.api  as sm
import statsmodels.formula.api as smf 
from statsmodels.graphics.regressionplots import plot_partregress_grid, plot_leverage_resid2, influence_plot, plot_fit
from patsy import dmatrices, dmatrix, NAAction
import seaborn as sb
from sklearn.metrics import roc_curve, auc


basecolors0 = ['blue', 'red',  'green', 'yellow', 'magenta', 'cyan', 'violet',
               'orange',  'goldenrod', 'grey', 'gold', 'silver', 'orangered', 'darkolivegreen',
               'olive', 'khaki', 'thistle', 'lightsteelblue', 'slateblue', 'black', 'darkviolet',
               'brown', 'indigo', 'hotpink', 'lavender']


def getcolor(cvar, col_data):
    dfc = pd.DataFrame(col_data)
    choicesCo = list(dfc[dfc.columns[0]].unique())
    choicesCo.sort()
    if (len(choicesCo) < len(basecolors0)):
        colorD = {item : basecolors0[choicesCo.index(item)]  for item in choicesCo}
        colorlist = [colorD[item] for item in col_data]
        lpatches = [mpatches.Patch(color = colorD[item],label = cvar + ', ' + str(item)) for item in colorD.keys()]
    else:
        cmap = plt.cm.plasma
        colorD = {item : cmap(choicesCo.index(item)/len(choicesCo)) for item in choicesCo}
        colorlist = [colorD[item] for item in col_data]
        lpatches = [mpatches.Patch(color = colorD[item],label = cvar +  ', ' + str(item)) for item in choicesCo]
    return colorD, colorlist, lpatches

#############################
### Model Plotting Functions
#############################


def doroc(MODEL = None):
    if (MODEL is None): return
    prediction_res = MODEL.get_prediction(transform = True)
    res_frame= prediction_res.summary_frame(alpha = 0.05)

    fpr, tpr, thresholds = roc_curve(MODEL.model.endog, res_frame['mean']) 
    roc_auc = auc(fpr, tpr)
    fig = plt.figure(figsize = (8,8))
    ax = fig.add_subplot()
    ax.plot(fpr, tpr)
    ax.plot([0, 1], [0, 1], 'k--')
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.set_title(f"ROC: {MODEL.model.formula}, AUC={round(roc_auc,5)}")
    fig.show()  #show the plots simultaneously
    #plt.show() #show plots one at a time
    return

def dopredictbin(res = None):
    if res is None: return
    xvpredictlist = list(res.model.exog_names)
    cvpredict = res.model.endog
    tstr = res.model.formula
    dsize = 8.0
    prediction_res = res.get_prediction(transform = True)
    res_frame= prediction_res.summary_frame(alpha = 0.05)
    ylabstr = "Est. Mean Response"
 
    for idx,xvpredict in enumerate(xvpredictlist):
        if idx == 0: continue
        fig, ax = plt.subplots() 
        sb.scatterplot(ax= ax, x = res.model.exog[:,idx], y = res_frame['mean'], hue = res.model.endog, palette = 'bright',s = dsize)
        plt.axhline(y=0, color='black', linestyle='-')
        plt.axhline(y=0.2, color = 'black', linestyle = 'dashed',linewidth = 0.5)
        plt.axhline(y=0.4, color = 'black', linestyle = 'dashed',linewidth = 0.5)
        plt.axhline(y=0.5, color = 'black', linestyle = 'solid',linewidth = 0.5)
        plt.axhline(y=0.6, color = 'black', linestyle = 'dashed',linewidth = 0.5)
        plt.axhline(y=0.8, color = 'black', linestyle = 'dashed',linewidth = 0.5)
        plt.axhline(y=1.0, color = 'black', linestyle = '-',linewidth = 0.5)
        plt.ylim((0, 1))
        plt.ylabel(ylabstr)
        plt.xlabel(xvpredict)
        plt.title(tstr)
        fig.show()  #show the plots simultaneously
        #plt.show() #show plots one at a time
    return

def dopredict(res = None):
    if res is None: return
    xvpredictlist = list(res.model.exog_names)
    tstr = res.model.formula
    depvar = res.model.endog
    dsize = 8.0
    prediction_res = res.get_prediction(transform = True)
    res_frame= prediction_res.summary_frame(alpha = 0.05)
    ylabstr = "Est. Mean Response"
    for idx,xvpredict in enumerate(xvpredictlist):
        if idx == 0: continue
        fig, ax = plt.subplots() 
        sb.scatterplot(ax = ax, x = res.model.exog[:,idx], y = depvar, color = 'blue',label = 'Observed', s= dsize)
        sb.scatterplot(ax = ax, x = res.model.exog[:,idx], y = res_frame['mean'], color = 'red',label = 'Predicted', s = dsize)
        #plt.ylim((0, 1))
        plt.ylabel(ylabstr)
        plt.xlabel(xvpredict)
        plt.title(tstr)
        fig.show()  #show the plots simultaneously
        #plt.show() #show plots one at a time
    return

def doresidual(res = None, mtype = 'OLS'):
    if res == None: return
    tstr = res.model.formula
    xvresidlist = list(res.model.exog_names)
    dsize = 8 #dot size
    if mtype != 'OLS': #if it's not OLS it's GLM
        vres = res.resid_deviance
        ylabstr = 'Deviance Residual'
    else:
        vres = res.resid
        ylabstr = 'Residual'
    residlim = max(np.abs(vres))
    for idx, xvresid in enumerate(xvresidlist):
        fig, ax = plt.subplots()
        if idx == 0 :
            prediction_res = res.get_prediction(transform = True)
            res_frame= prediction_res.summary_frame(alpha = 0.05)            
            sb.scatterplot(ax=ax, x = res_frame['mean'], y = vres, color = 'blue', s = dsize)
            plt.xlabel('Predicted ' + res.model.endog_names)
        else:
            sb.scatterplot(ax=ax, x = res.model.exog[:,idx], y = vres, color = 'blue', s = dsize) 
            plt.xlabel(xvresid)
        plt.axhline(y=0, color='black', linestyle='-')
        plt.ylim((-residlim, residlim))
        plt.ylabel(ylabstr)

        plt.title(tstr)
        fig.show()  #show the plots simultaneously
        #plt.show() #show plots one at a time
    return

#############################
#############################
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
            messagebox.showerror(' ',"I can only graph models with one or two independent variables.")    
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
                colorD, colorlist ,lpatches= grp.getcolor(cv,list(colordat))
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

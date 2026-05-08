            #SSstr1 =  f"SSE = {round(mdl().ssr,5)}, SSR={round(mdl().ess,5)}, SST = {round(mdl().ssr + mdl().ess,5)}" 
            #SSstr2 = f"MSE = {round(mdl().mse_resid,5)}, MSR ={round(mdl().mse_model,5)}, MST = {round(mdl().mse_total,5)} "   
            SSstr = SSstr0 + "\n" + "Model: " + input.stringM() + "\n\n" + str( mdl().summary()) + "\n"
            SSstr = SSstr + SSstr0 + '\n' + 'Analysis of Variance' + "\n"
            anova_rep = sm.stats.anova_lm(mdl(),typ=1)          
            row1 = pd.Series({'df': mdl().df_model, 'sum_sq': mdl().ess,'mean_sq': mdl().mse_model,'F': ' ','PR(>F)':' '},name = 'Regression')
            row2 = pd.Series({'df': mdl().df_resid + mdl().df_model, 'sum_sq': mdl().ess + mdl().ssr,'mean_sq': mdl().mse_total, 'F': ' ','PR(>F)':' '},name = 'Total')
            anova_rep.loc['Regression'] = row1
            anova_rep.loc['Total'] = row2
            anova_rep.replace(np.nan," ")
            SSstr = SSstr + str(anova_rep[anova_rep.columns[0:len(anova_rep.columns)-2]][-3:]) + '\n' + SSstr0

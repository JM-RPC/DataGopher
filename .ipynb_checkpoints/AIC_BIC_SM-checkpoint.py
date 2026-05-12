import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.genmod.generalized_linear_model import SET_USE_BIC_LLF
SET_USE_BIC_LLF(True) 
import numpy as np
import pandas as pd

x = [[1, 0], [1, 1], [1, 2], [1, 3], [1, 4], [1,5], [1,6], [1,7], [1,8]]
y = [[0], [49], [101], [149], [201], [220], [240], [257], [290]]

x2 = [item[1] for item in x[:]]
y2 = [item[0] for item in y]

df = pd.DataFrame({'x':x2,'y':y2})
df.to_csv("AIC_BIC_ols_data.csv")

res = sm.OLS(y, x).fit()


# Façon 1
res.aic # gives 
print(f" From OLS matrix api: AIC={res.aic}")

# Façon 2 
llf = res.llf # log-like value
k = 2
aic = -2*llf + 2 * k # gives 

bic = np.log(9)*k - 2*llf
print(f"By hand: AIC = {aic}, BIC = {bic}, Log Likelihood = {llf}, \n From results:#obs = {res.nobs}, model df= {res.df_model}")
print(res.summary().tables[0])

zstring = "\n\n==============================================================================\n"
zstring += "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@Formula API@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
zstring += "==============================================================================\n"

#Basic model structure
#model = smf.ols(formula='dependent_var ~ independent_var1 + independent_var2', data=df)
#results = model.fit()

resf = smf.ols(formula='y ~ x',data=df).fit()
print(zstring)
k = resf.df_model + 1
nbs = resf.nobs
#aic = -2*llf + 2 * k 
llf = res.llf 
aic = -2*llf + 2 * (res.df_model +1)
bic = np.log(resf.nobs)*k - 2*llf
print(f"By hand: AIC = {aic}, BIC = {bic}, Log Likelihood = {llf} \n From results: #obs= {resf.nobs}, dfmodel= {resf.df_model}")
print(resf.summary().tables[0])
#print(resf.summary())

zstring = "\n\n==============================================================================\n"
zstring += "@@@@@@@@@@@@@@@@@@@@@@@@@@@GLM Logit Formula API@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
zstring += "==================================================================================\n"

df['y'] = [0,0,0,1,0,1,0,1,1]
df.to_csv("AIC_BIC_Logit_data.csv")

reslf = smf.glm(formula='y ~ x',data=df, family=sm.families.Binomial(link=sm.families.links.Logit())).fit()
print(zstring)
k = reslf.df_model + 1
nbs = reslf.nobs
#aic = -2*llf + 2 * k 
llf = reslf.llf 
aic = -2*llf + 2 * (reslf.df_model +1)
bic = np.log(reslf.nobs)*k - 2*llf
print(f"By hand: AIC = {aic}, BIC = {bic}, Log Likelihood = {llf} \nFrom Results: AIC = {reslf.aic}, BIC = {reslf.bic}\n  #obs= {reslf.nobs}, dfmodel= {reslf.df_model}")
print(reslf.summary().tables[0])

print("Resetting BIC calculation.")
SET_USE_BIC_LLF(False) 
reslf2 = smf.glm(formula='y ~ x',data=df, family=sm.families.Binomial(link=sm.families.links.Logit())).fit()
llf = reslf.llf 
aic = -2*llf + 2 * (reslf.df_model +1)
bic = np.log(reslf.nobs)*k - 2*llf
print(f"By hand: AIC = {aic}, BIC = {bic}, Log Likelihood = {llf} \nFrom Results: AIC = {reslf.aic}, BIC = {reslf.bic}\n  #obs= {reslf.nobs}, dfmodel= {reslf.df_model}")
print(reslf.summary().tables[0])

#print(reslf.summary())

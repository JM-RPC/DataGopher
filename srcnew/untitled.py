import statsmodels.api as sm
import statsmodels.formula.api as smf
import pandas as pd
import numpy as np

# Sample Data: proportion of success (successes / trials)
data = pd.DataFrame({'successes': [10, 20, 30, 40],'trials': [50, 50, 50, 50],'predictor': [1, 2, 3, 4]})
data['proportion'] = data['successes'] / data['trials']

# Define endogenous variable (y) as [successes, failures]
y = np.column_stack((data['successes'], data['trials'] - data['successes']))

# Fit GLM with Binomial family
X = sm.add_constant(data['predictor'])
model = sm.GLM(y, X, family=sm.families.Binomial())
result = model.fit()

result.summary()
data
res = smf.glm("proportion ~ predictor", data).fit()
res.summary()

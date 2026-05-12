x = [[1, 0], [1, 1], [1, 2], [1, 3], [1, 4]]
y = [[0], [49], [101], [149], [201]]

res = sm.OLS(y, x).fit()

# Façon 1
res.aic # gives 16.5468

# Façon 2 
llf = res.llf # log-like value
k = 2
aic = -2*llf + 2 * k # gives 16.5468
#bic = ln(𝑛)𝑘−2ln(𝐿)
bic = 
  
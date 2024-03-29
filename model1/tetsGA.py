import numpy as np
from geneticalgorithm import geneticalgorithm as ga

def f(X):
    return np.sum(X)


varbound=np.array([[0,10]]*3)
print(varbound.shape)
model=ga(function=f,dimension=3,variable_type='real',variable_boundaries=varbound,convergence_curve=False)

model.run()
print(model.best_variable)
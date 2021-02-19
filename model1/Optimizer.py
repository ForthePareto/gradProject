import numpy as np
from geneticalgorithm import geneticalgorithm as ga
# docs: https://pypi.org/project/geneticalgorithm/
from fiveCompModel import FiveCompModel


class ModelOptimizer:
    def __init__(self, model):
        self.model = model
        self.experimental_data = model.get_exprimental_data() #done
        self.parameters_boundaries = model.get_parameters_boundaries() #done
        self.best_solution = None
        self.best_score = None

    def cost(self, params):
        """Cost using euclidean distance, parameter set are fed to the Cellmodel then cell measurments are done to be compared with model exprimental measurements.
        """
        #passing a solution of parameters to the cell model
        # print(params.shape)
        
        self.model.setCellParams(params) 
        #getting measurement of model after parameter modification to be evaluated
        measurements = self.model.get_measurements() #TODO

        norm_cost = np.linalg.norm(self.experimental_data - measurements)
        return norm_cost

    def optimize(self):
        algorithm_param = {'max_num_iteration': None,  
                   'population_size':5,\
                   'mutation_probability':0.1,\
                   'elit_ratio': 0.01,\
                   'crossover_probability': 0.5,\
                   'parents_portion': 0.3,\
                   'crossover_type':'uniform',\
                   'max_iteration_without_improv':None} 
        vartype =np.concatenate(
            (np.array([['real']]*7), np.array([['int']]*11)))

        
        GA_Optizimer = ga(function=self.cost,algorithm_parameters=algorithm_param, dimension=len(self.parameters_boundaries),
        variable_type_mixed=vartype, variable_boundaries=self.parameters_boundaries, convergence_curve=False)
        GA_Optizimer.run()
        self.best_solution = GA_Optizimer.best_variable
        self.best_score = GA_Optizimer.best_function


if __name__ == '__main__':
    cell_model = FiveCompModel()
    optimizer = ModelOptimizer(cell_model)
    optimizer.optimize()

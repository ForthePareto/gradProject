from sbi.inference.base import infer
import torch
from sbi import utils as utils
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from geneticalgorithm import geneticalgorithm as ga
# docs: https://pypi.org/project/geneticalgorithm/
from fiveCompModel import FiveCompModel


class ModelOptimizer:
    def __init__(self, model):
        self.model = model
        self.experimental_data = model.get_exprimental_data()  # done
        self.parameters_boundaries = model.get_parameters_boundaries()  # done
        self.best_solution = None
        self.best_score = None

    def cost(self, params):
        """Cost using euclidean distance, parameter set are fed to the Cellmodel then cell measurments are done to be compared with model exprimental measurements.
        """
        # passing a solution of parameters to the cell model
        try:
            self.model.setCellParams(params)
            # getting measurement of model after parameter modification to be evaluated
            measurements = self.model.get_measurements()
            # norm_cost = np.linalg.norm(self.experimental_data - measurements)
            norm_cost = np.linalg.norm(np.divide(
                (self.experimental_data - measurements), np.abs(self.experimental_data)))
        except (IndexError, ValueError):
            norm_cost = 100000

        # print(norm_cost)
        return norm_cost

    def optimize(self):
        algorithm_param = {'max_num_iteration': None,
                           'population_size': 100,
                           'mutation_probability': 0.1,
                           'elit_ratio': 0.2,
                           'crossover_probability': 0.5,
                           'parents_portion': 0.3,
                           'crossover_type': 'uniform',
                           'max_iteration_without_improv': None}
        vartype = np.array([['real']]*15)
        # vartype = np.array([['int']]*12)
        # vartype =np.concatenate(
        #     (np.array([['real']]*10), np.array([['int']]*8)))

        GA_Optizimer = ga(function=self.cost, algorithm_parameters=algorithm_param, dimension=len(self.parameters_boundaries),
                          variable_type_mixed=vartype, variable_boundaries=self.parameters_boundaries, function_timeout=40, convergence_curve=True)
        GA_Optizimer.run()
        self.best_solution = GA_Optizimer.best_variable
        self.best_score = GA_Optizimer.best_function


# visualization

# sbi


class SbiOptimizer:
    def __init__(self, model):
        self.model = model
        self.experimental_data = model.get_exprimental_data()  # done
        self.parameters_boundaries = model.get_parameters_boundaries()  # done
        self.prior = None
        self.init_prior(self.parameters_boundaries)
        self.best_solution = None
        self.best_score = None

    def init_prior(self, bounds):
        self.prior = utils.torchutils.BoxUniform(low=torch.as_tensor(bounds[:, 0]),
                                                 high=torch.as_tensor(bounds[:, 1]))

    def simulation_wrapper(self,params):
        """
        Returns summary statistics from conductance values in `params`.

        Summarizes the output of the HH simulator and converts it to `torch.Tensor`.
        """
        self.model.setCellParams(params)
        # getting measurement of model after parameter modification to be evaluated
        measurements = self.model.get_measurements()
        summstats = torch.as_tensor(measurements)
        return summstats
    def optimize(self,n_simulations=150,n_cores=1):
        posterior = infer(self.simulation_wrapper, self.prior, method='SNPE', 
                  num_simulations=n_simulations, num_workers=n_cores)
        posterior_sample = posterior.sample((1,), 
                                    x=self.experimental_data).numpy()
        print(posterior_sample)

if __name__ == '__main__':
    cell_model = FiveCompModel()
    # cell_model.setCellParams(np.random.rand(18,1))
    # cell_model.get_measurements()
    # cell_model.setCellParams(np.random.rand(18,1))
    # cell_model.get_measurements()
    # optimizer = ModelOptimizer(cell_model)
    # optimizer.optimize()
    optimizer = SbiOptimizer(cell_model)
    optimizer.optimize()

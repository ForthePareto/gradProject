from sbi.inference.base import infer
import torch
from sbi import utils as utils
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from geneticalgorithm import geneticalgorithm as ga
# docs: https://pypi.org/project/geneticalgorithm/
from fiveCompModel import FiveCompModel

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

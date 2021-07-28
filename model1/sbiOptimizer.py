from sbi.inference.base import infer
import torch
from sbi import utils as utils
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from geneticalgorithm import geneticalgorithm as ga
# docs: https://pypi.org/project/geneticalgorithm/
from fiveCompModel import FiveCompModel

import torch
import sbi
from sbi.inference import SNPE, prepare_for_sbi, simulate_for_sbi
from sbi.utils.get_nn_models import posterior_nn
from sbi import utils as utils
from sbi import analysis as analysis

class SbiOptimizer:
    def __init__(self, model):
        self.model = model
        self.experimental_data = model.get_exprimental_data()  # done
        self.parameters_boundaries = model.get_parameters_boundaries()[:6,:]  # done
        print(self.parameters_boundaries)
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
        self.model.setNonPassiveParams(params)
        # getting measurement of model after parameter modification to be evaluated
        measurements = self.model.get_EFEL_measurements(["AP_amplitude","AP_height",'AP_width','AHP_depth_abs',"AHP_time_from_peak"])
        summstats = torch.as_tensor(measurements)
        return summstats
    def optimize(self,n_simulations=10000,n_cores=1):
        posterior = infer(self.simulation_wrapper, self.prior, method='SNPE', 
                  num_simulations=n_simulations, num_workers=n_cores)
        posterior_sample = posterior.sample((1,), 
                                    x=self.experimental_data).numpy()
        print(posterior_sample)
    def optimize_multiRound(self,n_simulations=500,n_cores=1):
        # 2 rounds: first round simulates from the prior, second round simulates parameter set 
        # that were sampled from the obtained posterior.
        num_rounds = 2
        # The specific observation we want to focus the inference on.
        x_o = self.experimental_data
        simulator, prior = prepare_for_sbi(self.simulation_wrapper, self.prior)
        inference = SNPE(prior=prior)
        posteriors = []
        proposal = self.prior

        for _ in range(num_rounds):
            theta, x = simulate_for_sbi(simulator, proposal, num_simulations=5000)
            
            # In `SNLE` and `SNRE`, you should not pass the `proposal` to `.append_simulations()`
            density_estimator = inference.append_simulations(theta, x, proposal=proposal).train()
            posterior = inference.build_posterior(density_estimator,sample_with_mcmc=True)
            posteriors.append(posterior)
            proposal = posterior.set_default_x(x_o)
        print(posteriors[-1].sample((10,), 
                                    x=self.experimental_data).numpy())
        print("********************************")
        print(list(posteriors[-1].sample((1,), 
                                    x=self.experimental_data).numpy()))
if __name__ == '__main__':
    cell_model = FiveCompModel()
    # cell_model.setCellParams(np.random.rand(18,1))
    # cell_model.get_measurements()
    # cell_model.setCellParams(np.random.rand(18,1))
    # cell_model.get_measurements()
    # optimizer = ModelOptimizer(cell_model)
    # optimizer.optimize()
    optimizer = SbiOptimizer(cell_model)
    # optimizer.optimize()
    optimizer.optimize_multiRound()

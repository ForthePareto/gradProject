import numpy as np
from geneticalgorithm import geneticalgorithm as ga
# docs: https://pypi.org/project/geneticalgorithm/
from fiveCompModel import FiveCompModel


class ModelOptimizer:
    def __init__(self, model):
        self.model = model
        self.experimental_data = model.get_experimental_data()
        self.parameters_boundaries = model.get_parameters_boundaries()
        self.best_solution = None
        self.best_score = None

    def cost(self, params):
        """Cost using euclidean distance, parameter set are fed to the Cellmodel then cell measurments are done to be compared with model exprimental measurements.
        """
        self.model.setSomaParams(*params)
        measurements = self.model.get_measurements()

        norm_cost = np.linalg.norm(self.experimental_data - measurements)
        return norm_cost

    def optimize(self):
        GA_Optizimer = ga(function=self.cost, dimension=len(self.experimental_data),
                   variable_type='real', variable_boundaries=self.parameters_boundaries, convergence_curve=False)

        GA_Optizimer.run()
        self.best_solution = GA_Optizimer.best_variable
        self.best_score = GA_Optizimer.best_function


if __name__ == '__main__':
    cell_model = FiveCompModel()
    optimizer = ModelOptimizer(cell_model)

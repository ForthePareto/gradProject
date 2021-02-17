import numpy as np
from geneticalgorithm import geneticalgorithm as ga
# docs: https://pypi.org/project/geneticalgorithm/
from fiveCompModel import FiveCompModel


class ModelOptimizer:
    def __init__(self, model):
        self.model = model
        self.experimental_data = model.experimental_data
        self.experimental_data_boundaries = model.experimental_data_boundaries
        self.best_solution = None
        self.best_score = None

    def cost(self, params):
        """Cost using euclidean distance, parameter set are fed to the Cellmodel then cell measurments are done to be compared with model exprimental measurements.
        """
        self.setSomaParams(*params)

        norm_cost = np.linalg.norm(self.experimental_data - params)

    def optimize(self):
        model = ga(function=self.cost, dimension=len(self.experimental_data),
                   variable_type='real', variable_boundaries=self.experimental_data_boundaries, convergence_curve=False)

        model.run()
        self.best_solution = model.best_variable
        self.best_score = model.best_function


if __name__ == '__main__':
    cell_model = FiveCompModel()
    optimizer = ModelOptimizer(cell_model)

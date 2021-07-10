import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import functools
import deap
import deap.gp
import deap.benchmarks
from deap import base
from deap import creator
from deap import tools
from deap import algorithms
import Selector
from fiveCompModel import FiveCompModel
from algorithms import eaAlphaMuPlusLambdaCheckpoint, WSListIndividual
np.random.seed(1)
from datetime import datetime


class Nsga2Optimizer:
    def __init__(self, model):
        self.model = model
        self.experimental_data = model.get_exprimental_data()  # done
        self.parameters_boundaries = model.get_parameters_boundaries()  # done
        self.best_solution = None
        self.best_score = None

    def evaluate(self, params):
        """Cost using euclidean distance, parameter set are fed to the Cellmodel then cell measurments are done to be compared with model exprimental measurements.
        """
        # passing a solution of parameters to the cell model
        # print(params.shape)
        # print(params)
        parameters = np.copy(params)
        self.model.setPassiveParams(parameters)
        try:
            measurements = self.model.get_passive_measurements()
            # input Resistance
            cost1 = abs(measurements[0]-self.experimental_data[0])
            # time constant
            cost2 = abs(measurements[1]-self.experimental_data[-1])
            # getting measurement of model after parameter modification to be evaluated
            # norm_cost = np.linalg.norm(self.experimental_data - measurements)

        except (IndexError, ValueError):
            cost1 = 1000
            cost2 = 1000
        # print(cost1, cost2)
        # params.Rin = measurements[0]
        # params.tau = measurements[1]
        # params.target_voltage1 = self.experimental_data[0]
        # params.target_voltage2 = self.experimental_data[-1]

        params.tot_fitness = cost1 + cost2
        return cost1, cost2

    def ErrorVectorNonPassive(self, params):
        """Cost using euclidean distance, parameter set are fed to the Cellmodel then cell measurments are done to be compared with model exprimental measurements.
        """
        # passing a solution of parameters to the cell model
        # print(params.shape)
        # print(params)
        try:
            self.model.setCellParams(params)
            # getting measurement of model after parameter modification to be evaluated
            measurements = self.model.get_AP_measurements()
            # print("measurements.shape", measurements.shape)
            error = np.abs(
                (self.experimental_data[1:-2] - measurements))/np.abs(self.experimental_data[1:-2])
            # print("measurements.shape", error.shape)
        except (IndexError, ValueError):
            print("Error in measurement")
            error = np.array([1000]*len(self.experimental_data[1:-2]))
        # self.model.setCellParams(params)
        # #getting measurement of model after parameter modification to be evaluated
        # measurements = self.model.get_AP_measurements()
        # print(measurements.shape)
        # error = np.abs((self.experimental_data[1:-2] - measurements))/np.abs(self.experimental_data[1:-2])
        return list(error)

    def optimize(self, population_size=10, offspring_size=10, n_generations=100, plot=False):
        # Population size
        POP_SIZE = population_size
        # Number of offspring in every generation
        OFFSPRING_SIZE = offspring_size

        # Number of generations
        NGEN = n_generations

        # The parent and offspring population size are set the same
        MU = OFFSPRING_SIZE
        LAMBDA = OFFSPRING_SIZE
        # ALPHA = POP_SIZE

        # Crossover probability
        CXPB = 0.7
        # Mutation probability, should sum to one together with CXPB
        MUTPB = 0.3

        # Eta parameter of cx and mut operators
        ETA = 10.0
        SELECTOR = "NSGA2"

        IND_SIZE = len(self.parameters_boundaries[:, 0])

        # LOWER = [0.0]
        # UPPER = [1.0]
        LOWER = list(self.parameters_boundaries[:, 0])
        UPPER = list(self.parameters_boundaries[:, 1])
        OBJ_SIZE = 7
        creator.create("Fitness", base.Fitness, weights=[-1.0] * OBJ_SIZE)
        creator.create("Individual", list, fitness=creator.Fitness)

        self.toolbox = base.Toolbox()
        self.toolbox.register("uniformparams", uniform, LOWER, UPPER, IND_SIZE)
        # self.toolbox.register("Individual",
        #                deap.tools.initIterate,
        #                functools.partial(WSListIndividual, obj_size=OBJ_SIZE),
        #                self.toolbox.uniformparams)

        self.toolbox.register(
            "Individual",
            tools.initIterate,
            creator.Individual,
            self.toolbox.uniformparams)
        self.toolbox.register(
            "population",
            deap.tools.initRepeat,
            list,
            self.toolbox.Individual)

        self.toolbox.register("evaluate", self.ErrorVectorNonPassive)

        self.toolbox.register(
            "mate",
            deap.tools.cxSimulatedBinaryBounded,
            eta=ETA,
            low=LOWER,
            up=UPPER)
        self.toolbox.register("mutate", deap.tools.mutPolynomialBounded, eta=ETA,
                              low=LOWER, up=UPPER, indpb=0.1)

        self.toolbox.register("variate", deap.algorithms.varAnd)

        if not plot:
            # self.toolbox.register(
            #     "select",
            #     tools.selNSGA2)
            self.toolbox.register(
                "select",
                tools.selNSGA2)
        else:
            # self.toolbox.register(
            #     "select",
            #     plot_selector, selector=tools.selNSGA2)
            self.toolbox.register(
                "select",
                plot_selector, selector=tools.selNSGA2)

        pop = self.toolbox.population(n=MU)

        first_stats = tools.Statistics(key=lambda ind: ind.fitness.values[0])
        second_stats = tools.Statistics(key=lambda ind: ind.fitness.values[1])
        third_stats = tools.Statistics(key=lambda ind: ind.fitness.values[2])
        fourth_stats = tools.Statistics(key=lambda ind: ind.fitness.values[3])
        fifth_stats = tools.Statistics(key=lambda ind: ind.fitness.values[4])
        sixth_stats = tools.Statistics(key=lambda ind: ind.fitness.values[5])
        seventh_stats = tools.Statistics(key=lambda ind: ind.fitness.values[6])
        stats = tools.MultiStatistics(APHeight=first_stats, APWidth=second_stats, AHPDepth=third_stats, AHPDuration=fourth_stats,
                                      AHPHalfDuration=fifth_stats, AHPHalfDecay=sixth_stats, AHPRisingTime=seventh_stats)
        stats.register("min_error", np.min, axis=0)

        # stats = deap.tools.Statistics(key=lambda ind: ind.fitness.values[0])
        # stats.register("avg", np.mean)
        # stats.register("std", np.std)
        # stats.register("min", np.min)
        # stats.register("max", np.max)
        pop, logbook = algorithms.eaMuPlusLambda(
            pop,
            self.toolbox,
            MU,
            LAMBDA,
            CXPB,
            MUTPB,
            NGEN,
            stats,
            halloffame=None)
        self.pop, self.logbook = pop, logbook
        return pop, logbook




def uniform(lower_list, upper_list, dimensions):
    """Fill array from uniform distribution  """

    if hasattr(lower_list, '__iter__'):
        return [np.random.uniform(lower, upper) for lower, upper in
                zip(lower_list, upper_list)]
    else:
        return [np.random.uniform(lower_list, upper_list)
                for _ in range(dimensions)]


if __name__ == '__main__':
    cell_model = FiveCompModel()
    
    print("start Time =",  datetime.now().strftime("%H:%M:%S"))
    optimizer = Nsga2Optimizer(cell_model)
    pop, logbook = optimizer.optimize(
        population_size=100, offspring_size=100, n_generations=50)
    print(pop)
    print(logbook)
    print("end Time =",  datetime.now().strftime("%H:%M:%S"))


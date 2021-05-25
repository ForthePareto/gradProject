import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import deap
import deap.gp
import deap.benchmarks
from deap import base
from deap import creator
from deap import tools
from deap import algorithms
from fiveCompModel import FiveCompModel

np.random.seed(1)


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

    def optimize(self, population_size=100, offspring_size=100, n_generations=300,plot=False):
        # Population size
        POP_SIZE = population_size
        # Number of offspring in every generation
        OFFSPRING_SIZE = offspring_size

        # Number of generations
        NGEN = n_generations

        # The parent and offspring population size are set the same
        MU = OFFSPRING_SIZE
        LAMBDA = OFFSPRING_SIZE
        # Crossover probability
        CXPB = 0.7
        # Mutation probability, should sum to one together with CXPB
        MUTPB = 0.3

        # Eta parameter of cx and mut operators
        ETA = 10.0
        SELECTOR = "NSGA2"

        IND_SIZE = 1
        LOWER = [0.0]
        UPPER = [1.0]

        creator.create("Fitness", base.Fitness, weights=[-1.0] * 2)
        creator.create("Individual", Individual, fitness=creator.Fitness)

        self.toolbox = base.Toolbox()
        self.toolbox.register("uniformparams", uniform, LOWER, UPPER, IND_SIZE)
        self.toolbox.register(
            "Individual",
            tools.initIterate,
            creator.Individual,
            self.toolbox.uniformparams)
        self.toolbox.register("population", tools.initRepeat,
                              list, self.toolbox.Individual)

        self.toolbox.register("evaluate", self.evaluate)

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
            self.toolbox.register(
                "select",
                tools.selNSGA2)
        else:
            self.toolbox.register(
                "select",
                plot_selector, selector=tools.selNSGA2)

        pop = self.toolbox.population(n=MU)

        first_stats = tools.Statistics(key=lambda ind: ind.fitness.values[0])
        second_stats = tools.Statistics(key=lambda ind: ind.fitness.values[1])
        stats = tools.MultiStatistics(R_in=first_stats, tau=second_stats)
        stats.register("min", np.min, axis=0)
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


class Individual(list):
    def __init__(self, *args):
        list.__init__(self, *args)
        self.Rin = None
        self.tau = None


def plot_selector(population, k, selector=None, **kwargs):

    import operator
    best_ind = min(population, key=operator.attrgetter("tot_fitness"))
    fig,ax = plt.subplots(figsize=(12,8)) 
    for ind in population:
        ax.plot([ind.fitness.values[0]], [ind.fitness.values[1]],
                'o', color='grey', alpha=0.2, markersize=6)
    ax.plot([best_ind.fitness.values[0]], [
            best_ind.fitness.values[1]], 'o', color='red', markersize=8)
    plt.xlim([0.00, 3.5])
    plt.ylim([0, 5.0])
    plt.xlabel("Input Resistance error")
    plt.ylabel("Time Constant error")

    # plt.clear()
    # plt.draw()
    # plt.display(plt.gcf())
    # plt.pause(0.5)
    plt.box(True)
    plt.show()
    selected_pop = selector(population, k, **kwargs)

    return selected_pop


def uniform(lower_list, upper_list, dimensions):
    """Fill array """

    if hasattr(lower_list, '__iter__'):
        return [np.random.uniform(lower, upper) for lower, upper in
                zip(lower_list, upper_list)]
    else:
        return [np.random.uniform(lower_list, upper_list)
                for _ in range(dimensions)]


if __name__ == '__main__':
    cell_model = FiveCompModel()
    optimizer = Nsga2Optimizer(cell_model)
    pop, logbook = optimizer.optimize(
        population_size=100, offspring_size=100, n_generations=10)

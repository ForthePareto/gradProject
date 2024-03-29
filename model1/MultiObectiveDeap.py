from datetime import datetime
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

N = 0

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
        # global N
        # print(N)
        # N  += 1
        # passing a solution of parameters to the cell model
        self.model.setNonPassiveParams(params)
        # getting measurement of model after parameter modification to be evaluated
        measurements = self.model.get_EFEL_measurements(["Spikecount","time_to_first_spike","AP_amplitude","AP_height",'AP_width','AHP_depth_abs',"AHP_time_from_peak"])
        # self.model.model.graphVolt(self.model.volt, self.model.t, "trace").show()

        params.measurements = measurements
        # print("measurements.shape", measurements.shape)
        error = np.abs(
            (self.experimental_data - measurements))/np.abs(self.experimental_data)
        # try:
        #     self.model.setNonPassiveParams(params)
        #     # getting measurement of model after parameter modification to be evaluated
        #     measurements = self.model.get_EFEL_measurements(["Spikecount","time_to_first_spike","AP_amplitude","AP_height",'AP_width','AHP_depth_abs',"AHP_time_from_peak"])
        #     # self.model.model.graphVolt(self.model.volt, self.model.t, "trace").show()

        #     params.measurements = measurements
        #     # print("measurements.shape", measurements.shape)
        #     error = np.abs(
        #         (self.experimental_data - measurements))/np.abs(self.experimental_data)
        #     # error = np.abs(
        #     #     (self.experimental_data[1:-2] - measurements))/np.abs(self.experimental_data[1:-2])
        #     # print("measurements.shape", error.shape)
        # except (IndexError, ValueError):
        #     print("Error in measurement")
        #     error = np.array([1000]*len(self.experimental_data))
        #     # error = np.array([1000]*len(self.experimental_data[1:-2]))
        # error =list(range(1,8))
        params.measurements_error = error
        params.total_indivedual_error = sum(list(error))
        # print(error)
        # self.model.setCellParams(params)
        # # getting measurement of model after parameter modification to be evaluated
        # measurements = self.model.get_AP_measurements()
        # print(measurements.shape)
        # error = np.abs(
        #     (self.experimental_data[1:-2] - measurements))/np.abs(self.experimental_data[1:-2])
       
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
        OBJ_SIZE = len(self.experimental_data)
        weights = [-1.0]* OBJ_SIZE
        # weights[0] = -2.0
        creator.create("Fitness", base.Fitness, weights=weights)
        creator.create("Individual", Individual, fitness=creator.Fitness)

        self.toolbox = base.Toolbox()
        self.toolbox.register("uniformparams", uniform, LOWER, UPPER, IND_SIZE)
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

        # first_stats = tools.Statistics(key=lambda ind: ind.fitness.values[0])
        # second_stats = tools.Statistics(key=lambda ind: ind.fitness.values[1])
        # third_stats = tools.Statistics(key=lambda ind: ind.fitness.values[2])
        # fourth_stats = tools.Statistics(key=lambda ind: ind.fitness.values[3])
        # fifth_stats = tools.Statistics(key=lambda ind: ind.fitness.values[4])
        # sixth_stats = tools.Statistics(key=lambda ind: ind.fitness.values[5])
        # seventh_stats = tools.Statistics(key=lambda ind: ind.fitness.values[6])
        # # eighth_stats = tools.Statistics(key=lambda ind: ind.fitness.values[6])
        # stats = tools.MultiStatistics(APHeight=first_stats, APWidth=second_stats, AHPDepth=third_stats, AHPDuration=fourth_stats,
        #                               AHPHalfDuration=fifth_stats, AHPHalfDecay=sixth_stats, AHPRisingTime=seventh_stats)
        print(list(range(OBJ_SIZE)))
        
        # print(stats_list)
        first_stats = tools.Statistics(key=lambda ind: ind.fitness.values[0])
        second_stats = tools.Statistics(key=lambda ind: ind.fitness.values[1])
        third_stats = tools.Statistics(key=lambda ind: ind.fitness.values[2])
        fourth_stats = tools.Statistics(key=lambda ind: ind.fitness.values[3])
        fifth_stats = tools.Statistics(key=lambda ind: ind.fitness.values[4])
        sixth_stats = tools.Statistics(key=lambda ind: ind.fitness.values[5])
        seventh_stats = tools.Statistics(key=lambda ind: ind.fitness.values[6])
       
       
        # stats_list = [tools.Statistics(key=lambda ind: ind.fitness.values[i]) for i in range(OBJ_SIZE)]
        # stats_dict = dict(zip(self.model.EXPRIMENTAL_DATA[:,0],stats_list))
        # stats = tools.MultiStatistics(**stats_dict)

        # print(stats_dict)
        # print(stats_dict)
        stats = tools.MultiStatistics( Spikecount= first_stats,time_to_first_spike=second_stats,AP_amplitude=third_stats,AP_height=fourth_stats,
         APWidth=fifth_stats, AHP_depth_abs=sixth_stats, AHP_time_from_peak=seventh_stats)
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
class Individual(list):
    def __init__(self, *args):
        list.__init__(self, *args)
        self.measurements = None
        self.measurements_error = None
        self.total_indivedual_error = None

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
    # optimizer.model.setCellParams([0.3948756129235549, 0.9619749870565372, 0.17395335917101354, 0.12632951986691587, 0.6289123625480996, 0.5056621656768967, 0.02153343813138551, 0.8726109184518372, 1.3762639508579921, 0.018678269380864344, 0.09425770246331389, 0.3549523492569816, 0.5358401544817353, 0.5594844045368456, 0.34114602413479655])
    # #getting measurement of model after parameter modification to be evaluated
    # measurements = optimizer.model.get_AP_measurements()
    # print(optimizer.ErrorVectorNonPassive([0.3948756129235549, 0.9619749870565372, 0.17395335917101354, 0.12632951986691587, 0.6289123625480996, 0.5056621656768967, 0.02153343813138551, 0.8726109184518372, 1.3762639508579921, 0.018678269380864344, 0.09425770246331389, 0.3549523492569816, 0.5358401544817353, 0.5594844045368456, 0.34114602413479655]))
    pop, logbook = optimizer.optimize(
        population_size=150, offspring_size=150, n_generations=60)
    # print(pop)
    # print(logbook)
    i =  0
    pop.sort(key=lambda ind: ind.total_indivedual_error)
    for ind in pop:
        print(ind)
        print(f"individual {i} Total error =  {ind.total_indivedual_error}" )
        i+=1
        # print(ind.total_indivedual_error)
    errors = map(lambda ind: ind.total_indivedual_error, pop)
    best_sol_idx = np.argmin(errors)
    print("best solution is   ",pop[best_sol_idx], )
    print("with errors :   ",list( map(lambda ind: ind.measurements_error, pop))[best_sol_idx], )
    print(f"with total error {list(errors)[best_sol_idx]}")
    # print("end Time =",  datetime.now().strftime("%H:%M:%S"))

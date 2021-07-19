from datetime import datetime
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
from scoop import futures
from neuron import h
import multiprocessing

np.random.seed(1)

N = 0


class Individ(list):
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
def ErrorVectorNonPassive( params):
        """Cost using euclidean distance, parameter set are fed to the Cellmodel then cell measurments are done to be compared with model exprimental measurements.
        """
        # global N
        # print(N)
        # N  += 1
        # passing a solution of parameters to the cell model
        model = FiveCompModel()
        model.setNonPassiveParams(params)
        # getting measurement of model after parameter modification to be evaluated
        measurements = model.get_EFEL_measurements(["Spikecount","time_to_first_spike","AP_amplitude","AP_height",'AP_width','AHP_depth_abs',"AHP_time_from_peak"])
        # self.model.model.graphVolt(self.model.volt, self.model.t, "trace").show()

        params.measurements = measurements
        # print("measurements.shape", measurements.shape)
        experimental_data = np.copy(model.get_exprimental_data())  # done
        # parameters_boundaries = np.copy(model.get_parameters_boundaries())  # done
        error = np.abs(
            (experimental_data - measurements))/np.abs(experimental_data)
        
        params.measurements_error = error
        params.total_indivedual_error = sum(list(error))
        
        return list(error)
model = FiveCompModel()
experimental_data = np.copy(model.get_exprimental_data())  # done
parameters_boundaries = np.copy(model.get_parameters_boundaries())  # done

del model
best_solution = None
best_score = None



POP_SIZE = 160
# Number of offspring in every generation
OFFSPRING_SIZE = 160

# Number of generations
NGEN = 85

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

IND_SIZE = len(parameters_boundaries[:, 0][0:6])

# LOWER = [0.0]
# UPPER = [1.0]
LOWER = list(parameters_boundaries[:, 0][0:6])
UPPER = list(parameters_boundaries[:, 1][0:6])
OBJ_SIZE = len(experimental_data)
weights = [-1.0]* OBJ_SIZE
# weights[0] = -2.0
creator.create("Fitness", base.Fitness, weights=weights)
creator.create("Individual", Individ, fitness=creator.Fitness)
toolbox = base.Toolbox()
toolbox.register("uniformparams", uniform, LOWER, UPPER, IND_SIZE)
toolbox.register(
    "Individual",
    tools.initIterate,
    creator.Individual,
    toolbox.uniformparams)
toolbox.register(
    "population",
    deap.tools.initRepeat,
    list,
    toolbox.Individual)

toolbox.register("evaluate", ErrorVectorNonPassive)

toolbox.register(
    "mate",
    deap.tools.cxSimulatedBinaryBounded,
    eta=ETA,
    low=LOWER,
    up=UPPER)
toolbox.register("mutate", deap.tools.mutPolynomialBounded, eta=ETA,
                        low=LOWER, up=UPPER, indpb=0.1)

toolbox.register("variate", deap.algorithms.varAnd)
toolbox.register("map", futures.map)
hof = tools.HallOfFame(3)
# pool = multiprocessing.Pool()
# toolbox.register("map", pool.map)
plot = False
if not plot:
    # toolbox.register(
    #     "select",
    #     tools.selNSGA2)
    toolbox.register(
        "select",
        tools.selNSGA2)
else:
    # toolbox.register(
    #     "select",
    #     plot_selector, selector=tools.selNSGA2)
    toolbox.register(
        "select",
        plot_selector, selector=tools.selNSGA2)

    
    
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
# h.quit()
# stats = deap.tools.Statistics(key=lambda ind: ind.fitness.values[0])
# stats.register("avg", np.mean)
# stats.register("std", np.std)
# stats.register("min", np.min)
# stats.register("max", np.max)

if __name__ == '__main__':
    cell_model = 5
    
    
    print("start Time =",  datetime.now().strftime("%H:%M:%S"))
    pop = toolbox.population(n=MU)
   
    pop, logbook = algorithms.eaMuPlusLambda(
        pop,
        toolbox,
        MU,
        LAMBDA,
        CXPB,
        MUTPB,
        NGEN,
        stats,
        halloffame=hof)



    # optimizer = Nsga2Optimizer(cell_model)
    # pop, logbook = optimizer.optimize(
    #     population_size=150, offspring_size=150, n_generations=2)
    print("end Time =",  datetime.now().strftime("%H:%M:%S"))

    print(pop)
    print(logbook)
    print(hof)
    for hero in hof :
        print("nice on is",hero)
        error = ErrorVectorNonPassive(hero)
        print("with error =  ", error )
        print("and total error =  ", sum(error))
    
    pop.sort(key=lambda ind: sum(ErrorVectorNonPassive(ind)))
    # pop = sorted(pop,key=lambda ind: ind.total_indivedual_error)
    print("@@@@@@@@@@@@@@@@@@@@@")
    i = 0 
    for ind in pop:
        print(ind)
        error = ErrorVectorNonPassive(ind)
        print(f"individual {i}   error is {error} " )
        print(f"and Total error =  {sum(error)}")
        i+=1
        print("########################")
        # print(ind.total_indivedual_error)
    # errors = map(lambda ind: ind.total_indivedual_error, pop)
    # best_sol_idx = np.argmin(errors)
    # print("best solution is   ",pop[best_sol_idx], )
    # print("with errors :   ",list( map(lambda ind: ind.measurements_error, pop))[best_sol_idx], )
    # print(f"with total error {list(errors)[best_sol_idx]}")

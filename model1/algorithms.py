
import random
import logging
import shutil
import os

import deap.algorithms
import deap.tools
import pickle

from stoppingCriteria import MaxNGen

logger = logging.getLogger('__main__')



class WeightedSumFitness(deap.base.Fitness):

    """Fitness that compares by weighted sum"""

    def __init__(self, values=(), obj_size=None):
        self.weights = [-1.0] * obj_size if obj_size is not None else [-1]

        super(WeightedSumFitness, self).__init__(values)

    @property
    def weighted_sum(self):
        """Weighted sum of wvalues"""
        return sum(self.wvalues)

    @property
    def sum(self):
        """Weighted sum of values"""
        return sum(self.values)

    def __le__(self, other):
        return self.weighted_sum <= other.weighted_sum

    def __lt__(self, other):
        return self.weighted_sum < other.weighted_sum

    def __deepcopy__(self, _):
        """Override deepcopy"""

        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

class WSListIndividual(list):

    """Individual consisting of list with weighted sum field"""

    def __init__(self, *args, **kwargs):
        """Constructor"""
        self.fitness = WeightedSumFitness(obj_size=kwargs['obj_size'])
        del kwargs['obj_size']
        super(WSListIndividual, self).__init__(*args, **kwargs)

def _define_fitness(pop, obj_size):
    ''' Re-instanciate the fitness of the individuals for it to matches the
    evaluation function.
    '''
    

    new_pop = []
    if pop:
        for ind in pop:
            new_pop.append(WSListIndividual(list(ind), obj_size=obj_size))

    return new_pop


def _evaluate_invalid_fitness(toolbox, population):
    '''Evaluate the individuals with an invalid fitness
    Returns the count of individuals with invalid fitness
    '''
    invalid_ind = [ind for ind in population if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    return len(invalid_ind)


def _update_history_and_hof(halloffame, history, population):
    '''Update the hall of fame with the generated individuals
    Note: History and Hall-of-Fame behave like dictionaries
    '''
    if halloffame is not None:
        halloffame.update(population)

    history.update(population)


def _record_stats(stats, logbook, gen, population, invalid_count):
    '''Update the statistics with the new population'''
    record = stats.compile(population) if stats is not None else {}
    logbook.record(gen=gen, nevals=invalid_count, **record)


def _get_offspring(parents, toolbox, cxpb, mutpb):
    '''return the offspring, use toolbox.variate if possible'''
    if hasattr(toolbox, 'variate'):
        return toolbox.variate(parents, toolbox, cxpb, mutpb)
    return deap.algorithms.varAnd(parents, toolbox, cxpb, mutpb)


def _check_stopping_criteria(criteria, params):
    for c in criteria:
        c.check(params)
        if c.criteria_met:
            logger.info('Run stopped because of stopping criteria: ' +
                        c.name)
            return True
    else:
        return False


def eaAlphaMuPlusLambdaCheckpoint(
        population,
        toolbox,
        mu,
        cxpb,
        mutpb,
        ngen,
        stats=None,
        halloffame=None,
        cp_frequency=1,
        cp_filename=None,
        continue_cp=False):
    r"""This is the :math:`(~\alpha,\mu~,~\lambda)` evolutionary algorithm
    Args:
        population(list of deap Individuals)
        toolbox(deap Toolbox)
        mu(int): Total parent population size of EA
        cxpb(float): Crossover probability
        mutpb(float): Mutation probability
        ngen(int): Total number of generation to run
        stats(deap.tools.Statistics): generation of statistics
        halloffame(deap.tools.HallOfFame): hall of fame
        cp_frequency(int): generations between checkpoints
        cp_filename(string): path to checkpoint filename
        continue_cp(bool): whether to continue
    """

    if cp_filename:
        cp_filename_tmp = cp_filename + '.tmp'

    if continue_cp:
        # A file name has been given, then load the data from the file
        cp = pickle.load(open(cp_filename, "rb"))
        population = cp["population"]
        parents = cp["parents"]
        start_gen = cp["generation"]
        halloffame = cp["halloffame"]
        logbook = cp["logbook"]
        history = cp["history"]
        random.setstate(cp["rndstate"])

        # Assert that the fitness of the individuals match the evaluator
        obj_size = len(population[0].fitness.wvalues)
        population = _define_fitness(population, obj_size)
        parents = _define_fitness(parents, obj_size)
        _evaluate_invalid_fitness(toolbox, parents)
        _evaluate_invalid_fitness(toolbox, population)

    else:
        # Start a new evolution
        start_gen = 1
        parents = population[:]
        logbook = deap.tools.Logbook()
        logbook.header = ['gen', 'nevals'] + (stats.fields if stats else [])
        history = deap.tools.History()

        invalid_count = _evaluate_invalid_fitness(toolbox, population)
        _update_history_and_hof(halloffame, history, population)
        _record_stats(stats, logbook, start_gen, population, invalid_count)

    stopping_criteria = [MaxNGen(ngen)]

    # Begin the generational process
    gen = start_gen + 1
    stopping_params = {"gen": gen}
    while not(_check_stopping_criteria(stopping_criteria, stopping_params)):
        offspring = _get_offspring(parents, toolbox, cxpb, mutpb)

        population = parents + offspring

        invalid_count = _evaluate_invalid_fitness(toolbox, offspring)
        _update_history_and_hof(halloffame, history, population)
        _record_stats(stats, logbook, gen, population, invalid_count)

        # Select the next generation parents
        parents = toolbox.select(population, mu)

        logger.info(logbook.stream)

        if(cp_filename and cp_frequency and
           gen % cp_frequency == 0):
            cp = dict(population=population,
                      generation=gen,
                      parents=parents,
                      halloffame=halloffame,
                      history=history,
                      logbook=logbook,
                      rndstate=random.getstate())
            pickle.dump(cp, open(cp_filename_tmp, "wb"))
            if os.path.isfile(cp_filename_tmp):
                shutil.copy(cp_filename_tmp, cp_filename)
                logger.debug('Wrote checkpoint to %s', cp_filename)

        gen += 1
        stopping_params["gen"] = gen

    return population, halloffame, logbook, history
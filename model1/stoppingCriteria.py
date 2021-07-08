import logging
import numpy


logger = logging.getLogger('__main__')


class StoppingCriteria(object):
    """Stopping Criteria class"""

    def __init__(self):
        """Constructor"""
        self.criteria_met = False
        pass

    def check(self, kwargs):
        """Check if the stopping criteria is met"""
        pass

    def reset(self):
        self.criteria_met = False

class MaxNGen(StoppingCriteria):
    """Max ngen stopping criteria class"""
    name = "Max ngen"

    def __init__(self, max_ngen):
        """Constructor"""
        super(MaxNGen, self).__init__()
        self.max_ngen = max_ngen

    def check(self, kwargs):
        """Check if the maximum number of iteration is reached"""
        gen = kwargs.get("gen")

        if gen > self.max_ngen:
            self.criteria_met = True
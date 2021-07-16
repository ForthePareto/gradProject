import abc
import matplotlib.pyplot as plt
from enum import Enum
import pprint

PRINTING = True


class Level(Enum):
    HIGH = 0.5
    MID = 5.0
    LOW = 10.0
    VLOW = 50.0


class Model(abc.ABC):

    def __init__(self, model_file: str):
        self.model_parameters = None
        self.run(model_file)

    @abc.abstractmethod
    def run(self, model_file: str, model_name: str = None):
        pass

    @abc.abstractmethod
    def get_model_parameters(self, printing=PRINTING):
        pass

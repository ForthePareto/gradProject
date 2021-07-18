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
        self.setup(model_file)

    @abc.abstractmethod
    def setup(self, model_file: str, model_name: str = None):
        pass

    @abc.abstractmethod
    def get_model_parameters(self, printing=PRINTING):
        pass


class Plotter:
    @staticmethod
    def graphVolt(self, voltVector, tVector, label, ax, color="black"):
        # plt.figure()
        ax.plot(tVector, voltVector, color=color, label=label)
        ax.set(xlabel='t (ms)')
        ax.set(ylabel='v (mV)')
        # plt.show()

        return plt

    @staticmethod
    def graphOverlap(v1, t1, color1, label1, alpha1, v2, t2, color2, label2, alpha2, title):
        plt.figure()
        plt.plot(t1, v1, color=color1, alpha=alpha1, label=label1)
        plt.plot(t2, v2, color=color2, alpha=alpha2, label=label2)
        plt.title(title)
        plt.legend()
        plt.xlabel('t (ms)')
        plt.ylabel('v (mV)')
        # plt.show()

        return plt

    @staticmethod
    def graphMarker(plt, markAtT, markAtVolt, label, markerShape='X'):
        plt.plot(markAtT, markAtVolt, label=label, marker=markerShape)
        plt.legend()

        # plt.show()

from neuron import h
from neuron.units import ms, mV
import matplotlib.pyplot as plt
from enum import Enum



class Level(Enum):
    HIGH = 0.5
    MID = 5.0
    LOW = 10.0
    VLOW = 50.0


class NrnModel():
    def __init__(self, cellTemplateFile):

        self.cell = None
        self.soma = None
        self.iseg = None
        self.dendrites = []

        self.singleCellRun(cellTemplateFile)

        # print(dir(self.cell))
        # print(dir(self.soma))

        # print('-- Model topology --')
        # print(h.topology())

    def setP(self):
        h.amA_NafSmb1 = 999
        print(h.amA_NafSmb1)

    def singleCellRun(self, cellTemplateFile):
        # loading the cell
        h.load_file(cellTemplateFile)    # with no h current

        self.cell = h.fivecompMy()
        self.soma = self.cell.soma
        self.iseg = self.cell.iseg
        self.dendrites = [self.cell.dend1, self.cell.dend2, self.cell.dend3]

        # return cell,soma

    def setIClamp(self, delay, duration, amp, segment, position):

        # Add a current clamp at {position} of {segment}
        stim = h.IClamp(segment(position))
        stim.delay = delay           # ms
        stim.dur = duration        # ms
        stim.amp = amp             # nA
        return stim
        # print(self.soma.psection())

    def recordVolt(self, segmentToRecord, position):

        # set up a recording vector and record voltage at {position} of {segment}
        segment_v = h.Vector().record(segmentToRecord(position)._ref_v)

        segment_t = h.Vector().record(h._ref_t)  # record time.
        return segment_v, segment_t

    def runControler(self, TStop, init=-65):
        h.load_file('stdrun.hoc')
        h.finitialize(init * mV)
        h.continuerun(TStop * ms)
        # print(list(self.soma_v))

    def graphVolt(self, voltVector, tVector, label):
        plt.figure()
        # axes = plt.gca()
        # axes.set_ylim([-80,40])
        plt.plot(tVector, voltVector, color='k', label=label)
        plt.xlabel('t (ms)')
        plt.ylabel('v (mV)')
        # plt.show()

        return plt

    def graphOverlap(self, v1, t1, color1, label1, alpha1, v2, t2, color2, label2, alpha2, title):
        plt.figure()
        plt.plot(t1, v1, color=color1, alpha=alpha1, label=label1)
        plt.plot(t2, v2, color=color2, alpha=alpha2, label=label2)
        plt.title(title)
        plt.legend()
        plt.xlabel('t (ms)')
        plt.ylabel('v (mV)')
        # plt.show()

        return plt

    def graphMarker(self, plt, markAtT, markAtVolt, label, markerShape='X'):
        plt.plot(markAtT, markAtVolt, label=label, marker=markerShape)
        plt.legend()

        # plt.show()

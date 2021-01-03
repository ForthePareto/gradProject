from neuron import h
from neuron.units import ms, mV
import matplotlib.pyplot as plt

class NrnModel():
    def __init__(self):
        ## loading the cell
        h.load_file("5CompMy_temp.hoc")    # with no h current
        h.load_file('stdrun.hoc')

        # h('proc advance() {nrnpython("custom_advance()")}') 
        self.cell = None
        self.soma = None

        self.stim = None
        self.soma_v = None
        self.t = None
        
        self.singleCellRun()
        self.setStimulus()
        self.record()
        self.runControler()

        # print(dir(self.cell))
        # print(dir(self.soma))

        # print(self.soma.psection())
        
        # print(h.topology())
        self.measureInputResistance(-5)
        self.plotResults()


    def singleCellRun(self):
    
        self.cell = h.fivecompMy()
        self.soma = self.cell.soma
    

    # def custom_advance(self):
    #     h.fadvance()

    def setStimulus(self):

        self.stim = h.IClamp(self.soma(0.5))  # add a current clamp the the middle of the soma
        self.stim.delay = 150  # ms
        self.stim.dur   = 100 # ms
        self.stim.amp   = -5.0 # nA
        # print(self.soma.psection())



    def record(self):

        self.soma_v = h.Vector().record(self.soma(0.5)._ref_v)  # set up a recording vector and record voltage at the middle of the soma
        
        self.t = h.Vector().record(h._ref_t) #record time.
        
        
    def runControler(self):
        # h.load_file('stdrun.hoc')
        h.finitialize(-65 * mV)
        h.continuerun(500 * ms)
        # print(list(self.soma_v))
        



    def plotResults(self):
        plt.figure()
        # axes = plt.gca()
        # axes.set_ylim([-80,40]) 
        plt.plot(self.t, self.soma_v,color='k',label='soma(0.5)')
        plt.xlabel('t (ms)')
        plt.ylabel('v (mV)')
        
        plt.show()

    def measureInputResistance(self,ampExct):
        restMembPot = max(list(self.soma_v)) # Should be -65 mv
        minDepolarPot = min(list(self.soma_v))
        inputResistance = abs((restMembPot - minDepolarPot)/ampExct) # should it always be positive  ??

        print(f'restMembPot: {restMembPot} mV')
        print(f'minDepolarPot: {minDepolarPot} mV')
        print(f'inputResistance: {inputResistance} (mV/nA)')
        
        return inputResistance



nrn = NrnModel()
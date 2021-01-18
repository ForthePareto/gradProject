from neuron import h
from neuron.units import ms, mV
import matplotlib.pyplot as plt

class NrnModel():
    def __init__(self,cellTemplateFile):

        self.cell = None
        self.soma = None

        self.singleCellRun(cellTemplateFile)

        # print(dir(self.cell))
        # print(dir(self.soma))

        print('-- Model topology --')        
        print(h.topology())


    def singleCellRun(self,cellTemplateFile):
        ## loading the cell
        h.load_file(cellTemplateFile)    # with no h current
        
        self.cell = h.fivecompMy()
        self.soma = self.cell.soma

        # return cell,soma
    


    def setIClamp(self,delay,duration,amp,segment,position):

        stim = h.IClamp(segment(position))  # Add a current clamp at {position} of {segment}  
        stim.delay = delay           # ms
        stim.dur   = duration        # ms
        stim.amp   = amp             # nA
        return stim
        # print(self.soma.psection())



    def recordVolt(self,segmentToRecord,position):

        segment_v = h.Vector().record(segmentToRecord(position)._ref_v)  # set up a recording vector and record voltage at {position} of {segment}
        
        segment_t = h.Vector().record(h._ref_t) #record time.
        return segment_v,segment_t
        
    def runControler(self,TStop,init=-65):
        h.load_file('stdrun.hoc')
        h.finitialize(init * mV)
        h.continuerun(TStop * ms)
        # print(list(self.soma_v))
        



    def graphVolt(self,voltVector,tVector,label):
        plt.figure()
        # axes = plt.gca()
        # axes.set_ylim([-80,40]) 
        plt.plot(tVector, voltVector,color='k',label=label)
        plt.xlabel('t (ms)')
        plt.ylabel('v (mV)')
        
        plt.show()




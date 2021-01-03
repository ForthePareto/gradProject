from NrnModel import  NrnModel 

class FiveCompModel():
    def __init__(self,):
        
        self.model = NrnModel("5CompMy_temp.hoc")
    
    def measureInputResistance(self):
        amp = -5
        stim = self.model.setIClamp(delay=150,duration=100,amp=amp,segment=self.model.soma,position=0.5)
        volt,t = self.model.recordVolt(self.model.soma,0.5)
        self.model.runControler(TStop= 500,init = -65 )

        restMembPot = max(list(volt)) # Should be -65 mv
        minDepolarPot = min(list(volt))
        inputResistance = abs((restMembPot - minDepolarPot)/amp) # should it always be positive  ??
        # print(self.soma.psection())

        print("-- Input Resistance Measurement --")
        print(f'restMembPot: {restMembPot} mV')
        print(f'minDepolarPot: {minDepolarPot} mV')
        print(f'inputResistance: {inputResistance} (mV/nA)')
        self.model.graphVolt(volt,t,label='soma(0.5)')
        
        return inputResistance


if __name__=='__main__':

    modelRun = FiveCompModel()
    modelRun.measureInputResistance()
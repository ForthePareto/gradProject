from NrnModel import  NrnModel 

class FiveCompModel():
    def __init__(self,):
        
        self.model = NrnModel("5CompMy_temp.hoc")
    
    def inputResistance(self,amp):
        # amp = -0.5
        amp = amp
        stim = self.model.setIClamp(delay=150,duration=100,amp=amp,segment=self.model.soma,position=0.5)
        volt,t = self.model.recordVolt(self.model.soma,0.5)
        self.model.runControler(TStop= 500,init = -65 )

        restMembPot = max(list(volt)) # Should be -65 mv
        minDepolarPot = min(list(volt))
        inputResistance = abs((restMembPot - minDepolarPot)/amp) # should it always be positive  ??
        # print(self.soma.psection())

        print("----- Input Resistance Measurement -----")
        print(f'clamp Current: {amp} nA')
        print(f'restMembPot: {restMembPot} mV')
        print(f'minDepolarPot: {minDepolarPot} mV')
        print(f'inputResistance: {inputResistance} (mV/nA)')
        # self.model.graphVolt(volt,t,label='soma(0.5)')
        print("----- ---------------------------- -----")
        
        return inputResistance

    def timeConstant(self,inputResistance):
        print("----- time Constant Measurement -----")

        capacitance = self.model.soma.psection()['cm'][0]
        # print(capacitance)
        tau = capacitance * inputResistance
        print("----- ---------------------------- -----")

        return tau


if __name__=='__main__':

    modelRun = FiveCompModel()
    testAmps = [-0.5,-0.6,-0.7,-0.8,-0.9,-1.0]
    
    inputRes = [modelRun.inputResistance(amp) for amp in testAmps]
    avgInRes = sum(inputRes)/len(inputRes)
    print(f'inputRes List: {inputRes}')
    print(f'avgInRes: {avgInRes} (mV/nA)' )
    # tau = modelRun.timeConstant(inputRes)

    # print(f'Tau: {tau}')
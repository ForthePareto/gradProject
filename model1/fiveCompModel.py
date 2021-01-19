from NrnModel import  NrnModel 
import math
class FiveCompModel():
    def __init__(self,):
        
        self.model = NrnModel("5CompMy_temp.hoc")
    

    def generateSpike(self,clampAmp,duration,delay,stimSeg,clampAt,Tstop,init=-65):
        stim = self.model.setIClamp(delay,duration,clampAmp,segment=stimSeg,position=clampAt)
        volt,t = self.model.recordVolt(self.model.soma,0.5)
        self.model.runControler(TStop= Tstop,init = -65 )
        return volt,t 

    def inputResistance(self,amp,EnablePlotting,EnablePrinting):
        delay = 150
        duration = 100
        volt,t = self.generateSpike(amp,duration = duration,delay = delay,stimSeg = self.model.soma,clampAt = 0.5,Tstop = 500)
        

        # TODO: slice the time interval of the stimulas and get the plateau volts
        # ::DONE::
        slicedVolt,slicedT = self.sliceSpikeGraph(volt,t,delay - 10 , delay + duration + 10)
        
        restMembPot = max(slicedVolt) # Should be around -65 mv
        minDepolarPot = min(slicedVolt)

        inputResistance = abs((restMembPot - minDepolarPot)/amp) # should it always be positive  ??
        # print(self.soma.psection())
        
        if EnablePrinting:
            print("----- Input Resistance Measurement -----")
            print(f'clamp Current: {amp} nA')
            print(f'restMembPot: {restMembPot} mV')
            print(f'minDepolarPot: {minDepolarPot} mV')
            print(f'inputResistance: {inputResistance} (mV/nA)')
            print("----- ---------------------------- -----")
        
        if EnablePlotting:
            #TODO: overlay plots , plot full graph and the sliced with diff color ,  and mark points on the graph
            # ::DONE::             
            plt = self.model.graphOverlap(volt,t,'k','Full Spike',0.8,slicedVolt,slicedT,'g','Sliced spike',1.0,'input Resistance')
            plt.show()
        return inputResistance

    def avgInRes(self,sampleAmps,EnablePlotting,EnablePrinting):
        print("----- Averaged Input Resistance  -----\n")

        inputRes = [modelRun.inputResistance(amp,EnablePlotting,EnablePrinting) for amp in sampleAmps]
        avgInRes = sum(inputRes)/len(inputRes)
        print(f'inputRes List: \n{inputRes}\n')
        print(f'avgInRes: {avgInRes} (mV/nA)' )
        print("----- ---------------------------- -----\n")

        return avgInRes

    
    def sliceSpikeGraph(self,voltVec,tVec,startAtTime,endAtTime):
        voltVec = list(voltVec)
        tVec = list(tVec)

        slicedTime = [t for t in tVec if startAtTime <= t <= endAtTime]

        startIndex = tVec.index(slicedTime[0]) 
        endIndex = tVec.index(slicedTime[-1]) 

        slicedVolt = voltVec[startIndex:endIndex + 1] 

        return slicedVolt,slicedTime

    def timeConstant(self,amp):
        delay = 150
        duration = 100
        volt , t  = self.generateSpike(amp,duration = duration,delay = delay,stimSeg = self.model.soma,clampAt = 0.5,Tstop = 500)
        tStart  = delay + duration 
        tEnd    = delay + duration + 100
        
        slicedVolt,slicedTime = self.sliceSpikeGraph(volt,t,tStart,tEnd)

        vStart =  slicedVolt[0]
        vEnd =    slicedVolt[-1]
        tC = -(tEnd - tStart)/ (math.log(vEnd/vStart))
        
        plt = self.model.graphOverlap(volt,t,'k','Full Spike',0.8,slicedVolt,slicedTime,'g','Sliced spike',1.0,'Time Constant')
        # self.model.graphMarker(plt,tStart,vStart,'start Point')
        plt.show()
        return tC



if __name__=='__main__':

    modelRun = FiveCompModel()
    # modelRun.inputResistance(-0.5,True,True)

    testAmps = [-0.5,-0.6,-0.7,-0.8,-0.9,-1.0]
    modelRun.avgInRes(testAmps,True,False)
    
    tau = modelRun.timeConstant(-0.5)
    
    

    print(f'Tau: {tau}')
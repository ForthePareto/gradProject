from NrnModel import NrnModel ,Level
import math
from numpy import arange



class FiveCompModel():
    def __init__(self,):

        self.model = NrnModel("5CompMy_temp.hoc")
        self.soma = self.model.soma
        self.iseg = self.model.iseg

    def stimulateCell(self, clampAmp, duration, delay, stimSeg, clampAt, Tstop, init=-65):
        """ Stimulate the cell at the desired properties
            Args:
            :param clampAmp: the current value at which the cell is stimulated (in nA) 
            :param duration: the time for which the stimulation is continued
            :param delay: the time at which the stimulation is started
            :param stimSeg: the segment at which the cell is stimulated
            :param clampAt: the location in the segment at which clamp is inserted
            :param Tstop: the duration for which the recording is done
            :param init: the resting membrane voltage of the cell
        
        :return volt: the recorded voltage vector
        :return t: the recorded time vector
        
         """
        stim = self.model.setIClamp(delay, duration, clampAmp, segment=stimSeg, position=clampAt)
        volt, t = self.model.recordVolt(self.model.soma, 0.5)
        self.model.runControler(TStop=Tstop, init=-65)
        
        return volt, t

    def inputResistance(self, amp, EnablePlotting, EnablePrinting):
        delay = 150
        duration = 100
        volt, t = self.stimulateCell(
            amp, duration=duration, delay=delay, stimSeg=self.model.soma, clampAt=0.5, Tstop=500)

        # TODO: slice the time interval of the stimulas and get the plateau volts
        # ::DONE::
        slicedVolt, slicedT = self.sliceSpikeGraph(
            volt, t, delay - 10, delay + duration + 10)

        restMembPot = max(slicedVolt)  # Should be around -65 mv
        minDepolarPot = min(slicedVolt)

        # should it always be positive  ??
        inputResistance = abs((restMembPot - minDepolarPot)/amp)
        # print(self.soma.psection())

        if EnablePrinting:
            print("----- Input Resistance Measurement -----")
            print(f'clamp Current: {amp} nA')
            print(f'restMembPot: {restMembPot} mV')
            print(f'minDepolarPot: {minDepolarPot} mV')
            print(f'inputResistance: {inputResistance} (mV/nA)')
            print("----- ---------------------------- -----")

        if EnablePlotting:
            # TODO: overlay plots , plot full graph and the sliced with diff color ,  and mark points on the graph
            # ::DONE::
            plt = self.model.graphOverlap(
                volt, t, 'k', 'Full Spike', 0.8, slicedVolt, slicedT, 'g', 'Sliced spike', 1.0, 'input Resistance')
            plt.show()
        return inputResistance

    def avgInRes(self, sampleAmps, EnablePlotting, EnablePrinting):
        print("----- Averaged Input Resistance  -----\n")

        inputRes = [modelRun.inputResistance(
            amp, EnablePlotting, EnablePrinting) for amp in sampleAmps]
        avgInRes = sum(inputRes)/len(inputRes)
        print(f'inputRes List: \n{inputRes}\n')
        print(f'avgInRes: {avgInRes} (mV/nA)')
        print("----- ---------------------------- -----\n")

        return avgInRes

    def timeConstant(self, amp):
        delay = 150
        duration = 100
        volt, t = self.stimulateCell(
            amp, duration=duration, delay=delay, stimSeg=self.model.soma, clampAt=0.5, Tstop=500)
        tStart = delay + duration
        # TODO: make a function that detects stable intervales and use it in time constant function
        tEnd = delay + duration + 100

        slicedVolt, slicedTime = self.sliceSpikeGraph(volt, t, tStart, tEnd)

        vStart = slicedVolt[0]
        vEnd = slicedVolt[-1]
        # print(f'vStart: {vStart}')
        # print(f'vEnd: {vEnd}')
        # print(f'tStart: {tStart}')
        # print(f'tEnd: {tEnd}')
        tC = -(tEnd - tStart) / math.log(1 - (vEnd/vStart))

        plt = self.model.graphOverlap(
            volt, t, 'k', 'Full Spike', 0.8, slicedVolt, slicedTime, 'g', 'Sliced spike', 1.0, 'Time Constant')
        # self.model.graphMarker(plt,tStart,vStart,'start Point')
        plt.show()
        return tC

    def APHeight(self,voltVec,timeVec,delay, duration):
        """ measures the AP Height of the spike 

                :param voltVec: recoreded vector of the spike voltage 
                :param timeVec: recoreded vector of the spike time
                :param delay: the time at which the cell is stimulated   
                :param duration: the time for which the stimulation is continued
            :return apHeight: the Height of the spike in milliVolts
            :return apRest: the resting potential in milliVolts
            :return apPeak: the peak potential in milliVolts

        """
        volt, time = self.sliceSpikeGraph(voltVec, timeVec, delay, delay + 10)
        # get peak point
        vPeak = max(volt)
        indexPeak = volt.index(vPeak)
        TPeak = time[indexPeak]
        # get restng point 
        vRest = volt[0]
        indexVRest = volt.index(vRest)
        tRest = time[indexVRest]
        apHeight = abs(vPeak - vRest) 
        print(f'apHeight: {apHeight} mV')
        

        plt = self.model.graphOverlap(voltVec, timeVec, 'k', 'Full AP', 0.8,
                                      volt, time, 'g', 'AP Spike', 1.0, 'AP Height')

        self.model.graphMarker(plt, TPeak, vPeak, 'AP Peak', 'x')
        self.model.graphMarker(plt, tRest, vRest, 'AP Resting', 'x')
        
        return  apHeight , vRest , vPeak 

    def APWidth(self, voltVec, timeVec, delay, duration):
        ## FIXME: matches aren't aon the same level , but close enough ... (works for me) 
        """ measures the AP width of the spike 

                :param voltVec: recoreded vector of the spike voltage 
                :param timeVec: recoreded vector of the spike time
                :param delay: the time at which the cell is stimulated   
                :param duration: the time for which the stimulation is continued
            :return : the width of the spike in milliSecs

        """
        # TODO: find the end of the spike with the interval function that will be done later
        # volt, time = self.sliceSpikeGraph(voltVec, timeVec, delay, delay + 10)
        volt , time ,plt= self.patternHighligher(voltVec,timeVec,delay,duration)
        apHeight , vRest , vPeak = self.APHeight(voltVec,timeVec,delay,duration)
        # calculate the mid point
        print(f'vRest {vRest} mV')
        apHalfV = (apHeight / 2) + vRest
        print(f'apHalfV {apHalfV} mV')

        # find actual matches
        matches =self.closeMatches(volt,apHalfV,4.5)
        matches = list(zip(*matches))
        # print(f'matches {matches}')
        vMatches = matches[0]
        indexMatches = matches[-1]
        
        m1 = vMatches[0]
        m2 = vMatches[-1]
        t1 = time[indexMatches[0]] 
        t2 = time[indexMatches[-1]] 
        
        apWidth = (t2 - t1)
        
        plt = self.model.graphOverlap(voltVec, timeVec, 'k', 'Full AP', 0.8,
                                      volt, time, 'g', 'AP Spike', 1.0, 'AP Width')

        self.model.graphMarker(plt, t1, m1, 'AP half1', 'x')
        self.model.graphMarker(plt, t2, m2, 'AP half2', 'x')

        plt.show()
        print(f'apWidth: {apWidth} ms')
        return apWidth


    def AHPDepth(self,voltVec,timeVec,delay,duration):
        """ Calculate the depth of the AHP phase in mV   
        
        Args:
            :param voltVec: recoreded vector of the spike voltage 
            :param timeVec: recoreded vector of the spike time
            :param delay: the time at which the stimulation is started
            :param duration: the time for which the stimulation is continued
        
        :return AHPDepth:depth of the AHP phase in mV
        
        """
        volt,t,plt = self.patternHighligher(voltVec,timeVec,delay,duration,reverse=True)
        AHPStartV = volt[0]          
        AHPPeakV = min(volt)
        AHPStartT = t[0]          
        AHPPeakT = t[volt.index(AHPPeakV)]
        AHPDepthV = abs(AHPPeakV - AHPStartV)
        self.model.graphMarker(plt,AHPPeakT,AHPPeakV,'AHP PEAK',markerShape='x')
        self.model.graphMarker(plt,AHPStartT,AHPStartV,'AHP Start',markerShape='x')
        
        plt.title('AHP Depth')
        plt.show()
        print(f'AHPDepthV :{AHPDepthV} mV')
        return AHPDepthV


    def AHPDuration(self,voltVec,timeVec,delay,duration):
        """ Calculate the duration of the AHP phase in mSec   
        
        Args:
            :param voltVec: recoreded vector of the spike voltage 
            :param timeVec: recoreded vector of the spike time
            :param delay: the time at which the stimulation is started
            :param duration: the time for which the stimulation is continued
        
        :return AHPDuration:duration of the AHP phase in mSec
        """
        volt,t,plt = self.patternHighligher(voltVec,timeVec,delay,duration,reverse=True)

        AHPStartV = volt[0]          
        AHPStartT = t[0]          

        AHPEndV = volt[-1]        
        AHPEndT = t[-1]
        AHPDuration = AHPEndT - AHPStartT 
        self.model.graphMarker(plt,AHPStartT,AHPStartV,'AHP Start',markerShape='x')
        self.model.graphMarker(plt,AHPEndT,AHPEndV,'AHP End',markerShape='x')
        
        plt.title('AHP Duration')
        plt.show()
        print(f'AHPDuration: {AHPDuration} mSecs')
        return AHPDuration


    def AHPHalfDuration(self,voltVec,timeVec,delay,duration):
        """ Calculate the half-duration of the AHP phase in mSec   
        
        Args:
            :param voltVec: recoreded vector of the spike voltage 
            :param timeVec: recoreded vector of the spike time
            :param delay: the time at which the stimulation is started
            :param duration: the time for which the stimulation is continued
        
        :return AHPHalfDuration:half duration of the AHP phase in mSec
        """
        volt,t,plt = self.patternHighligher(voltVec,timeVec,delay,duration,reverse=True)

        AHPStartV = volt[0]          
        AHPPeakV = min(volt)
        # print(f'AHPPeakV :{AHPPeakV}')
        # print(f'AHPStartV :{AHPStartV}')

        AHPHalfV = ((AHPPeakV - AHPStartV) / 2) + AHPStartV 
        print(f'AHPHalfV :{AHPHalfV}')
        # find close matches to the exact value of {AHPHalfV}
        matches = self.closeMatches(volt,AHPHalfV,0.005)
        matches = list(zip(*matches))
        print(f'matches {matches}')
        matchesV,matchesT = matches
        # left point
        v1 = matchesV[0]
        t1 = t[matchesT[0]]
        
        # right point
        v2 = matchesV[-1]
        t2 = t[matchesT[-1]]

            
        AHPHalfDuration = t2 - t1 
        self.model.graphMarker(plt,t1,v1,'AHP half-left',markerShape='x')
        self.model.graphMarker(plt,t2,v2,'AHP half.right',markerShape='x')
        plt.show()
        print(f'AHPHalfDuration: {AHPHalfDuration} mSecs')
        return AHPHalfDuration


    def AHPHalfDecay(self,voltVec,timeVec,delay,duration):
        """ Calculate the half-decay of the AHP phase in mSec   
        
        Args:
            :param voltVec: recoreded vector of the spike voltage 
            :param timeVec: recoreded vector of the spike time
            :param delay: the time at which the stimulation is started
            :param duration: the time for which the stimulation is continued
        
        :return AHPHalfDecay:half decay of the AHP phase in mSec
        """        
        volt,t,plt = self.patternHighligher(voltVec,timeVec,delay,duration,reverse=True)

        AHPStartV = volt[0]          
        AHPPeakV = min(volt)
        AHPPeakT = t[volt.index(AHPPeakV)]

        AHPHalfV = ((AHPPeakV - AHPStartV) / 2) + AHPStartV 
        # print(f'AHPHalfV :{AHPHalfV}')

        # find close matches to the exact value of {AHPHalfV}
        matches = self.closeMatches(volt,AHPHalfV,0.005)
        matches = list(zip(*matches))
        # print(f'matches {matches}')
        matchesV,matchesT = matches        
        
        # right point
        AHPHalfVLeft = matchesV[-1]
        AHPHalfTLeft = t[matchesT[-1]]

        AHPHalfDecay = AHPHalfTLeft - AHPPeakT
        self.model.graphMarker(plt,AHPHalfTLeft,AHPHalfVLeft,'AHP half-left',markerShape='x')
        self.model.graphMarker(plt,AHPPeakT,AHPPeakV,'AHP Peak',markerShape='x')
        
        plt.title('AHP Half-Decay')
        plt.show()
        print(f'AHPHalfDecay: {AHPHalfDecay} mSecs')
        return AHPHalfDecay


    def AHPRisingTime(self,voltVec,timeVec,delay,duration):
        """ Calculate the Rising Time of the AHP phase in mSec   
        
            Args:
                :param voltVec: recoreded vector of the spike voltage 
                :param timeVec: recoreded vector of the spike time
                :param delay: the time at which the stimulation is started
                :param duration: the time for which the stimulation is continued
            
            :return AHPRisingTime: Rising Time of the AHP phase in mSec
        """
        volt,t,plt = self.patternHighligher(voltVec,timeVec,delay,duration,reverse=True)
        
        AHPStartV = volt[0]          
        AHPStartT = t[0]          
        
        AHPPeakV = min(volt)
        AHPPeakT = t[volt.index(AHPPeakV)]
        
        AHPRisingTime = AHPPeakT - AHPStartT
        self.model.graphMarker(plt,AHPPeakT,AHPPeakV,'AHP PEAK',markerShape='x')
        self.model.graphMarker(plt,AHPStartT,AHPStartV,'AHP Start',markerShape='x')
        plt.title('AHP-Rising Time')
        plt.show()
        print(f'AHPRisingTime :{AHPRisingTime} mV')
        return AHPRisingTime

    def Rheobase(self,accuracy,refineTimes:int,duration=50,delay=150):
        """ Calculate Rheobase current of the cell in nA
            Args:
                :param accuracy: accuracy level {Level.HIGH, Level.MID, Level.LOW,Level.VLOW}  
                :param refineTimes: number of repeation, the higher, the more accurate the Rheobase     
                :param delay: the time at which the stimulation is started 
                :param duration: the time for which the stimulation is continued (should be +50 ms)
        
            :return rheobase: Calculate Rheobase current of the cell in nA
        """
        start = 1
        end = 20
        step = 1
        while refineTimes:

            for current in arange(start,end,step):
                volt,t = self.stimulateCell(current,duration,delay,self.soma,0.5,500)
                if self.isSpike(volt,t,delay,duration,accuracy):
                    start = current - step
                    end = current 
                    print(f'current: {current}')
                    step = step / 10
                    break
                    
            refineTimes -= 1
        rheobase = end
        return rheobase
        
########################################################################        
##################         HELPER FUNCTIONS          ###################        
########################################################################        


    def sliceSpikeGraph(self, voltVec, tVec, startAtTime, endAtTime):
        """ Slices the spike between two desired times

                :param voltVec: recoreded vector of the spike voltage 
                :param tVec: recoreded vector of the spike time
                :param startAtTime: time in (ms) at which start the slice
                :param endAtTime: time in (ms) at which end the slice
            :return slicedVolt: (list) of the sliced spike's voltVec  
            :return slicedTime: (list) of the sliced spike's tVec

         """

        voltVec = list(voltVec)
        tVec = list(tVec)

        slicedTime = [t for t in tVec if startAtTime <= t <= endAtTime]

        startIndex = tVec.index(slicedTime[0])
        endIndex = tVec.index(slicedTime[-1])

        slicedVolt = voltVec[startIndex:endIndex + 1]

        return slicedVolt, slicedTime


    def closeMatches(self, lst: list, findVal, tolerance):
        # TODO: complete docs 
        """ find a list of closest matches to a specific value with a spicified tolerance 
            Args:
                :param lst: 
                :param findVal: 
                :param tolerance:
            :return: list of (value,index) pairs 
        """
        # matches = [(val,index) for index,val in enumerate(lst) if abs(val - findVal) < tolerance]
        matches = [(val,index) for index,val in enumerate(lst) if math.isclose(val,findVal,abs_tol=tolerance)]

        return matches


    def patternHighligher(self,voltVec,timeVec,delay,duration,restingVolt=-65,reverse=False):
        """ Detects the up-down shape of the spike and extracts it
            Args:
                :param voltVec: recoreded vector of the spike voltage 
                :param timeVec: recoreded vector of the spike time
                :param delay: the time at which the stimulation is started
                :param duration: the time for which the stimulation is continued
            
            :return spikeVolt: list of the spike voltage values
            :return spikeTime: list of the spike time values
            :return plt: matplotlib class member (graph handler,used to overlay on top old graphs)

         """
        volt,t = self.sliceSpikeGraph(voltVec,timeVec,delay,delay + duration + 70)
        stillUp = True 
        stillDown = True 
        # if not(reverse):
        spikeVolt = [volt[0]]
        for v in volt:
            title = "Spike Pattern"
            label = "Spike"

            if (v >= spikeVolt[-1]) and stillUp:
                spikeVolt += [v]
            elif (v < spikeVolt[-1]) and (v >= restingVolt) and stillDown:
                stillUp = False
                spikeVolt += [v]
            else:
                stillDown = False
        if reverse:
            stillDown = True
            stillUp = False
            spikeVolt = [spikeVolt[-1]]
            title = "AHP Pattern"
            label = "AHP"
            for v in volt:
                if (v < spikeVolt[-1]) and(v <= restingVolt) and stillDown:
                    spikeVolt += [v]
                    stillUp = True
                elif (v > spikeVolt[-1]) and (v <= restingVolt) and stillUp:
                    stillDown = False
                    spikeVolt += [v]
                else:
                    stillUp = False
        
        
        startIndex = volt.index(spikeVolt[0])
        endIndex =  volt.index(spikeVolt[-1])
        spikeTime = t[startIndex:endIndex + 1] 

        # resize both list to match dimenstions
        spikeVolt,spikeTime = self.matchSize(spikeVolt,spikeTime)

        plt = self.model.graphOverlap(voltVec, timeVec, 'k',"Full AP",0.2,
                                        spikeVolt,spikeTime,'r',label,1.0,title)
        # plt.show()
    
    
        return spikeVolt,spikeTime,plt

    def matchSize(self,lst1,lst2):
        # resize both list to match dimenstions
        len1 = len(lst1)
        len2 = len(lst2)
        if len1 != len2:
            minLen = min(len1,len2)
            lst1 = lst1[:minLen] 
            lst2= lst2[:minLen] 
        return lst1,lst2


    def isSpike(self,voltVec,timeVec,delay,duration,accuracy:Level) -> bool: 
        """ detect if there is a spike 
        
        Args:
            :param voltVec: recoreded vector of the spike voltage 
            :param timeVec: recoreded vector of the spike time
            :param delay: the time at which the stimulation is started
            :param duration: the time for which the stimulation is continued
            :param accuracy: accuracy level {Level.HIGH, Level.MID, Level.LOW,Level.VLOW}  
            
        :return bool: true if spike and false otherwise
         """

        volt,t,plt = self.patternHighligher(voltVec,timeVec,delay,duration)
        plt.close()
        return (abs(max(volt) - min(volt)) >= accuracy.value)



########################################################################        
########################################################################        


if __name__ == '__main__':

    def testRun():
        modelRun = FiveCompModel()
        modelRun.inputResistance(-0.5,True,True)

        # testAmps = [-0.5, -0.6, -0.7, -0.8, -0.9, -1.0]
        # modelRun.avgInRes(testAmps, True, False)
        tau = modelRun.timeConstant(-0.5)

        delay = 150
        duration = 6
        current = 12
        volt, t = modelRun.stimulateCell(current, duration, delay, modelRun.iseg, 0.5, 500)
        # res = modelRun.isSpike(volt,t,delay,duration,Level.HIGH)
        # print(f'Is Spike: {res}')
        modelRun.APHeight(volt,t,delay,duration)
        modelRun.APWidth(volt,t,delay,duration)
        modelRun.AHPDepth(volt,t,delay,duration)
        modelRun.AHPDuration(volt,t,delay,duration)
        modelRun.AHPHalfDuration(volt,t,delay,duration)
        modelRun.AHPHalfDecay(volt,t,delay,duration)
        modelRun.AHPRisingTime(volt,t,delay,duration)
        modelRun.Rheobase(Level.VLOW,3)
        # spikeV,spikeT,plt = modelRun.patternHighligher(volt,t,-65,150,6,reverse=False)
        # spikeV,spikeT,plt = modelRun.patternHighligher(volt,t,-65,150,6,reverse=True)
        # print(spikeV)
        # plt = modelRun.model.graphOverlap(volt, t, 'k',"Full AP",0.8,
        #                                 spikeV,spikeT,'r',"Spike",1.0,"SPIKE Pattern")
        # plt.show()
        # width = modelRun.APWidth(volt, t, 150, 5)
        # print(f'Tau: {tau} ms')

    testRun()
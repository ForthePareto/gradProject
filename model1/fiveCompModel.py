from NrnModel import NrnModel
import math


class FiveCompModel():
    def __init__(self,):

        self.model = NrnModel("5CompMy_temp.hoc")
        self.soma = self.model.soma
        self.iseg = self.model.iseg

    def generateSpike(self, clampAmp, duration, delay, stimSeg, clampAt, Tstop, init=-65):
        stim = self.model.setIClamp(
            delay, duration, clampAmp, segment=stimSeg, position=clampAt)
        volt, t = self.model.recordVolt(self.model.soma, 0.5)
        self.model.runControler(TStop=Tstop, init=-65)
        return volt, t

    def inputResistance(self, amp, EnablePlotting, EnablePrinting):
        delay = 150
        duration = 100
        volt, t = self.generateSpike(
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

    def timeConstant(self, amp):
        delay = 150
        duration = 100
        volt, t = self.generateSpike(
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

    def APWidth(self, voltVec, timeVec, startsAt, duration):
        """ measures the AP width of the spike 

                :param voltVec: recoreded vector of the spike voltage 
                :param timeVec: recoreded vector of the spike time
                :param startsAt: the time at which the cell is stimulated   
                :param duration: the time for which the stimulation is continued
            :return : the width of the spike in milliSecs

        """
        # TODO: find the end of the spike with the interval function that will be done later
        volt, time = self.sliceSpikeGraph(
            voltVec, timeVec, startsAt, startsAt + 10)
        # get peak point
        vPeak = max(volt)
        indexPeak = volt.index(vPeak)
        TPeak = time[indexPeak]
        # get restng point 
        vRest = volt[0]
        indexVRest = volt.index(vRest)
        tRest = time[indexVRest]
        # calculate the mid point
        apHalfV = ((vPeak - vRest) / 2) + vRest
        print(f'apHalfV {apHalfV}')

        # find actual matches
        matches =self.closeMatches(volt,apHalfV,0.8)
        matches = list(zip(*matches))
        print(f'matches {matches}')
        vMatches = matches[0]
        indexMatches = matches[-1]
        
        m1 = vMatches[0]
        m2 = vMatches[-1]
        t1 = time[indexMatches[0]] 
        t2 = time[indexMatches[-1]] 
        
        apWidth = (t2 - t1)
        
        plt = self.model.graphOverlap(
            voltVec, timeVec, 'k', 'Full Spike', 0.8, volt, time, 'g', 'AP', 1.0, 'AP Width')
        self.model.graphMarker(plt, TPeak, vPeak, 'AP Peak', 'x')
        self.model.graphMarker(plt, tRest, vRest, 'AP Resting', 'x')
        self.model.graphMarker(plt, t1, m1, 'AP half1', 'x')
        self.model.graphMarker(plt, t2, m2, 'AP half2', 'x')

        plt.show()
        print(f'apWidth: {apWidth} ms')
        return apWidth

    def closeMatches(self, lst: list, findVal, tolerance):
        # TODO: complete docs 
        """ find a list of closest matches to a specific value with a spicified tolerance 
            Args:
                :param lst: 
                :param findVal: 
                :param tolerance:
            :return: list of (value,index) pairs 
        """
        matches = [(val,index) for index,val in enumerate(lst) if (findVal - tolerance) < val < (findVal + tolerance)]

        return matches


if __name__ == '__main__':

    modelRun = FiveCompModel()
    # modelRun.inputResistance(-0.5,True,True)

    testAmps = [-0.5, -0.6, -0.7, -0.8, -0.9, -1.0]
    # modelRun.avgInRes(testAmps, True, False)

    # tau = modelRun.timeConstant(-0.5)
    volt, t = modelRun.generateSpike(10, 6, 150, modelRun.iseg, 0.5, 500)
    # plt = modelRun.model.graphVolt(volt, t, "AP")
    # plt.show()
    width = modelRun.APWidth(volt, t, 150, 5)
    # print(f'Tau: {tau} ms')

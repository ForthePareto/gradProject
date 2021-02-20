from NrnModel import NrnModel, Level
import math
import numpy as np
from xlwt import Workbook
import time
from neuron import h


PLOTTING = False
PRINTING = False


class FiveCompModel():
    def __init__(self,):

        self.model = NrnModel("5CompMy_temp.hoc")
        self.soma = self.model.soma
        self.iseg = self.model.iseg
        self.EXPRIMENTAL_DATA = np.array([["input resistance", 1.26],
                                          ['AP Height', 81.48],
                                          ["AP Width", 1.02],
                                          ["AHP Depth", 5.31],
                                          ["AHP Duration", 64.82],
                                          ["AHP Half-Duration", 36.82],
                                          ["AHP Half-Decay", 26.75],
                                          ["AHP Rising-Time", 11.27],
                                          ["Rheobase", 7.88]])
        self.measurements = np.zeros((9))
        
        # self.Parmeters_boundaries = {"conductance": [0, 1]}
        # self.xlSheet = None
        # self.row = None
        # self.col = None
        # self.xlSheetInit()

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
        stim = self.model.setIClamp(
            delay, duration, clampAmp, segment=stimSeg, position=clampAt)
        volt, t = self.model.recordVolt(self.model.soma, 0.5)
        self.model.runControler(TStop=Tstop, init=-65)

        return volt, t

    def inputResistance(self, amp, plotting=PLOTTING, printing=PRINTING):
        """ Measures the input resistance
            Args:
                :param amp: current amplitude used to stimulate the cell
                :param plotting: Boolean used to toggle plotting on and off
                :param printing: Boolean used to toggle printing on and off
            :return inputResistance: input Resistance


        """
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

        if printing:
            print("----- Input Resistance Measurement -----")
            print(f'clamp Current: {amp} nA')
            print(f'restMembPot: {restMembPot} mV')
            print(f'minDepolarPot: {minDepolarPot} mV')
            print(f'inputResistance: {inputResistance} (mV/nA)')
            print("----- ---------------------------- -----")
            # self.xlSheet.write(1,0,"Input Resistance")
            # self.xlSheetWriteRows("Input Resistance")
            # self.xlSheetWriteCols(inputResistance)

        if plotting:
            # TODO: overlay plots , plot full graph and the sliced with diff color ,  and mark points on the graph
            # ::DONE::
            plt = self.model.graphOverlap(
                volt, t, 'k', 'Full Spike', 0.8, slicedVolt, slicedT, 'g', 'Sliced spike', 1.0, 'input Resistance')
            plt.show()
        return inputResistance

    def avgInRes(self, sampleAmps, plotting=PLOTTING, printing=PRINTING):
        """ Measures the average input resistance over many samples
            Args:
                :param sampleAmps: List of current amplitudes used to stimulate the cell
                :param plotting: Boolean used to toggle plotting on and off
                :param printing: Boolean used to toggle printing on and off
            :return avgInRes: average input Resistance


        """
        inputRes = [self.inputResistance(
            amp, plotting=PLOTTING, printing=PRINTING) for amp in sampleAmps]
        avgInRes = sum(inputRes)/len(inputRes)

        if printing:
            print("----- Averaged Input Resistance  -----\n")
            # print(f'inputRes List: \n{inputRes}\n')
            print(f'avgInRes: {avgInRes} (mV/nA)')
            print("----- ---------------------------- -----\n")

        return avgInRes

    def timeConstant(self, amp, plotting=PLOTTING, printing=PRINTING):
        """ Measures the time constant
            Args:
                :param amp: List of current amplitudes used to stimulate the cell
                :param plotting: Boolean used to toggle plotting on and off
                :param printing: Boolean used to toggle printing on and off

            :return tC: time constant
        """
        delay = 150
        duration = 100
        volt, t = self.stimulateCell(amp, duration=duration, delay=delay,
                                     stimSeg=self.model.soma, clampAt=0.5, Tstop=500)
        tStart = delay + duration
        # TODO: make a function that detects stable intervales and use it in time constant function
        tEnd = delay + duration + 30

        slicedVolt, slicedTime = self.sliceSpikeGraph(volt, t, tStart, tEnd)
        # slicedVolt, slicedTime,plt = self.patternHighligher(volt,t,tStart,duration,plotting = True)

        vStart = slicedVolt[0]
        vEnd = slicedVolt[-1]
        tC = -(tEnd - tStart) / math.log(1 - (vEnd/vStart))

        if printing:
            print(f'Time Constant: {tC}')
            # print(f'vStart: {vStart}')
            # print(f'vEnd: {vEnd}')
            # print(f'tStart: {tStart}')
            # print(f'tEnd: {tEnd}')
        if plotting:
            plt = self.model.graphOverlap(volt, t, 'k', 'Full Spike', 0.8,
                                          slicedVolt, slicedTime, 'g', 'Sliced spike', 1.0, 'Time Constant')
            # self.model.graphMarker(plt,tStart,vStart,'start Point')
            plt.show()
        return tC

    def APHeight(self, voltVec, timeVec, delay, duration, plotting=PLOTTING, printing=PRINTING):
        """ measures the AP Height of the spike
            Args:
                :param voltVec: recoreded vector of the spike voltage
                :param timeVec: recoreded vector of the spike time
                :param delay: the time at which the cell is stimulated
                :param duration: the time for which the stimulation is continued
                :param plotting: Boolean used to toggle plotting on and off
                :param printing: Boolean used to toggle printing on and off

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

        if printing:
            print(f'apHeight: {apHeight} mV')

        if plotting:
            plt = self.model.graphOverlap(voltVec, timeVec, 'k', 'Full AP', 0.8,
                                          volt, time, 'g', 'AP Spike', 1.0, 'AP Height')

            self.model.graphMarker(plt, TPeak, vPeak, 'AP Peak', 'x')
            self.model.graphMarker(plt, tRest, vRest, 'AP Resting', 'x')

        return apHeight, vRest, vPeak

    def APWidth(self, voltVec, timeVec, delay, duration, plotting=PLOTTING, printing=PRINTING):
        # FIXME: matches aren't aon the same level , but close enough ... (works for me)
        """ measures the AP width of the spike

                :param voltVec: recoreded vector of the spike voltage
                :param timeVec: recoreded vector of the spike time
                :param delay: the time at which the cell is stimulated
                :param duration: the time for which the stimulation is continued
                :param plotting: Boolean used to toggle plotting on and off
                :param printing: Boolean used to toggle printing on and off

            :return : the width of the spike in milliSecs

        """
        # TODO: find the end of the spike with the interval function that will be done later
        # volt, time = self.sliceSpikeGraph(voltVec, timeVec, delay, delay + 10)
        volt, time, plt = self.patternHighligher(
            voltVec, timeVec, delay, duration, False)
        apHeight, vRest, vPeak = self.APHeight(
            voltVec, timeVec, delay, duration, False, False)
        # calculate the mid point
        apHalfV = (apHeight / 2) + vRest

        # find actual matches
        matches = self.closeMatches(volt, apHalfV, 5)
        matches = list(zip(*matches))
        # print(f'matches {matches}')
        vMatches = matches[0]
        indexMatches = matches[-1]

        m1 = vMatches[0]
        m2 = vMatches[-1]
        t1 = time[indexMatches[0]]
        t2 = time[indexMatches[-1]]

        apWidth = (t2 - t1)
        if plotting:
            plt = self.model.graphOverlap(voltVec, timeVec, 'k', 'Full AP', 0.8,
                                          volt, time, 'g', 'AP Spike', 1.0, 'AP Width')

            self.model.graphMarker(plt, t1, m1, 'AP half1', 'x')
            self.model.graphMarker(plt, t2, m2, 'AP half2', 'x')

            plt.show()
        if printing:
            # print(f'vRest {vRest} mV')
            # print(f'apHalfV {apHalfV} mV')
            print(f'apWidth: {apWidth} ms')
        return apWidth

    def AHPDepth(self, voltVec, timeVec, delay, duration, plotting=PLOTTING, printing=PRINTING):
        """ Calculate the depth of the AHP phase in mV

        Args:
            :param voltVec: recoreded vector of the spike voltage
            :param timeVec: recoreded vector of the spike time
            :param delay: the time at which the stimulation is started
            :param duration: the time for which the stimulation is continued
            :param plotting: Boolean used to toggle plotting on and off
            :param printing: Boolean used to toggle printing on and off


        :return AHPDepth:depth of the AHP phase in mV

        """
        volt, t, plt = self.patternHighligher(
            voltVec, timeVec, delay, duration, plotting=PLOTTING, reverse=True)
        AHPStartV = volt[0]
        AHPPeakV = min(volt)
        AHPStartT = t[0]
        AHPPeakT = t[volt.index(AHPPeakV)]
        AHPDepthV = abs(AHPPeakV - AHPStartV)

        if plotting:
            self.model.graphMarker(
                plt, AHPPeakT, AHPPeakV, 'AHP PEAK', markerShape='x')
            self.model.graphMarker(
                plt, AHPStartT, AHPStartV, 'AHP Start', markerShape='x')

            plt.title('AHP Depth')
            plt.show()
        if printing:
            print(f'AHPDepthV :{AHPDepthV} mV')
        return AHPDepthV

    def AHPDuration(self, voltVec, timeVec, delay, duration, plotting=PLOTTING, printing=PRINTING):
        """ Calculate the duration of the AHP phase in mSec

        Args:
            :param voltVec: recoreded vector of the spike voltage
            :param timeVec: recoreded vector of the spike time
            :param delay: the time at which the stimulation is started
            :param duration: the time for which the stimulation is continued
            :param plotting: Boolean used to toggle plotting on and off
            :param printing: Boolean used to toggle printing on and off

        :return AHPDuration:duration of the AHP phase in mSec
        """
        volt, t, plt = self.patternHighligher(
            voltVec, timeVec, delay, duration, plotting=PLOTTING, reverse=True)

        AHPStartV = volt[0]
        AHPStartT = t[0]

        AHPEndV = volt[-1]
        AHPEndT = t[-1]
        AHPDuration = AHPEndT - AHPStartT

        if plotting:
            self.model.graphMarker(
                plt, AHPStartT, AHPStartV, 'AHP Start', markerShape='x')
            self.model.graphMarker(plt, AHPEndT, AHPEndV,
                                   'AHP End', markerShape='x')

            plt.title('AHP Duration')
            plt.show()
        if printing:
            print(f'AHPDuration: {AHPDuration} mSecs')
        return AHPDuration

    def AHPHalfDuration(self, voltVec, timeVec, delay, duration, plotting=PLOTTING, printing=PRINTING):
        """ Calculate the half-duration of the AHP phase in mSec

        Args:
            :param voltVec: recoreded vector of the spike voltage
            :param timeVec: recoreded vector of the spike time
            :param delay: the time at which the stimulation is started
            :param duration: the time for which the stimulation is continued
            :param plotting: Boolean used to toggle plotting on and off
            :param printing: Boolean used to toggle printing on and off

        :return AHPHalfDuration:half duration of the AHP phase in mSec
        """
        volt, t, plt = self.patternHighligher(
            voltVec, timeVec, delay, duration, plotting=PLOTTING, reverse=True)

        AHPStartV = volt[0]
        AHPPeakV = min(volt)
        # print(f'AHPPeakV :{AHPPeakV}')
        # print(f'AHPStartV :{AHPStartV}')

        AHPHalfV = ((AHPPeakV - AHPStartV) / 2) + AHPStartV
        # find close matches to the exact value of {AHPHalfV}
        matches = self.closeMatches(volt, AHPHalfV, 0.05)
        matches = list(zip(*matches))
        if printing:
            print(f'AHPHalfV :{AHPHalfV}')
            # print(f'matches {matches}')
        matchesV, matchesT = matches
        # left point
        v1 = matchesV[0]
        t1 = t[matchesT[0]]

        # right point
        v2 = matchesV[-1]
        t2 = t[matchesT[-1]]

        AHPHalfDuration = t2 - t1
        if plotting:
            self.model.graphMarker(
                plt, t1, v1, 'AHP half-left', markerShape='x')
            self.model.graphMarker(
                plt, t2, v2, 'AHP half.right', markerShape='x')
            plt.show()
        if printing:
            print(f'AHPHalfDuration: {AHPHalfDuration} mSecs')
        return AHPHalfDuration

    def AHPHalfDecay(self, voltVec, timeVec, delay, duration, plotting=PLOTTING, printing=PRINTING):
        """ Calculate the half-decay of the AHP phase in mSec

        Args:
            :param voltVec: recoreded vector of the spike voltage
            :param timeVec: recoreded vector of the spike time
            :param delay: the time at which the stimulation is started
            :param duration: the time for which the stimulation is continued
            :param plotting: Boolean used to toggle plotting on and off
            :param printing: Boolean used to toggle printing on and off

        :return AHPHalfDecay:half decay of the AHP phase in mSec
        """
        volt, t, plt = self.patternHighligher(
            voltVec, timeVec, delay, duration, plotting=PLOTTING, reverse=True)

        AHPStartV = volt[0]
        AHPPeakV = min(volt)
        AHPPeakT = t[volt.index(AHPPeakV)]

        AHPHalfV = ((AHPPeakV - AHPStartV) / 2) + AHPStartV
        # print(f'AHPHalfV :{AHPHalfV}')

        # find close matches to the exact value of {AHPHalfV}
        matches = self.closeMatches(volt, AHPHalfV, 0.005)
        matches = list(zip(*matches))
        # print(f'matches {matches}')
        matchesV, matchesT = matches

        # right point
        AHPHalfVLeft = matchesV[-1]
        AHPHalfTLeft = t[matchesT[-1]]

        AHPHalfDecay = AHPHalfTLeft - AHPPeakT
        if plotting:
            self.model.graphMarker(
                plt, AHPHalfTLeft, AHPHalfVLeft, 'AHP half-left', markerShape='x')
            self.model.graphMarker(
                plt, AHPPeakT, AHPPeakV, 'AHP Peak', markerShape='x')

            plt.title('AHP Half-Decay')
            plt.show()
        if printing:
            print(f'AHPHalfDecay: {AHPHalfDecay} mSecs')
        return AHPHalfDecay

    def AHPRisingTime(self, voltVec, timeVec, delay, duration, plotting=PLOTTING, printing=PRINTING):
        """ Calculate the Rising Time of the AHP phase in mSec

            Args:
                :param voltVec: recoreded vector of the spike voltage
                :param timeVec: recoreded vector of the spike time
                :param delay: the time at which the stimulation is started
                :param duration: the time for which the stimulation is continued
                :param plotting: Boolean used to toggle plotting on and off
                :param printing: Boolean used to toggle printing on and off

            :return AHPRisingTime: Rising Time of the AHP phase in mSec
        """
        volt, t, plt = self.patternHighligher(
            voltVec, timeVec, delay, duration, plotting=PLOTTING, reverse=True)

        AHPStartV = volt[0]
        AHPStartT = t[0]

        AHPPeakV = min(volt)
        AHPPeakT = t[volt.index(AHPPeakV)]

        AHPRisingTime = AHPPeakT - AHPStartT
        if plotting:
            self.model.graphMarker(
                plt, AHPPeakT, AHPPeakV, 'AHP PEAK', markerShape='x')
            self.model.graphMarker(
                plt, AHPStartT, AHPStartV, 'AHP Start', markerShape='x')
            plt.title('AHP-Rising Time')
            plt.show()
        if printing:
            print(f'AHPRisingTime :{AHPRisingTime} mSecs')
        return AHPRisingTime

    def Rheobase(self, accuracy, refineTimes: int, plotting=PLOTTING, printing=PRINTING, duration=50, delay=150):
        """ Calculate Rheobase current of the cell in nA
            Args:
                :param accuracy: accuracy level {Level.HIGH, Level.MID, Level.LOW,Level.VLOW}
                :param refineTimes: number of repeation, the higher, the more accurate the Rheobase
                :param plotting: Boolean used to toggle printing on and off
                :param printing: Boolean used to toggle printing on and off
                :param duration: the time for which the stimulation is continued (should be +50 ms)
                :param delay: the time at which the stimulation is started

            :return rheobase: Calculate Rheobase current of the cell in nA
        """
        rheobase_steps = False
        start = 1
        end = 20
        step = 1
        while refineTimes:

            for current in np.arange(start, end, step):
                volt, t = self.stimulateCell(
                    current, duration, delay, self.soma, 0.5, 500)
                if self.isSpike(volt, t, delay, duration, accuracy, plotting=PLOTTING):

                    start = current - step
                    end = current
                    if printing and rheobase_steps:
                        print(f'in Range [{start},{end}] ')
                        print(f'at current: {current}')
                    step = step / 10
                    break

            refineTimes -= 1
        rheobase = end
        if printing:
            print(f'rheobase {rheobase} nA')
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
        """ find a list of closest matches to a specific value with a spicified tolerance
            Args:
                :param lst: target list to search into
                :param findVal: target value
                :param tolerance: accepted error in matches
            :return: list of (value,index) pairs
        """
        # matches = [(val,index) for index,val in enumerate(lst) if abs(val - findVal) < tolerance]
        matches = [(val, index) for index, val in enumerate(lst)
                   if math.isclose(val, findVal, abs_tol=tolerance)]

        return matches

    def patternHighligher(self, voltVec, timeVec, delay, duration, plotting=PLOTTING, restingVolt=-65, reverse=False):
        """ Detects the up-down shape of the spike and extracts it
            Args:
                :param voltVec: recoreded vector of the spike voltage
                :param timeVec: recoreded vector of the spike time
                :param delay: the time at which the stimulation is started
                :param duration: the time for which the stimulation is continued
                :param plotting: Boolean used to toggle plotting on and off



            :return spikeVolt: list of the spike voltage values
            :return spikeTime: list of the spike time values
            :return plt: matplotlib class member (graph handler,used to overlay on top old graphs)

         """
        volt, t = self.sliceSpikeGraph(
            voltVec, timeVec, delay, delay + duration + 70)
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
                if (v < spikeVolt[-1]) and (v <= restingVolt) and stillDown:
                    spikeVolt += [v]
                    stillUp = True
                elif (v > spikeVolt[-1]) and (v <= restingVolt) and stillUp:
                    stillDown = False
                    spikeVolt += [v]
                else:
                    stillUp = False

        startIndex = volt.index(spikeVolt[0])
        endIndex = volt.index(spikeVolt[-1])
        spikeTime = t[startIndex:endIndex + 1]

        # resize both list to match dimenstions
        spikeVolt, spikeTime = self.matchSize(spikeVolt, spikeTime)
        plt = None
        if plotting:
            plt = self.model.graphOverlap(voltVec, timeVec, 'k', "Full AP", 0.2,
                                          spikeVolt, spikeTime, 'r', label, 1.0, title)
            # plt.show()

        return spikeVolt, spikeTime, plt

    def matchSize(self, lst1, lst2):
        # resize both list to match dimenstions
        len1 = len(lst1)
        len2 = len(lst2)
        if len1 != len2:
            minLen = min(len1, len2)
            lst1 = lst1[:minLen]
            lst2 = lst2[:minLen]
        return lst1, lst2

    def isSpike(self, voltVec, timeVec, delay, duration, accuracy: Level, plotting=PLOTTING) -> bool:
        """ detect if there is a spike

        Args:
            :param voltVec: recoreded vector of the spike voltage
            :param timeVec: recoreded vector of the spike time
            :param delay: the time at which the stimulation is started
            :param duration: the time for which the stimulation is continued
            :param accuracy: accuracy level {Level.HIGH, Level.MID, Level.LOW,Level.VLOW}
            :param plotting: Boolean used to toggle plotting on and off

        :return bool: true if spike and false otherwise
         """
        volt, t, plt = self.patternHighligher(
            voltVec, timeVec, delay, duration, plotting)
        if plotting:
            plt.close()
        return (abs(max(volt) - min(volt)) >= accuracy.value)


########################################################################
########################################################################


########################################################################
##################         Parameter setters         ###################
##################          in trash phase           ###################
########################################################################

    def setCellParams(self, params: list):
        # self.model.g_pas, self.model.gnabar_NafSmb1, self.model.gkdrbar_KdrSmb1, self.model.gkcabar_CaSmb1, self.model.gcanbar_CaSmb1, self.model.gcalbar_CaSmb1, \
        #     h.th_NafSmb1, h.amA_NafSmb1, h.bmA_NafSmb1, h.theta_h_NafSmb1, h.theta_n_KdrSmb1, \
        #     h.thetamn_CaSmb1, h.thetahn_CaSmb1, h.f_CaSmb1, h.alpha_CaSmb1, h.kca_CaSmb1, h.kd_CaSmb1, h.nexp_CaSmb1 = tuple(
        #         params)
        self.model.g_pas, self.model.gnabar_NafSmb1, self.model.gkdrbar_KdrSmb1, self.model.gkcabar_CaSmb1, self.model.gcanbar_CaSmb1, self.model.gcalbar_CaSmb1 = tuple(params)


    def somaParams(self):

        print(self.model.soma.g_pas)
        print(self.model.soma.gnabar_NafSmb1)
        print(self.model.soma.gkdrbar_KdrSmb1)
        print(self.model.soma.gkcabar_CaSmb1)
        print(self.model.soma.gcanbar_CaSmb1)
        print(self.model.soma.gcalbar_CaSmb1)
        print(h.th_NafSmb1)
        print(h.amA_NafSmb1)
        print(h.bmA_NafSmb1)
        print(h.theta_h_NafSmb1)
        print(h.theta_n_KdrSmb1)
        print(h.thetamn_CaSmb1)
        print(h.thetahn_CaSmb1)
        print(h.f_CaSmb1)
        print(h.alpha_CaSmb1)
        print(h.kca_CaSmb1)
        print(h.kd_CaSmb1)
        print(h.nexp_CaSmb1)

########################################################################
########################################################################
    def get_exprimental_data(self): 
        """get_exprimental_data [A getter for model's experimental data (measurments only without discription)]

        Returns:
            [numpy.array]
        """
        return self.EXPRIMENTAL_DATA[:, 1].astype(np.float)

    def get_parameters_boundaries(self):
        boundaries = np.array([[0, 1]]*6)
        # boundaries = np.array([[0, 1]]*12)
        # boundaries = np.concatenate(
        #     (np.array([[0, 1]]*6), np.array([[0, 130]]*12)))
        return boundaries

    def get_measurements(self):
        delay = 150
        duration = 1
        current = 21
        rIn = self.inputResistance(-0.5,
                                   plotting=False, printing=False)
        volt, t = self.stimulateCell(
            current, duration, delay, self.iseg, 0.5, 500)
        APHeight, rest, peak = self.APHeight(
            volt, t, delay, duration, plotting=False, printing=False)

        APWidth = self.APWidth(
            volt, t, delay, duration, plotting=False, printing=False)

        AHPDepth = self.AHPDepth(
            volt, t, delay, duration, plotting=False, printing=False)

        AHPDuration = self.AHPDuration(
            volt, t, delay, duration, plotting=False, printing=False)

        AHPHalfDuration = self.AHPHalfDuration(
            volt, t, delay, duration, plotting=False, printing=False)

        AHPHalfDecay = self.AHPHalfDecay(
            volt, t, delay, duration, plotting=False, printing=False)

        AHPRisingTime = self.AHPRisingTime(
            volt, t, delay, duration, plotting=False, printing=False)

        Rheobase = self.Rheobase(
            Level.VLOW, 1, plotting=False, printing=False)
        self.measurements = np.array( [rIn, APHeight, APWidth, AHPDepth, AHPDuration,
            AHPHalfDuration, AHPHalfDecay, AHPRisingTime, Rheobase]).astype(np.float)
        print("\n Measurements: ",self.measurements)
        return self.measurements


if __name__ == '__main__':

    def xlSheetInit():
        """ Initializes the exel sheet to write into """
        col = 1
        row = 1
        # Workbook is created
        wb = Workbook()
        # add_sheet is used to create sheet.
        xlSheet = wb.add_sheet('Feature Measurments')
        return xlSheet, wb, row, col

    def xlSheetWriteCols(xlSheet, row, col, item):

        xlSheet.write(row-1, 1, item)
        return col

    def xlSheetWriteRows(xlSheet, row, col, item):
        xlSheet.write(row, 0, item)
        return (row+1)

    def testRun(plotting: bool, printing: bool, save_to_file: bool):
        modelRun = FiveCompModel()
        # modelRun.somaParams()
        modelRun.setCellParams(np.ones(18))
        rIn = modelRun.inputResistance(-0.5,
                                       plotting=plotting, printing=printing)

        # testAmps = [-0.5, -0.6, -0.7, -0.8, -0.9, -1.0]
        # avgRin = modelRun.avgInRes(
        #     testAmps, plotting=plotting, printing=printing)

        # tau = modelRun.timeConstant(-0.5, plotting=plotting, printing=printing)

        delay = 150
        duration = 1
        current = 21
        volt, t = modelRun.stimulateCell(
            current, duration, delay, modelRun.iseg, 0.5, 500)
        plt = modelRun.model.graphVolt(volt,t,"AP")
        plt.show()
        # # res = modelRun.isSpike(volt,t,delay,,Level.HIGH,duration)
        # # print(f'Is Spike: {res}')
        APHeight, rest, peak = modelRun.APHeight(
            volt, t, delay, duration, plotting=plotting, printing=printing)

        APWidth = modelRun.APWidth(
            volt, t, delay, duration, plotting=plotting, printing=printing)

        AHPDepth = modelRun.AHPDepth(
            volt, t, delay, duration, plotting=plotting, printing=printing)

        AHPDuration = modelRun.AHPDuration(
            volt, t, delay, duration, plotting=plotting, printing=printing)

        AHPHalfDuration = modelRun.AHPHalfDuration(
            volt, t, delay, duration, plotting=plotting, printing=printing)

        AHPHalfDecay = modelRun.AHPHalfDecay(
            volt, t, delay, duration, plotting=plotting, printing=printing)

        AHPRisingTime = modelRun.AHPRisingTime(
            volt, t, delay, duration, plotting=plotting, printing=printing)

        Rheobase = modelRun.Rheobase(
            Level.VLOW, 5, plotting=plotting, printing=printing)

        if save_to_file:
            xlSheet, wb, row, col = xlSheetInit()
            row = xlSheetWriteRows(
                xlSheet, row, col, "input Resistance (mV/nA)")
            col = xlSheetWriteCols(xlSheet, row, col, round(rIn, 2))

            row = xlSheetWriteRows(
                xlSheet, row, col, "Average input Resistance (mV/nA)")
            col = xlSheetWriteCols(xlSheet, row, col, round(avgRin, 2))

            row = xlSheetWriteRows(xlSheet, row, col, "time Constant (ms)")
            col = xlSheetWriteCols(xlSheet, row, col, round(tau, 2))

            row = xlSheetWriteRows(xlSheet, row, col, "AP Height (mV)")
            col = xlSheetWriteCols(xlSheet, row, col, round(APHeight, 2))

            row = xlSheetWriteRows(xlSheet, row, col, "AP Width (ms)")
            col = xlSheetWriteCols(xlSheet, row, col, round(APWidth, 2))

            row = xlSheetWriteRows(xlSheet, row, col, "AHP Depth (mV)")
            col = xlSheetWriteCols(xlSheet, row, col, round(AHPDepth, 2))

            row = xlSheetWriteRows(xlSheet, row, col, "AHP Duration (ms)")
            col = xlSheetWriteCols(xlSheet, row, col, round(AHPDuration, 2))

            row = xlSheetWriteRows(xlSheet, row, col, "AHP Half-Duration (ms)")
            col = xlSheetWriteCols(
                xlSheet, row, col, round(AHPHalfDuration, 2))

            row = xlSheetWriteRows(xlSheet, row, col, "AHP Half-Decay (ms)")
            col = xlSheetWriteCols(xlSheet, row, col, round(AHPHalfDecay, 2))

            row = xlSheetWriteRows(xlSheet, row, col, "AHP Rising-Time (ms)")
            col = xlSheetWriteCols(xlSheet, row, col, round(AHPRisingTime, 2))

            row = xlSheetWriteRows(xlSheet, row, col, "Rheobase (nA)")
            col = xlSheetWriteCols(xlSheet, row, col, round(Rheobase, 2))
            wb.save('measurementsEslam.xls')

        # #spikeV,spikeT,plt = modelRun.patternHighligher(volt,t,-65,150,6,reverse=False)
        # # spikeV,spikeT,plt = modelRun.patternHighligher(volt,t,-65,150,6,reverse=True)
        # # print(spikeV)
        # # plt = modelRun.model.graphOverlap(volt, t, 'k',"Full AP",0.8,
        # #                                 spikeV,spikeT,'r',"Spike",1.0,"SPIKE Pattern")
        # # plt.show()
        # # width = modelRun.APWidth(volt, t, 150, 5)
        # # print(f'Tau: {tau} ms')

        # wb.save('measurements.xls')

    start_time = time.time()
    testRun(plotting=True, printing=True, save_to_file=False)
    print("Measurements are done in--- %s seconds ---" %
          (time.time() - start_time))

    # model = FiveCompModel()
    # model.somaParams()

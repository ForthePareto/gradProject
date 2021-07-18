from NrnModel import NrnModel
import efel
import matplotlib.pyplot as plt
import numpy as np
import math


class EfelMeasurements():
    def __init__(self, model=None, modelHocFile: str = "5CompMy_temp.hoc"):

        self.model = model if(model is not None) else NrnModel(modelHocFile)
        self.soma = self.model.soma
        self.iseg = self.model.iseg
        self.trace = {}

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

    def stimulateCell(self, clampAmp, duration, delay, stimSeg, clampAt, Tstop, init=-65):
        """ Stimulate the cell with the supplied properties
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
        self.volt, self.t = volt, t
        import numpy as np
        temp = []
        # print(int(volt.size()))
        # for n in range(int(volt.size())):
        #     temp.append(volt.x[n])
        # print(np.array(temp))
        # print(len(temp))
        # self.model.graphVolt(volt, t,"trace").show()
        # print( self.closeMatches(t,delay,0.7))
        start =  sorted(self.closeMatches(t,delay,0.025),key=lambda x: x[0])[0][0]        
        end =  sorted(self.closeMatches(t,delay+duration,0.025),key=lambda x: x[0])[0][0]         
        # print(t[2]-t[1])
        print(start)
        print(end)
        self.trace['T'] = t
        self.trace['V'] = volt
        # self.trace['stim_start'] = [delay-10]
        # self.trace['stim_end']  = [500]
        self.trace['stim_start'] = [start]
        self.trace['stim_end'] = [delay+5]

        return volt, t

    def getMeasurements(self, featureNames: list):
        traces = [self.trace]

        traces_results = efel.getFeatureValues(traces, featureNames)

        # The return value is a list of trace_results, every trace_results
        # corresponds to one trace in the 'traces' list above (in same order)
        for trace_results in traces_results:
            # trace_result is a dictionary, with as keys the requested eFeatures
            for feature_name, feature_values in trace_results.items():
                print("Feature %s has the following values: %s" %
                      (feature_name, ', '.join([str(x) for x in feature_values])))


if __name__ == '__main__':

    fig, ax = plt.subplots()
    for i in range(1):
        delay = 150  # 150
        duration = 1
        current = 21
        efel.setDoubleSetting('stimulus_current', current)
        # efel.setDoubleSetting('interp_step', 0.025)
        # efel.setIntSetting("strict_stiminterval", True)

        testEFEL = EfelMeasurements()
        testEFEL.stimulateCell(current, duration, delay,
                               testEFEL.iseg, 0.5, 500)
        testEFEL.getMeasurements(["Spikecount", "time_to_first_spike", "AP_amplitude",
                                  "AP_height", 'AP_width', 'AHP_depth_abs', "AHP_time_from_peak"])

        testEFEL.model.graphVolt(
            testEFEL.volt, testEFEL.t, "trace", ax, color=np.random.rand(3,))
        # ax.set_color("red")
    plt.show()

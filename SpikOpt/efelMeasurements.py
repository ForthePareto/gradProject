from NrnModel import NrnModel
import efel
import matplotlib.pyplot as plt
import numpy as np
import math
from collections import OrderedDict


EFEL_NAME_MAP = {"Input Resistance": "ohmic_input_resistance",
                 "AP Amplitude": "AP_amplitude",
                 "AP Height": "AP_height",
                 "AP Width": "AP_width",
                 "AHP Absolute Depth": "AHP_depth_abs",
                 "AHP Duration": "AHPDuration",
                 "AHP time from peak": "AHP_time_from_peak",
                 "Spikecount": "Spikecount",
                 "Time to First Spike": "time_to_first_spike",
                 }
EFEL2NAME_MAP = {v: k for k, v in EFEL_NAME_MAP.items()}


def _zero_valued_dict(keys):
    return dict.fromkeys(keys, 0)


class EfelMeasurements():
    def __init__(self, model, config):

        self.cell = model
        self.volt = None
        self.t = None
        self.delay = None
        self.duration = None
        self.Tstop = None
        self._setup(config)
        self.trace = {}

    def setup(self, config):
        self.volt, self.t = self.cell.stimulateCell(
            float(config["Amplitude"]), float(
                config["Duration"]), float(config["Delay"]),
            float(
                config["T stop"]), config["Stimulus Section"], config["Recording Section"],
            clampAt=float(config["Stimulus Position"]), recordAt=float(config["Recording Position"]), init=float(config["Vinit"]))
        self.delay = float(config["Delay"])
        self.duration = float(config["Duration"])
        self.Tstop = float(config["T stop"])

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

        # start =  sorted(self.closeMatches(self.t,delay,0.025),key=lambda x: x[0])[0][0]
        # end =  sorted(self.closeMatches(self.t,delay+duration,0.025),key=lambda x: x[0])[0][0]
        # print(t[2]-t[1])
        efel.setDoubleSetting('stimulus_current', current)
        efel.setIntSetting("strict_stiminterval", True)
        self.trace['T'] = self.t
        self.trace['V'] = self.volt
        # self.trace['stim_start'] = [delay-10]
        # self.trace['stim_end']  = [500]
        self.trace['stim_start'] = [self.delay]
        self.trace['stim_end'] = [self.Tstop]

        return self.volt, self.t

    def getMeasurements(self, featureNames: list):
        traces = [self.trace]
        efel_feature_names = []
        for fName in featureNames:
            if fName not in list(EFEL_NAME_MAP.keys()):
                raise ValueError(
                    f" Feature: '{fName}' is not availabe in Efel or not spelled well")
            efel_feature_names.append(EFEL_NAME_MAP[fName])

        traces_results = efel.getFeatureValues(traces, efel_feature_names)
        self.measurements = OrderedDict()
        check_peaks = efel.getFeatureValues(traces, ["Spikecount_stimint"])
        if check_peaks[0]["Spikecount_stimint"][0] == 0:
            return _zero_valued_dict(featureNames)

        traces_results = efel.getFeatureValues(traces, efel_feature_names)
        if traces_results[0]["AP_amplitude"] is None:
            # print("efel failed",len(traces_results[0]["AP_amplitude"]) , len(traces_results[0]["AP_height"]))
            print(f"n spikes are {check_peaks[0]['Spikecount_stimint'][0]}")
            return _zero_valued_dict(featureNames)

        for trace_results in traces_results:
            # trace_result is a dictionary, with as keys the requested eFeatures

            for feature_name, feature_values in trace_results.items():

                if len(feature_values) > 0:

                    self.measurements[EFEL2NAME_MAP[feature_name]
                                      ] = feature_values[0]
                else:
                    print(f"{feature_name} failed")
                    self.measurements[EFEL2NAME_MAP[feature_name]] = 0

        return self.measurements


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

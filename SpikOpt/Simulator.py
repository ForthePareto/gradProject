from NrnModel import NrnModel
import math
import numpy as np
# from xlwt import Workbook
import time
from neuron import h
from efelMeasurements import EfelMeasurements
import efel
from collections import OrderedDict
from Model import Plotter, Level

PLOTTING = False
PRINTING = False
SUPPORTED_MODEL_TYPES = ['Nmodel']


class Simulator():
    def __init__(self, model_type: str, model_file: str, model_name: str):
        if model_type == "Nmodel":
            self.model = NrnModel(model_file, model_name)
        else:
            raise NotImplementedError(
                f"only {SUPPORTED_MODEL_TYPES} are supported")
        # self.soma = self.model.soma
        # self.iseg = self.model.iseg
        # self.dendrites = self.model.dendrites
        self.EXPRIMENTAL_DATA = np.array([["input resistance", 1.26],
                                          ['AP Height', 81.48],
                                          ["AP Width", 1.02],
                                          ["AHP Depth", 5.31],
                                          ["AHP Duration", 64.82],
                                          ["AHP Half-Duration", 36.82],
                                          ["AHP Half-Decay", 26.75],
                                          ["AHP Rising-Time", 11.27],
                                          ["Rheobase", 7.88],
                                          ["time constant", 6.25]])
        # efel data
        self.EXPRIMENTAL_DATA = np.array(
            [["AP_amplitude", 80.414],
             ["AP_height", 14.527],
                ['AP_width', 0.8],
                ["AHP_depth_abs", -70.28],
                ["AHP_time_from_peak", 16.3],
             ])
        self.measurements = np.zeros((9))

        self.trace = {}

        # self.Parmeters_boundaries = {"conductance": [0, 1]}
        # self.xlSheet = None
        # self.row = None
        # self.col = None
        # self.xlSheetInit()
    def fetch_model_parameters(self) -> OrderedDict:
        return self.model.get_model_parameters()

    def fetch_model_channels(self) -> OrderedDict:
        return self.model.get_compartments_channels()

    


########################################################################
########################################################################


########################################################################
##################  Parameter setters,getters        ###################
##################                                   ###################
########################################################################
    # np_soma = 7
    # np_iseg = 4
    # np_dend1 = 1
    # np_dend2 = 2
    # np_dend3 = 1

    def setCellParams(self, params: list):
        # because gpas is proportinal in all segments dends = g_soma*(1/48)
        self.g_pas = params[0]
        self.setSomaParams(params[0:7])
        self.setIsegParams(params[7:11])
        self.setDend1Params(params[11:12])
        self.setDend2Params(params[12:14])
        self.setDend3Params(params[14:])

    def setPassiveParams(self, params: list):
        """
        set passive conductance to all compartments
        """
        self.g_pas = params[0]
        self.model.soma.g_pas = self.g_pas
        self.model.iseg.g_pas = self.g_pas
        self.model.dendrites[0].g_pas = self.g_pas / 48.9
        self.model.dendrites[1].g_pas = self.g_pas / 48.9
        self.model.dendrites[2].g_pas = self.g_pas / 48.9  # 1/11000

    def setNonPassiveParams(self, params: list):
        self.model.soma.gnabar_NafSmb1,\
            self.model.soma.gkdrbar_KdrSmb1,\
            self.model.soma.gkcabar_CaSmb1,\
            self.model.soma.gcanbar_CaSmb1,\
            self.model.soma.gcalbar_CaSmb1,\
            self.model.soma.ghbar_hb1 = tuple(params[0:6])

    def setSomaParams(self, params: list):
        # self.model.soma.g_pas, self.model.soma.gnabar_NafSmb1, self.model.soma.gkdrbar_KdrSmb1, self.model.soma.gkcabar_CaSmb1, self.model.soma.gcanbar_CaSmb1, self.model.soma.gcalbar_CaSmb1, \
        #     h.kd_CaSmb1, h.nexp_CaSmb1, h.f_CaSmb1, h.alpha_CaSmb1, h.th_NafSmb1, h.amA_NafSmb1, h.bmA_NafSmb1, h.theta_h_NafSmb1, h.theta_n_KdrSmb1, \
        #     h.thetamn_CaSmb1, h.thetahn_CaSmb1, h.kca_CaSmb1 = tuple(
        #         params)
        assert (len(params) == 7)
        self.model.soma.g_pas,\
            self.model.soma.gnabar_NafSmb1,\
            self.model.soma.gkdrbar_KdrSmb1,\
            self.model.soma.gkcabar_CaSmb1,\
            self.model.soma.gcanbar_CaSmb1,\
            self.model.soma.gcalbar_CaSmb1,\
            self.model.soma.ghbar_hb1 = tuple(params)

    def setIsegParams(self, params: list):
        assert (len(params) == 4)
        # 1/225
        # 0.001/7
        # 1.33
        # 3.2971e-5
        # 0.16552
        self.model.iseg.g_pas = self.g_pas
        self.model.iseg.ghbar_hb1, \
            self.model.iseg.gnabar_NafIsb1, \
            self.model.iseg.gnapbar_NapIsb1, \
            self.model.iseg.gkbar_KdrIsb1 = tuple(params)

    def setDend1Params(self, params: list):
        assert (len(params) == 1)
        # 1/11000
        # 0.002/7
        self.model.dendrites[0].g_pas = self.g_pas / 48.9
        self.model.dendrites[0].ghbar_hb1 = params[0]

    def setDend2Params(self, params: list):
        # 1/11000
        # 0.002/7
        # 0.00016
        assert (len(params) == 2)
        self.model.dendrites[1].g_pas = self.g_pas / 48.9
        self.model.dendrites[1].ghbar_hb1, \
            self.model.dendrites[1].gcaLlvabar_Llvab1 = tuple(params)

    def setDend3Params(self, params: list):
        assert (len(params) == 1)
        self.model.dendrites[2].g_pas = self.g_pas / 48.9  # 1/11000
        self.model.dendrites[2].ghbar_hb1 = params[0]      # 0.002/7

    def somaParams(self):
        print(self.model.soma.g_pas)
        print(self.model.soma.gnabar_NafSmb1)
        print(self.model.soma.gkdrbar_KdrSmb1)
        print(self.model.soma.gkcabar_CaSmb1)
        print(self.model.soma.gcanbar_CaSmb1)
        print(self.model.soma.gcalbar_CaSmb1)
        print(h.kd_CaSmb1)  # 0.0005
        print(h.nexp_CaSmb1)  # 1
        print(h.f_CaSmb1)  # 0.001
        print(h.alpha_CaSmb1)  # 1
        print(h.th_NafSmb1)
        print(h.amA_NafSmb1)
        print(h.bmA_NafSmb1)
        print(h.theta_h_NafSmb1)
        print(h.theta_n_KdrSmb1)
        print(h.thetamn_CaSmb1)
        print(h.thetahn_CaSmb1)
        print(h.kca_CaSmb1)


########################################################################
########################################################################

    def stimulate_efel_Cell(self, clampAmp, duration, delay, stimSeg, clampAt, Tstop, init=-65):
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

        self.trace['T'] = t
        self.trace['V'] = volt
        self.trace['stim_start'] = [delay-20]
        self.trace['stim_end'] = [500]
        return volt, t

    def print_EFEL_Measurements(self, featureNames: list):
        traces = [self.trace]

        traces_results = efel.getFeatureValues(traces, featureNames)

        # The return value is a list of trace_results, every trace_results
        # corresponds to one trace in the 'traces' list above (in same order)
        for trace_results in traces_results:
            # trace_result is a dictionary, with as keys the requested eFeatures
            for feature_name, feature_values in trace_results.items():
                print("Feature %s has the following values: %s" %
                      (feature_name, ', '.join([str(x) for x in feature_values])))

    def get_EFEL_measurements(self, featureNames):
        delay = 150
        duration = 1
        current = 21
        efel.setDoubleSetting('stimulus_current', current)
        efel.setIntSetting("strict_stiminterval", True)
        self.stimulate_efel_Cell(
            current, duration, delay, self.model.iseg, 0.5, 500)
        traces = [self.trace]
        check_peaks = efel.getFeatureValues(traces, ["Spikecount_stimint"])
        if check_peaks[0]["Spikecount_stimint"][0] == 0:
            return np.zeros(len(featureNames))
        traces_results = efel.getFeatureValues(traces, featureNames)
        if traces_results[0]["AP_amplitude"] is None:
            # print("efel failed",len(traces_results[0]["AP_amplitude"]) , len(traces_results[0]["AP_height"]))
            print(f"n spikes are {check_peaks[0]['Spikecount_stimint'][0]}")
            return np.zeros(len(featureNames))
        measurements = []
        for trace_results in traces_results:
            # trace_result is a dictionary, with as keys the requested eFeatures

            for feature_name, feature_values in trace_results.items():

                if len(feature_values) > 0:
                    measurements.append(feature_values[0])
                else:
                    print(f"{feature_name} failed")
                    measurements.append(0)

        return np.array(measurements)

    def get_exprimental_data(self):
        """get_exprimental_data [A getter for model's experimental data (measurments only without discription)]

        Returns:
            [numpy.array]
        """
        return self.EXPRIMENTAL_DATA[:, 1].astype(np.float)

    def get_parameters_boundaries(self):
        # boundaries = np.array([[0, 1]]*6)
        # boundaries = np.array([[0, 1]]*12)
        boundaries = np.concatenate(
            (np.array([[0, 1]]*8), np.array([[0, 1.7]]), np.array([[0, 1]]*6)))
        return boundaries

   


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
        modelRun = Simulator()

        modelRun.model.getModelParameters()
        # modelRun.somaParams()
        # modelRun.setCellParams(np.ones(18))
        rIn = modelRun.inputResistance(-0.5,
                                       plotting=plotting, printing=printing)

        # testAmps = [-0.5, -0.6, -0.7, -0.8, -0.9, -1.0]
        # avgRin = modelRun.avgInRes(
        #     testAmps, plotting=plotting, printing=printing)

        tau = modelRun.timeConstant(-0.5, plotting=plotting, printing=printing)

        delay = 150
        duration = 80
        current = 21
        volt, t = modelRun.stimulateCell(
            current, duration, delay, modelRun.iseg, 0.5, 500)
        # plt = modelRun.model.graphVolt(volt, t, "AP")
        # plt.show()
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
            Level.VLOW, 1, plotting=plotting, printing=printing)

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

    # start_time = time.time()

    # testRun(plotting=True, printing=True, save_to_file=False)
    # print("Measurements are done in--- %s seconds ---" %
    #       (time.time() - start_time))

    model = Simulator()
    # model.setNonPassiveParams([0.49560683118607457, 0.23340705779143517, 0.021298216879921224,
    #    0.11215461948592614, 0.03114830565851094, 0.0923564917708006])
    # model.setNonPassiveParams([0.3865326748233099, 0.15095456804461402, 0.01285859938420347, 0.29840635090426376, 0.017506734583927555, 0.7315609248478437])
    # model.setNonPassiveParams([0.8915485852981853, 0.9891505531636227, 0.03785323436596699, 0.12185825476352832, 0.07039571347860495, 0.0702996422573877])
    # model.setNonPassiveParams([0.9571472348218247, 0.8888712322766363, 0.0396973350549424, 0.9718646220118743, 0.05839309301160812, 0.3126811561554764])
    model.setNonPassiveParams([0.7157734280535681, 0.0783158275088403, 0.037849066079255686,
                               0.20186479394872267, 0.042968980382427205, 0.43630327285909665])
    delay = 150
    duration = 1
    current = 21
    efel.setDoubleSetting('stimulus_current', current)
    efel.setIntSetting("strict_stiminterval", True)
    # efel.setDoubleSetting('delay', delay)

    model.stimulate_efel_Cell(current, duration, delay, model.iseg, 0.5, 500)
    # model.print_EFEL_Measurements(['AP_amplitude', 'AP1_amp', "AP_height", 'AP_width', "spike_half_width", 'AHP_depth_abs', "fast_AHP", 'AHP_depth',
    #  "AHP_time_from_peak", "AHP_slow_time", 'decay_time_constant_after_stim', 'ohmic_input_resistance', 'ohmic_input_resistance_vb_ssse'])
    model.print_EFEL_Measurements(
        ["AP_amplitude", "AP_height", 'AP_width', 'AHP_depth_abs', "AHP_depth", "AHP_time_from_peak"])
    model.EXPRIMENTAL_DATA = np.array(
        [["AP_amplitude", 80.414],
         ["AP_height", 14.527],
         ['AP_width', 0.8],
         ["AHP_depth_abs", -70.28],
         ["AHP_time_from_peak", 16.3],
         ])
    # print(model.get_EFEL_measurements(["AP_amplitude","AP_height",'AP_width','AHP_depth_abs',"AHP_time_from_peak"]))
    print("######################### our measurements###################################")
    # model.get_AP_measurements(printing=True, plotting=False)
    # # print(model.model.cell.soma_dends_resistance_ratio)
    # # model.model.cell.global_conductance = 1/400
    # model.model.soma.g_pas = 69
    # model.dendrites[1].g_pas = model.model.soma.g_pas
    # print(model.dendrites[1].g_pas)
    # # print(model.model.cell.dend1.g_pas)
    # # print(model.model.cell.dend2.g_pas)
    # # print(model.model.cell.dend3.g_pas)
    model.model.graphVolt(model.volt, model.t, "trace").show()

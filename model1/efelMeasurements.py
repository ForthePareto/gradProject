from NrnModel import NrnModel
import efel

class EfelMeasurements():
    def __init__(self,modelHocFile:str = "5CompMy_temp.hoc"):

        self.model = NrnModel(modelHocFile)
        self.soma = self.model.soma
        self.iseg = self.model.iseg
        self.trace = {}       

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
            stim = self.model.setIClamp(delay, duration, clampAmp, segment=stimSeg, position=clampAt)
            volt, t = self.model.recordVolt(self.model.soma, 0.5)
            self.model.runControler(TStop=Tstop, init=-65)
            
            self.trace['T'] = t
            self.trace['V'] = volt
            self.trace['stim_start'] = [delay]
            self.trace['stim_end']  = [delay + duration]

            return volt, t


    def getMeasurements(self,featureNames:list):
        traces = [self.trace]

        traces_results = efel.getFeatureValues(traces,featureNames)

        # The return value is a list of trace_results, every trace_results
        # corresponds to one trace in the 'traces' list above (in same order)
        for trace_results in traces_results:
            # trace_result is a dictionary, with as keys the requested eFeatures
            for feature_name, feature_values in trace_results.items():
                print("Feature %s has the following values: %s" % \
                        (feature_name, ', '.join([str(x) for x in feature_values])))




if __name__ == '__main__':
        delay = 150
        duration = 1
        current = 21
        efel.setDoubleSetting('stimulus_current',current)
        testEFEL = EfelMeasurements()
        testEFEL.stimulateCell(current, duration, delay, testEFEL.iseg, 0.5, 500)
        testEFEL.getMeasurements(['AP_amplitude','AP1_amp','AHP_depth_abs','AHP_depth','AP_width','decay_time_constant_after_stim','ohmic_input_resistance','ohmic_input_resistance_vb_ssse'])
        
    


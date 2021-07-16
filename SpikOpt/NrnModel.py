from collections import OrderedDict
from Model import Model
from neuron import h
from neuron.units import ms, mV
import matplotlib.pyplot as plt
from enum import Enum
import pprint

PRINTING = True


class Level(Enum):
    HIGH = 0.5
    MID = 5.0
    LOW = 10.0
    VLOW = 50.0


class NrnModel(Model):
    def __init__(self, model_file: str, model_name: str = None):
        if model_name is None:
            raise ValueError(
                "You Must give the model name in the Nmodel template")
        self.compartments_dict = None
        self.compartments_list = None
        self.channels = None
        self.model_parameters = None
        self.run(model_file, model_name)

    def run(self, model_file: str, model_name: str = None):
        """loading the model hoc file, updates self.compartments_dict ,self.compartments_list """
        # loading the cell
        if model_name is None:
            raise ValueError("Model name must be passed")
        h.load_file(model_file)    # with no h current
        try:
            self.cell = getattr(h, model_name)()
        except:
            raise ValueError(
                "The given model name doesn't match the one given in model template file")

        # topology = self.cell.wholetree()
        self.compartments_dict = self.get_all_compartments()
        self.compartments_list = list(self.compartments_dict.values())
        # print(list(self.compartment_dict.keys()))
        # print(self.compartments_list[0].wholetree())

    def runControler(self, TStop, init=-65):
        h.load_file('stdrun.hoc')
        h.finitialize(init * mV)
        h.continuerun(TStop * ms)
        # print(list(self.soma_v))

    def get_model_parameters(self, printing=PRINTING):
        """ Returns model parameters dictionary with the following format:
        {
            {key=section_name :value= {key= 'morphology': value= {paramVame: paramValue ,.:.,.:.,.:.} ,
                                      key = 'density_mechs': value = {key=channel_name , value = {paramVame: paramValue ,.:.,.:.,.:.}}}
        }
        """
        topology = h.allsec()
        pp = pprint.PrettyPrinter()
        modelParams = []
        for section in topology:
            modelParams.append(section.psection())
            # print(type(section.psection()))

        params = OrderedDict()
        # params = {}
        for sec in modelParams:
            #for every section in the cell create a key with section name, with value equal to a dictionary
            params[str(sec.get("name"))] = {}

            params[str(sec.get("name"))]['morphology'] = sec.get("morphology")
            unwanted_morphology_info = ["pts3d", "parent", "trueparent"]
            for info in unwanted_morphology_info:
                params[str(sec.get("name"))]['morphology'].pop(info, None)

            params[str(sec.get("name"))]['density_mechs'] = {}
            params[str(sec.get("name"))]['density_mechs'] = sec.get(
                "density_mechs")
        if printing:
            pprint.PrettyPrinter().pprint(params)
            
        self.model_parameters = params
        return  self.model_parameters

    def get_compartments_channels(self, printing=PRINTING):
        """Returns the available channels for each compartement and updates self.channels"""
        channels = OrderedDict()
        for sec in h.allsec():
            channels[str(sec.name())] = []
        for sec in h.allsec():
            for seg in sec:
                for mech in seg:
                    channels[str(sec.name())] += [str(mech.name())]
        if printing:
            pp = pprint.PrettyPrinter()
            pp.pprint(channels)
        self.channels = channels
        return channels

    def get_all_compartments(self) -> OrderedDict:
        sections = OrderedDict()
        for section in h.allsec():
            sections[str(h.secname(sec=section))] = section
        return sections

    def get_compartement(self, compartement: str):
        if len(compartement.split('.')) == 1:
            # in case of input was soma instead of fivecompMy[0].soma
            compartement = self._get_model_name() + "." + compartement
        return self.compartments_dict.get(compartement)

    def _get_model_name(self) -> str:
        return list(self.compartments_dict.keys())[0].split(".")[0]

    def setIClamp(self, delay, duration, amp, segment, position):
        """Add a current clamp at {position} of {segment}"""
        stim = h.IClamp(segment(position))

        stim.delay = delay           # ms
        stim.dur = duration        # ms
        stim.amp = amp             # nA
        return stim

    def recordVolt(self, segmentToRecord, position):

        # set up a recording vector and record voltage at {position} of {segment}
        segment_v = h.Vector().record(segmentToRecord(position)._ref_v)

        segment_t = h.Vector().record(h._ref_t)  # record time.
        return segment_v, segment_t




if __name__ == '__main__':
    from hoc2swc import hoc2swc

    # hoc2swc("5CompMy_temp.hoc", "out.swc")
    model = NrnModel("5CompMy_temp.hoc", "fivecompMy")
    # model.get_model_parameters()
    model.get_compartments_channels(printing=False)
    print(model.get_model_parameters(printing=False)["fivecompMy[0].soma"]["morphology"]['diam'][0])
    # print(model.get_compartement("soma"))
    # pp = pprint.PrettyPrinter()
    # for seg in model.compartments_list[0]:
    #     print(type(seg.NafSmb1_amA))
    # print(model.compartments_list[0][0].pas.g)
    # pp.pprint(h.shape())
    # print(model.cell.soma.g_pas)

from Simulator import Simulator
from collections import OrderedDict
from MultiObectiveDeap import Nsga2Optimizer

AVAILABE_OPTIMIZERS = {"NSGA2": Nsga2Optimizer}

class Fitter:
    def __init__(self, model_type: str, model_file: str, model_name: str, **kwargs):
        self.model_meta_data = None
        self.simulator = None
        self.optimizer = None
        self.requested_measurments = None
        self.stimulation_protocol = None
        self.parameters_info = None
        self.experimental_data = OrderedDict()  # measurement_name: weight, mean, std
        self.target_parameters = OrderedDict()  # param_name : range

        self._initialize_simulator(model_type, model_file, model_name)



    def _save_model_metaData(self, model_type, model_file, model_name):
        keys = ["model_type", "model_file", "model_name"]
        vals = [model_type, model_file, model_name]
        self.model_meta_data = dict(zip(keys, vals))

    def _initialize_simulator(self, model_type, model_file, model_name):
        """Initializes the simulator with the given model configuration."""
        self.simulator = Simulator(model_type, model_file, model_name)

    def fetch_model_parameters(self) -> OrderedDict:
        """Returns an OrderedDictionary with keys= compartments  name , values= dictionary of each channel and their corresponding parameters as strings
            usually parameters are channel conductances.
        """
        if self.simulator is None:
            raise ValueError("Simulator is not initialized")
        return self.simulator.fetch_model_parameters()

    def fetch_model_channels(self) -> OrderedDict:
        """Returns an OrderedDictionary with keys= compartments  name , values= list of inserted channels"""
        if self.simulator is None:
            raise ValueError("Simulator is not initialized")
        return self.simulator.fetch_model_channels()

    def fit(self, optimizer_type: str,measurer_type: str,config: dict, **kwargs): #TODO: ask about parallism
        optimizer = AVAILABE_OPTIMIZERS[optimizer_type]()
        
        self.stimulation_protocol = config.get("stimulation_protocol", None)
        """Format:  {"Protocol Name": "IClamp دروب داون", "Stimulus Type":"Step دروب داون" , "Amplitude":"21" ,"Delay":"150", "Duration":"3", 
        "Stimulus Section":"Iseg دروب داون","Stimulus Position":"0.5" ,"Param":"V دروب", "Recording Section":"Soma دروب د","Recording Position":"0.5", "Vinit":"-65", "T stop":"500"}
        """ 
        if self.stimulation_protocol is None:
            raise ValueError("stimulation protocol is not provided")

      
        self.experimental_data = config.get("experimental_data", None)
        """Format: {   "AP_height":{"weight":-1,"mean":12,"std":12}, "spikeCount":{"weight":-1,"mean":2,"std":1}     }"""
        if self.experimental_data is None:
            raise ValueError("Experimental data is not provided")
        
        optimizer.setup(config)
        

        


if __name__ == '__main__':
    fitter = Fitter("Nmodel", "5CompMy_temp.hoc", "fivecompMy")
    channels = fitter.fetch_model_channels()  # gui first page
    # gui second page, need to be parsed in the upper layer
    params = fitter.fetch_model_parameters()
    config = {}
    fitter.fit(config)
    print(dict(params))

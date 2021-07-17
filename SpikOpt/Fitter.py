from Simulator import Simulator
from collections import OrderedDict

class Fitter:
    def __init__(self, model_type: str,model_file: str ,model_name: str , optimizer_type: str  ):
        self.simulator = None
        self.optimizer = None
        self.requested_measurments = list()
        self.experimental_data = OrderedDict() #measurement_name: weight, mean, std
        self.target_parameters = OrderedDict() #param_name : range

        self.initialize_simulator(model_type,model_file,model_name)

    


    def initialize_simulator(self,model_type,model_file,model_name):
        """Initializes the simulator with the given model configuration."""
        self.simulator = Simulator(model_type,model_file,model_name)

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
    
    
        



if __name__ == '__main__':
    fitter = Fitter("Nmodel","5CompMy_temp.hoc","fivecompMy","Nsga2")
    channels = fitter.fetch_model_channels() # gui first page
    params = fitter.fetch_model_parameters() # gui second page, need to be parsed in the upper layer
    print(dict(params))


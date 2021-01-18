### Auto start
from neuron import h, gui

## loading the cell
h.load_file("5CompMy_temp.hoc")    # with no h current
# h.load_file("5CompMy_temp.hoc")

def singleCellRun():
    
    myCell = h.fivecompMy()

    return myCell
##-----------------{ systems functions }-----------------------
# #Note : this function is essential for the neuron GUI to work smoothly from python.
# definition of the custom advance process through python.
# to include fieldrec function on each time step
h('proc advance() {nrnpython("custom_advance()")}')


def custom_advance():
    h.fadvance()
# -----------------End of Function-----------------------------------------------


cell = singleCellRun() # FIXED 
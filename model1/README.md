## TO-DO 

1. ~~Clean up code~~
2. ~~Remove hard coded params and so on ...~~
3. USE ISSUES AND PROJECT BOARDS INSTEAD OF THIS README 'TO-DO'


## Common commands
- `nrngui` : opens neuron GUI
- `nrnivmodl PATH` : compiles mod files
  


## Design Notes

A design decision that i made, Is to make methods that are supposed to measure a specific feature to be in isolation from others,

with the intention that this might give more flexiblity in the optimization model, to be able to optimize on indvidual features in isolation ,

A downside with this design, Is that some method that overlap some calculations, are duplicated, 
And on top of that,  almost all of the measurement methods share some function that is supppoed to be O(n) [ if i am correct ] , (e.g `patternHighligher` and `sliceSpikeGraph`) , which is bad , i MIGHT have to Rethink it.

NOTE: i did really consider code performance ...    

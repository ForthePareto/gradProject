
# Introduction draft
>___Introduction (1-2 pages): The introduction should cover the need or
motivation, a background on the problem, the overall objective, detailed
SMART objectives, and a Gantt chart for implementation of the project
objectives.___

## Table of contents 

1. need or motivation
2. a background on the problem
3. the overall objective,
4. detailed [SMART objectives](https://www.cdc.gov/dhdsp/docs/smart_objectives.pdf)
5. and a [Gantt  chart](https://www.atlassian.com/agile/project-management/gantt-chart) for implementation of the project objectives.


> [source:](http://neurofitter.sourceforge.net/Publications/VanGeit_FrNeurInf_07_Preprint.pdf)


### 1. Need or motivation

One of the big challenges facing a scientist developing a detailed computational model is how to tune model parameters that cannot be directly derived from experimental results. This is especially true for neuroscientists who develop complex models of neurons that consist of many different compartments (Rall, 1964) incorporating multiple types of voltage-gated ion channels (London and Häusser, 2005) that all require separate parameters. This problem can become even more complicated when one wants to model neuronal networks, which can consist of a large number of neurons of different types (De Schutter et al., 2005). Because of the sharp increase in computational power that is made available to scientists in the field (Markram, 2006) and because of the increasingly detailed knowledge of neuronal mechanisms that underlie neuronal function, these models have become more and more complex, causing an increase in the number of parameters that need to be fitted. In the extreme case there can be different parameters for each compartment or neuron.


Until recently the traditional approach was to tune neuronal model parameters by hand. This requires a lot of effort and knowledge from the scientist and can be very challenging since the underlying mechanisms are highly nonlinear and difficult to grasp. It can also induce some bias as the scientist has a natural tendency to assign in advance different roles to each parameter. However, complicated models have been successfully developed this way (Traub et al., 1991; De Schutter and Bower, 1994). Several parameter search methods have been developed over the years to automate the tuning of neuron models. Three different approaches can be distinguished. First, some methods do a brute force scan of the entire parameter space (Bhalla and Bower, 1993; Foster et al., 1993; Prinz et al., 2003)


### 2. A background on the problem
### 3. the overall objective


> [source](http://www.scholarpedia.org/article/Neuronal_parameter_optimization)

**Neuronal parameter optimization** is the process of identifying sets of parameters that lead to a desired electrical activity pattern in a neuron or neuronal network model that is not fully constrained by experimental data.


__The need for optimization__
Single neurons and neuronal networks intended to reproduce an experimentally observed electrical behavior are modeled with systems of differential equations that contain parameters such as (but not limited to):
-  membrane capacitance, maximal conductances, half activation and inactivation voltages and time constants of individual ionic currents, axial resistance, and morphological parameters such as cell size and axon or dendrite branch structure, length(s) and diameter(s).
In the biological neurons and networks that inspire these models, it is practically never possible to measure all parameters needed to fully constrain the model in a single experimental preparation. Furthermore, the properties of neurons and networks vary even between animals of the same species or within the same animal (Marder and Goaillard 2006), and strategies such as

-   combining a subset of parameters measured in animal A with another subset measured in animal B or
-   obtaining model parameter values by averaging over measurements of the same parameter in different animals

usually fail to produce the desired model behavior (Golowasch et al. 2002).

Starting with a set of differential equations that constitutes a neuron or network model, it is therefore often necessary to find sets of model parameters that approximate the desired behavior through methods other than experimental measurement.


**What is "optimal"?**

Regardless of the optimization method used, model parameter optimization requires a measure for the "goodness" of model neuron or network activity, i.e. for how well the model produces the desired electrical activity pattern. As an alternative to maximizing the goodness of a model, parameter optimization methods can also minimize the difference between the model's activity and the biological target activity as measured by a "distance" or "error" function. Because both strategies are in use, this article does not distinguish between maximizing a goodness measure or minimizing an error measure and uses the two optimization strategies interchangeably.

The choice of goodness or error measure depends on the purpose of the model neuron or network and can have significant influence on the results and success of model parameter optimization. Examples of goodness or error measures are:

-   Root-mean-square difference between the voltage trajectories - spontaneous or in response to stimuli - generated by the model and the biological neuron or network it is supposed to model (Bhalla and Bower 1993).
-   Overlap between model and target voltage trajectories in the dV/dt versus V phase plane (LeMasson and Maex 2001, Achard and De Schutter 2006), a goodness measure that has the advantage of being insensitive to time shifts between voltage traces, but the disadvantage of loosing all timing information.
-   Similarity between features extracted from the model and target voltage traces, such as inter-spike intervals or spike amplitudes (Bhalla and Bower 1993).
-   All-or-none measures of goodness, such as whether a model's behavior is of a certain type, like  bursting or tonically spiking, or falls within the experimentally observed range for characteristics such as burst period and duration (Prinz et al. 2003, 2004). Such digital goodness measures preclude the use of gradient descent  algorithms.
-   Visual similarity between the voltage traces generated by a model and those of the experimental data it is supposed to mimic, as judged by the modeler (Guckenheimer et al. 1993). Such un-quantified and objective goodness measures preclude automated parameter optimization.

Parameter sets with a goodness above a satisfactory threshold are called "solutions" for the optimization problem in question. If there are multiple solutions for an optimization problem - as is often the case - the entirety of those solutions is referred to as the "solution space" of the problem.


**Neuronal parameter optimization methods**

Methods that are being used to identify model parameter sets that generate a desired behavior include:

-   hand-tuning
-   parameter space exploration
-   gradient descent
-   evolutionary algorithms
-   hybrid methods that combine several of the above

Each of these methods will be briefly described below, including a discussion of their mutual advantages and disadvantages. A range of methods for neuronal parameter optimization is also described in (Achard et al. in press).



___1. Hand-tuning___

Perhaps the most widely used method to obtain a model parameter set that produces good model behavior is to manually change one or a few model parameters at a time, guided by trial-and-error and the modeler's experience and prior knowledge of neuronal or network  [dynamics](http://www.scholarpedia.org/article/Dynamical_Systems "Dynamical Systems"), until the model's behavior is satisfactorily close to the experimentally observed target behavior - or until the modeler loses patience.

__Advantages__

-   Does not require the design and programming of an optimization algorithm or goodness function.
-   Not computationally intensive.
-   Incorporates prior knowledge about neuron or network behavior.

__Disadvantages__

-   Difficult even for experienced modelers.
-   Highly subjective.
-   Time-consuming.
-   If a good parameter set is found, it is never certain if there is a better one that has not been discovered.
-   If no good parameter set is found, it is not clear whether it is because none exists, or because existing good parameter sets were not discovered.

__Examples__

-   (Nadim et al. 1995) used hand-tuning to arrive at a functional model of the leech heartbeat elemental  [oscillator](http://www.scholarpedia.org/article/Periodic_Orbit "Periodic Orbit").
-   (Soto-Trevino et al. 2005) hand-tuned a multi-compartment model of a pacemaker network to reproduce a variety of experimentally observed behaviors.




__2. Parameter space exploration__

Parameter space exploration methods use computational brute force to simulate model behavior for a large number of parameter sets and to select those parameter sets that best reproduce the target neuron or network activity. The parameter space of the model can be explored by covering it with a regular grid of parameter sets or with random combinations of parameters. Simulation and analysis results from each simulated parameter set are often stored in a model database that can later be mined for parameter sets that generate activity patterns other than the original target behavior.
___ADD FIGURE___

__Advantages__

-   Provides information about model behavior throughout parameter space.
-   Does not require prior knowledge of model dynamics.
-   Locates entire solution space rather than a single solution.

__Disadvantages__

-   Computationally intensive.
-   Number of simulations necessary to cover parameter space increases exponentially with the number of parameters.
-   Sparse sampling of parameter space may locate good, but miss best parameter sets.

__Examples__

-   (Bhalla and Bower 1993) used parameter exploration of different cell types to localize regions of interest in parameter space.
-   (Foster et al. 1993) used a stochastic search method to study the role of conductances in Hodgkin-Huxley type model neurons.
-   (Goldman et al. 2001) explored the maximal conductance space of a model neuron to identify regions in parameter space that generate silent, tonically spiking, or bursting behavior.
-   (Prinz et al. 2003) used the example of a stomatogastric model neuron to introduce model database construction and analysis as model analysis tools.
-   (Prinz et al. 2004) explored the parameter space of a rhythmic model network and showed that similar and functional network behavior can arise from different network parameter sets.

__3. Gradient descent__

Gradient descent methods (or ascent methods, depending on whether a goodness measure or error function is being used) start at a point in parameter space, locally explore how goodness changes if one or several parameters are changed by small amounts, and then chose a new best parameter set by moving in the direction in parameter space that most improves the goodness of the model. These steps are repeated until an optimal model parameter combination has been found.

__Advantages__

-   Can be computationally efficient.

__Disadvantages__

-   Needs to assume that the goodness function is smooth.
-   Danger of getting stuck in local goodness maxima.

__Examples__

-   (Bhalla and Bower 1993) used gradient descent to identify good parameter sets for multi-compartment models of mitral and granule cells of the olfactory bulb.


__4. Evolutionary algorithms__

[Evolutionary algorithms](http://www.scholarpedia.org/w/index.php?title=Evolutionary_algorithms&action=edit&redlink=1 "Evolutionary algorithms (page does not exist)")  (which include  [genetic algorithms](http://www.scholarpedia.org/article/Genetic_algorithms "Genetic algorithms")) for model parameter optimization use principles such as mutation, mating, and selection - derived from Darwinian evolution - to improve the goodness of a population of model parameter sets. Evolutionary algorithms typically start with a random population of parameter sets, evaluate the goodness of each parameter set, select the best sets as parents of the next generation, and generate that next generation of parameter sets by mixing the parent parameter sets and randomly mutating a subset of parameters. These steps are then repeated with each new generation until parameter sets with sufficient goodness have been identified.

__Advantages__

-   Can handle high-dimensional and non-smooth parameter spaces.
-   Have been shown to be computationally efficient (Moles et al. 2003).

__Disadvantages__

-   Outcome can be highly sensitive to choice of goodness function and algorithmic parameters such as generation size, mutation rate, breeding strategy, etc.

__Examples__

-   (Taylor and Enoka 2004) used an evolutionary algorithm to optimize motor neuron  [synchronization](http://www.scholarpedia.org/article/Synchronization "Synchronization").
-   (Keren et al. 2005) constrained  [compartmental models](http://www.scholarpedia.org/article/Neuronal_Cable_Theory "Neuronal Cable Theory")  using multiple voltage recordings and genetic algorithms.
-   (Achard and De Schutter 2006) found solutions for a complex model neuron with an evolutionary algorithm as the first stage of a hybrid optimization strategy.


__5. Hybrid methods__

Hybrid model parameter optimization methods combine several of the methods described above by applying them to the same model parameter optimization problem either sequentially or in parallel (Achard et al. in press).

__Advantages__

-   Can combine the advantages of the underlying methods.

__Disadvantages__

-   Complex implementation.
-   Require expertise in multiple parameter optimization methods.

__Examples__

-   (Bhalla and Bower 1993) combined gradient descent methods (to localize good parameter sets) with brute-force parameter exploration (to explore how sensitively model behavior depends on the parameters in the vicinity of these solutions).
-   (Achard and De Schutter 2006) used evolutionary algorithms to identify multiple good parameter sets for a complex Purkinjie cell model that would have been too high-dimensional for exhaustive parameter space exploration, but then systematically explored the space between these parameter sets.
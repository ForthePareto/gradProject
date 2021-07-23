# Slide 1 
- Nerve cell's topology

A typical neuron has four morphologically deﬁned regions:
1. the cell body(soma)
2. dendrites
3. axon
4. and presynaptic terminals


# Slide 2
- Action potential
    - memberane potential

    there is an electrical potential diﬀerence across the cell membrane, called
    the membrane potential. 

    the membrane potential arise from the separation of intracellular
    and extracellular space by a cell membrane

    The intracellular , and the extracellular
    mediums contain diﬀering concentrations of various ions
    Some key inorganic ions in nerve cells are
    positively charged cations, including sodium (Na+), potassium (K+),
    
    Typically, there is a greater concentration of extracellular sodium(Na+) than intracellular sodium, and conversely for potassium (K+)

    - Ion channels 
        Ion channels are pores in the lipid bilayer 
        many types of ion channels, referred to as active channels, can exist in open states, where it is possible for ions to pass through the channel, and closed states, in which ions cannot permeate through the channel.

        Whether an active channel is in an open or closed state may depend on the membrane potential,
        passive channels do not change their permeability in response to changes in the membrane potential.

        Both passive channels and active channels in the open state exhibit selective permeability to diﬀerent types of ion.
        For example, potassium channels primarily allow potassium ions to pass through. There are many types of ion channel, each of which has a diﬀerent permeability to each type of ion


    - Action potential

    The threshold is the value of the
    membrane potential which, if reached, leads to the all-or-nothing initiation of an action potential.

    action potentials are characterised by a sharp
    increase in the membrane potential (depolarisation of the membrane) followed by a somewhat less sharp
    decrease towards the resting potential (repolarisation). This may be followed by an afterhyperpolarisation
    phase in which the membrane potential falls below the resting potential before recovering gradually to the
    resting potential.




# Slide 3
- what aﬀects action potenials (model parameters , channels...)?
__See screenShots__

As the concentration of sodium in the extracellular solution is reduced, the action potentials become smaller.

an important property of the voltage-dependent Na+ channels. the permeability increases
rapidly and then, the permeability decays back to its initial level. This phenomenon is called inactivation.

In addition to voltage-dependent changes in Na+ permeability, there are voltage-dependent changes in K+
permeability.

major diﬀerence between the changes in the K+ channels and the changes in the Na+ channels is
that the K+ channels are slower to activate or open.




# Slide 4
-introducing NEURON

The NEURON software, developed at Duke University, is a simulation environment for modeling individual
neurons and networks of neurons.


NEURON is primarily used to simulate the full experiments on the models, starting from stimulating the model and  recording the model’s behavior,

By writing instructions in NEURON’s programming language ,'hoc', we can specify a model that descripes
the desired model topology and diﬀerent channels and their respective paramerters


# Slide 5

- Action pot. feature extraction



__time constant (tuo)__

    the time for the potential to change from its initial value to its final value ,the change occurs as an exponential function of time.


__internal resistance (resistance of the axoplasm) (Ri)__

- The ohmic input resistance Ri of the cell




__average internal resistance__ 

- The average ohmic input resistance Ri of the cell 

        Measures the average input resistance over many samples


__Action potential (AP) Height__

- The relative height of the action potential 

      Difference betweent AP-Start and AP-Peak potentials






__Action potential (AP) Width__

- Width of spike

        Time from AP half-amplitude value in Depolarization, till the same value is reached in Repolarization phase




__after-hyperpolarization (AHP) depth__ 

-   Relative depth of ahp phase

        Difference between Resting membrane potential and min potential in hyperpolarization phase


__after-hyperpolarization (AHP) Duration__

- hyperpolarization-phase time ...
    
        Time from AHP-Start(resting-membrane pot.) till AHP-End (resting-membrane pot. agian)



__after-hyperpolarization (AHP) Half-Duration__

    time between AHP-half values



__after-hyperpolarization (AHP) Half-Decay__

    time from AHP-trough to AHP-half valve



__after-hyperpolarization (AHP)Rising-Time__

    time from AHP-Start till AHP-trough


__Rheobase__

    the min Current for a long duration (+50 ms), that causes a spike and is estimulated from the soma. 




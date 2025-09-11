# Part 2 - Working with the NOMAD-Simulations schema plugin

In NOMAD, all the simulation metadata is defined under the `Simulation` section. You can find its Python schema defined in the [`nomad-simulations`](https://github.com/nomad-coe/nomad-simulations/) repository. The [entry point](parser_plugins.md) for the schema is defined in [src/nomad_simulations/schema_packages/\_\_init\_\_.py](https://github.com/nomad-coe/nomad-simulations/blob/develop/src/nomad_simulations/schema_packages/__init__.py) module. This section will appear under the `data` section for each NOMAD [*entry*](https://nomad-lab.eu/prod/v1/staging/docs/reference/glossary.html#entry). There is also a [specialized documentation page](https://nomad-coe.github.io/nomad-simulations/) in the `nomad-simulations` repository.

The `Simulation` section inherits from a more abstract section or concept called `BaseSimulation`, which at the same time inherits from another section, `Activity`.

??? note "Inheritance and composition"
    During this part, we will identify the **is a** concept with inheritance of one section into another (e.g., a `Simulation` _is an_ `Activity`) and the **has a** concept with composition of one section under another (e.g., a `Simulation` **has a** `ModelSystem` sub-section). Strictly speaking, this equivalency is not entirely true, as we are loosing it in some cases. But for the purpose of learning the complicated rules of inheritance and composition, we will conceptually maintain this equivalency during this Tutorial.

A set of [base sections](https://nomad-lab.eu/prod/v1/staging/docs/howto/customization/base_sections.html) derived from the [Basic Formal Ontology (BFO)](https://basic-formal-ontology.org/) is used as the basis for our section definitions. The previous inheritance allows us to define `Simulation` at the same level of other activities in Materials Science, e.g., `Experiment`, `Measurement`, `Analysis`. We do this in order to achieve a common vocabulary and data standardization with the experimental community. The relationship tree from the most abstract sections upon reaching `Simulation` is thus:

<div class="click-zoom">
    <label>
        <input type="checkbox">
        <img src="../assets/part2-nomad-simulations/simulation_base_details.png" alt="Simulation base section diagram." width="80%" title="Click to zoom in">
    </label>
</div>

Note that the white-headed arrow here indicates _inheritance_ / _is a_ relationship. `BaseSimulation` contains the general information about the `Program` used (see [Program](#program)), as well as general time information about the simulation, e.g., the datetime at which it started (`datetime` is defined within `Activity` and is inherited by `BaseSimulation`) and ended (`datetime_end`). `Simulation` contains further information about the specific input and output sections ([see below](#sub-sections-in-simulation)).

??? question "Notation for the section attributes in the UML diagram"
    Throughout this documentation page we will use UML diagrams to describe our section / class definitions, as well as to include the information abpit their attributes / quantities including their main definitions. The notation is:

        <name-of-quantity>: <type-of-quantity>, <(optional) units-of-quantity>

    Thus, `cpu1_start: np.float64, s` means that there is a quantity named `'cpu1_start'` of type `numpy.float64` and whose units are `'s'` (seconds).
    We also include the existence of sub-sections by bolding the name. For example, there is a sub-section under `Simulation` named `'model_method'` whose section defintion can be found in the `ModelMethod` section. We will represent this sub-section containment in more complex UML diagrams in the future using the containment arrow (see below for the specific ase of [`Program`](#program)).

We use double inheritance from `EntryData` in order to populate the `data` section in the NOMAD archive. All of the base sections discussed here are subject to the [public normalize function](#normalize-function) in NOMAD. The private function `set_system_branch_depth()` is related with the [ModelSystem section](#modelsystem).

Let's use this knowledge to see how to work with the schema in practice. If you have not already installed `nomad-simulations`, do so now following the instructions in the [Overview](index.md#tutorial-information-and-preparation).

!!! abstract "Assignment 2.1"
    Create an instance of the `Simulation` section. Imagine you know that the CPU1 took 24 minutes and 30 seconds on finishing the simulation; can you populate the `Simulation` section with these times? What is the elapsed time in seconds? And in hours?

??? success "Solution 2.1"
    We can open a Python console:
    ```sh
    python
    ```

    And import and instantiate the `Simulation` section:
    ```python
    from nomad_simulations.schema_packages.general import Simulation
    simulation = Simulation()
    ```

    Now, we can assign the elapsed time of the CPU1 by defining the start and the end quantities, i.e., `cpu1_start` and `cpu1_end`. To assign the units, we also need to import the [Pint](https://pint.readthedocs.io/en/stable/) utility class `ureg`:
    ```python
    from nomad.units import ureg
    simulation.cpu1_start = 0 * ureg.second
    simulation.cpu1_end = 30 * ureg.second + 24 * ureg.minute
    ```

    In seconds, the elapsed time can be printed by doing:
    ```python
    simulation.cpu1_end - simulation.cpu1_start
    ```
    which is 1470 seconds. In hours, we can use the method `to('hour')`:
    ```python
    (simulation.cpu1_end - simulation.cpu1_start).to('hour')
    ```
    which give us approximately 0.4083 hours.




## Main sub-sections in `Simulation` {#sub-sections-in-simulation}

The `Simulation` section is composed of 4 main sub-sections:

1. [`Program`](#program): contains all the program metadata, e.g., `name` of the program, `version`, etc.
2. [`ModelSystem`](#modelsystem): contains all the system metadata about geometrical positions of atoms, their states, simulation cells, symmetry information, etc.
3. [`ModelMethod`](#modelmethod): contains all the methodological metadata, and is divided in two main aspects: the mathematical model or approximation used in the simulation (e.g., `DFT`, `GW`, `ForceFields`, etc.) and the numerical settings used to compute the properties (e.g., meshes, self-consistent parameters, basis sets settings, etc.).
4. [`Outputs`](#outputs): contains all the output properties obtained during the simulation.

!!! note "Self-consistent steps, SinglePoint entries, and more complex workflows."
    The minimal unit for storing data in the NOMAD archive is an [*entry*](https://nomad-lab.eu/prod/v1/staging/docs/reference/glossary.html#entry). In the context of simulation data, an entry may contain data from a calculation on an individual system configuration (e.g., a single-point DFT calculation) using **only** the above-mentioned sections of the `Simulation` section. Information from self-consistent iterations to converge properties for this configuration are also contained within these sections.

    More complex calculations that involve multiple configurations require the definition of a *workflow* section within the archive. Depending on the situation, the information from individual workflow steps may be stored within a single or multiple entries. For example, for efficiency, the data from workflows involving a large amount of configurations, e.g., molecular dynamics trajectories, are stored within a single entry. Other standard workflows store the single-point data in separate entries, e.g.,  a `GW` calculation is composed of a `DFT SinglePoint` entry and a `GW SinglePoint` entry. Higher-level workflows, which simply connect a series of standard or custom workflows, are typically stored as a separate entry. See [Part V - Custom Workflows](custom_workflows.md) for more information.
<!--Mention here Part V?-->

The following schematic represents a simplified representation of the `Simulation` section (note that the arrows here are a simple way of visually defining _inputs_ and _outputs_):

<div class="click-zoom">
    <label>
        <input type="checkbox">
        <img src="../assets/part2-nomad-simulations/simulation_composition.png" alt="Simulation composition diagram." width="80%" title="Click to zoom in">
    </label>
</div>

## `Program` {#program}

The `Program` section contains all the information about the program / software / code used to perform the simulation. The detailed relationship tree is:

<div class="click-zoom">
    <label>
        <input type="checkbox">
        <img src="../assets/part2-nomad-simulations/program.png" alt="Program quantities and functions UML diagram." width="80%" title="Click to zoom in">
    </label>
</div>

Note that the rhombo-headed arrow here indicates a _composition_ / _has a_ relationship, so that `BaseSimulation` has a `Program` sub-section under it.

!!! abstract "Assignment 2.2"
    Instantiate a `Program` section and directly assign the name `'VASP'` and the version `'5.0.0'` quantities. Add this sub-section to the `Simulation` section created in the Assignment 2.1. Can you re-assign the `Program.version` quantity to be an integer number, 5?

??? success "Solution 2.2"
    We can import and assign directly quantities of sections by doing:
    ```python
    from nomad_simulations.schema_packages.general import Program
    program = Program(name='VASP', version='5.0.0')
    ```

    And we can add it as a sub-section of `Simulation` by assigning the attribute of that class:
    ```python
    simulation.program = program
    ```

    If we try to re-assign:
    ```python
    program.version = 5
    ```
    the code will complain with a `TypeError`:
    ```sh
    TypeError: The value 5 with type <class 'int'> for quantity nomad_simulations.schema_packages.general.Program.version:Quantity is not of type <class 'str'>
    ```
    This is because in the defintion of the `class Program` and the `Quantity:version`, we defined the type to be a string. So answering the question: no, it is not possible to re-assign `version` to be an integer due to the fact that is defined to be a string.



## `ModelMethod` {#modelmethod}

The `ModelMethod` section is an input section which contains all the information about the mathematical model used to perform the simulation. In NOMAD, we can extend the support of certain methods by inheriting from `ModelMethod` and extend the schema for the new methodology. `ModelMethod` also contains a specialized sub-section called [`NumericalSettings`](#numericalsettings). The detailed relationship tree is:

<div class="click-zoom">
    <label>
        <input type="checkbox">
        <img src="../assets/part2-nomad-simulations/model_method.png" alt="ModelMethod quantities and functions UML diagram." width="80%" title="Click to zoom in">
    </label>
</div>

`ModelMethod` is thus a sub-section under `Simulation`. It inherits from an abstract section `BaseModelMethod`, as well as containing a sub-section called `contributions` of the same section. The underlying idea of `ModelMethod` is to parse the input parameters of the mathematical model, typically a Hamiltonian. This total Hamiltonian or model could be split into individual sub-terms or `contributions`. Each of the electronic-structure methodologies inherit from `ModelMethodElectronic`, which contains a boolean `is_spin_polarized` indicating if the `Simulation` is spin polarized or not. The different levels of abstractions are useful when dealing with commonalities amongst the methods.

!!! abstract "Assignment 2.3"
    Instantiate a `DFT` section. For simplicity, you can also assign the `jacobs_ladder` quantity to be `'LDA'`. Add this sub-section to the `Simulation` section created in the Assignment 2.1. What is the underlying concept that allows you to add directly the `class DFT` under `Simulation.model_method`, provided that the definition of this attribute is a `ModelMethod` sub-section? Can you reason why the current schema (version 0.0.2) is inconsistent in handling the `xc_functionals` contributions?

??? success "Solution 2.3"
    Similarly to Assignment 2.2, we can import and create the `DFT` section:
    ```python
    from nomad_simulations.schema_packages.model_method import DFT
    dft = DFT(jacobs_ladder='LDA')
    ```

    This time, due to the fact that `Simulation.model_method` is a repeating sub-section (i.e., a list of sub-sections), we need to append `dft` instead of directly assigning the attribute:
    ```python
    simulation.model_method.append(dft)
    ```

    Thanks to inheritance of `class DFT` with `ModelMethod` and polymorphism, we can directly append `dft` as a `model_method` sub-section.

    The current schema is also a bit inconsistent due to the fact that `BaseModelMethod` has a sub-section called `contributions`, while `DFT` has also a sub-section called `xc_functionals`, hence both sub-sections live at the same time under the section `DFT`. Conceptually, both sub-sections are the same: they refer to a sub-term or contribution of the total DFT Hamiltonian, thus, their definitions should be combined, and only one sub-section should be used. The best action here would be to open an issue in the `nomad-simulations` Github repository, or directly contact the maintainers.



### `NumericalSettings` {#numericalsettings}

The `NumericalSettings` section is an abstract section used to define the numerical parameters set during the simulation, e.g., the plane-wave basis cutoff used, the k-mesh, etc. These parameters can be defined into specialized classes which inherit from `NumericalSettings` (similar to what happens with all the electronic-structure methodologies and `ModelMethod`). The detailed relationship tree is:

<div class="click-zoom">
    <label>
        <input type="checkbox">
        <img src="../assets/part2-nomad-simulations/model_method_with_numerical_settings.png" alt="NumericalSettings quantities and functions UML diagram." width="80%" title="Click to zoom in">
    </label>
</div>

!!! abstract "Assignment 2.4"
    Instantiate a `SelfConsistency` section and assign the quantity `threshold_change` to be `1e-3` and the `threshold_change_unit` to be `'joule'`. Add this sub-section to the `DFT` section created in the Assignment 2.3. Is the new information also stored in the `Simulation` section created in Assignment 2.1? Can you access the information of the Jacobs ladder string used in this simulation **starting** from the newly instantiated class?

??? success "Solution 2.4"
    We can import and create the class `SelfConsistency`, assign the specified quantities, and append it under `dft`:
    ```python
    from nomad_simulations.schema_packages.numerical_settings import SelfConsistency
    scf = SelfConsistency(threshold_change=1e-3, threshold_change_unit='joule')
    dft.numerical_settings.append(scf)
    ```

    In order to see if `scf` is showing directly under `simulation`, we can:
    ```python
    simulation.model_method[0].numerical_settings
    ```
    which indeed returns:
    ```sh
    [SelfConsistency:SelfConsistency(name, threshold_change, threshold_change_unit)]
    ```

    In order to go from `scf` to the `dft.jacobs_ladder` information, we need to go one level up with respect to `scf`. In order to do this, we can use the method `m_parent`:
    ```python
    scf.m_parent.jacobs_ladder
    ```
    which will return:
    ```sh
    'LDA'
    ```

## `ModelSystem` {#modelsystem}

The `ModelSystem` section is an input section which contains all the information about the geometrical space quantities (positions, lattice vectors, volumes, etc) of the simulated system. This section contains various quantities and sub-sections which aim to describe the system in the most complete way and in a variety of cases, from unit cells of crystals and molecules up to microstructures. In order to handle this _hierarchical_ structure, `ModelSystem` is nested over itself, i.e., a `ModelSystem` can be composed of sub-systems, which at the same time could be composed of smaller sub-systems, and so on. This is done thanks to the (proxy) sub-section attribute called `model_system`.

The `Cell` sub-section is an important section which contains information of the simulated cell, including the `lattice_vectors` and the `positions` of the particles within. However, it does not contain specific information about these particles, e.g., their chemical identity or electronic state, as this is the responsability of a more specialized section, the `AtomicCell`. This section stores the relevant information about each of the atoms constituting the material via the [`AtomsState`](#atomsstate) sub-section. The `Symmetry` sub-section contains standard symmetry classifications of the system, while the `ChemicalFormula` sub-section stores various strings that allow the system to be identified in a specific format of the chemical formulas (IUPAC, Hill, etc).

The detailed relationship tree is:

<div class="click-zoom">
    <label>
        <input type="checkbox">
        <img src="../assets/part2-nomad-simulations/model_system.png" alt="ModelSystem quantities and functions UML diagram." width="80%" title="Click to zoom in">
    </label>
</div>

The `Entity` abstract section is defined in the [Basic Formal Ontology (BFO)](https://basic-formal-ontology.org/) similar to `Activity`, and we use it to abstract our `ModelSystem`. In fact, `ModelSystem` is inheriting from an intermediate abstract section called `System`. This base section, `System`, is also used by the experimental data models to define the composition and structure of the measured materials.

??? note "GeometricSpace and simulated cells."
    The abstract section `GeometricSpace` is used to define more general real space quantities related with the system of reference used, areas, lengths, volumes, etc. However, this section and `Cell` are currently (version 0.0.2) under revision and will probably change in the near future.


### `AtomsState` and other sub-sections {#atomsstate}

The `AtomsState` section is a list of sub-sections within `AtomicCell`, corresponding to the list of particles specified by the `positions` array defined under `Cell`. Each `AtomsState` section contains information about a specific chemical element used in the simulation, and may also contain additional `OrbitalsState`, `CoreHole`, or `HubbardInteractions` information. The detailed relationship tree is:

<div class="click-zoom">
    <label>
        <input type="checkbox">
        <img src="../assets/part2-nomad-simulations/model_system_with_atoms_state.png" alt="AtomsState quantities and functions UML diagram." width="80%" title="Click to zoom in">
    </label>
</div>



!!! abstract "Assignment 2.5"
    Instantiate two `AtomsState` sections and assign the `chemical_symbol` to be `'Ga'` and `'As'` for each of these sections. For this assignment, we also need to define a `logger` object in order for the functionalities to work:
    ```python
    from nomad import utils
    logger = utils.get_logger(__name__)
    ```
    Using a method of `AtomsState`, what is the atomic number of Ga and of As?

??? success "Solution 2.5"
    We can import and create two instances of `AtomsState` and assign `chemical_symbol` in a variety of ways. In this case, we used list comprehension:
    ```python
    from nomad_simulations.schema_packages.atoms_state import AtomsState
    atoms_states = [AtomsState(chemical_symbol=element) for element in ['Ga', 'As']]
    ```

    For each of the atoms, we can use the class method `resolve_atomic_number(logger)` which will directly return the atomic number of each section:
    ```python
    [atom.resolve_atomic_number(logger=logger) for atom in atoms_states]
    ```
    which returns:
    ```sh
    [31, 33]
    ```
    Hence, the atomic number of Ga is 31 and of As is 33.


!!! abstract "Assignment 2.6"
    Instantiate a `ModelSystem` section and a `AtomicCell` section. Assign the `positions` in the `AtomicCell` section to be `[[0, 0, 0], [1, 1, 1]]` in meters. Add the `atoms_states` defined in the Assignment 2.5 under the `AtomicCell` section. Append this `AtomicCell` section under `ModelSystem`, and append `ModelSystem` to the `Simulation` section created in Assignment 2.1.

    Now, we want to extract the different formats in which the chemical formulas of this system can be written. For that, instantiate directly the `ChemicalFormula` sub-section under `ModelSystem`. Note: you can use the `ChemicalFormula.normalize(archive, logger)` method, and pass `archive=None` to this function.

    What are the different formats of the chemical formula? What is the string of the `descriptive` format and why it coincides with other format(s) in the sub-section?

??? success "Solution 2.6"
    We can import and create instances of `ModelSystem` and `AtomicCell` and assign the corresponding quantities directly:
    ```python
    from nomad_simulations.schema_packages.model_system import ModelSystem, AtomicCell
    model_system = ModelSystem()
    atomic_cell = AtomicCell(atoms_state=atoms_states, positions=[[0, 0, 0], [1, 1, 1]] * ureg.meter)
    model_system.cell.append(atomic_cell)
    ```

    We can append this section to `Simulation`:
    ```python
    simulation.model_system.append(model_system)
    ```

    We can now assign directly an empty `ChemicalFormula` section to `ModelSystem`, in order to be able to call for the specific class method:
    ```python
    from nomad_simulations.schema_packages.model_system import ChemicalFormula
    model_system.chemical_formula = ChemicalFormula()
    ```

    In order to extract the formulas and assign them to the quantities of the section `ChemicalFormula`, we can use the method `normalize()`. This class method takes two arguments as inputs: `archive` and `logger`. For the purpose of this tutorial, we can set `archive=None`:
    ```python
    model_system.chemical_formula.normalize(archive=None, logger=logger)
    ```

    Now, the `ChemicalFormula` sub-section contains the information of the different formats for the chemical formula: `reduced` and `hill` are both `'AsGa'`, while `iupac` is `'GaAs'`. The `descriptive` formula is set depending on the chemical elements present in the system, and because neither `'H'` nor `'O'` is present (i.e., no organic formulas), and gallium arsenide does not belong to any format exceptions, then it is set to the inorganic typical formula `'GaAs'`, coinciding with `iupac`. The `anonymous` formula is `'AB'`.



## `Outputs` {#outputs}

The `Outputs` section contains all the information about the properties computed by the simulations, as well as references to the relevant `ModelMethod` and `ModelSystem`. Each property is stored individually under `Outputs`, and inherits from an abstract section call `PhysicalProperty`. The `PhysicalProperty` base section contains the `value` of the property along with other relevant quantities. The `variables` sub-section enables the physical property to be stored as a function of a varying parameter. Accordingly, the shape of value is calculated in a dynamic way. This means that the same physical property (e.g., `ElectronicBandGap`) could have different shapes depending on the use-case being parsed (e.g., a single scalar number or a set of varying scalars with respect to a variable, e.g., `Temperature`).

The `Outputs` section can be further specialized into `SCFOutputs` in case the properties are calculated in a series of self-consistent steps. The steps are stored under a sub-section called `scf_steps`, while the last step and other non-self-consistently calculated properties are stored directly under `SCFOutputs`. The reference to the `SelfConsistency` section (see [NumericalSettings](#numericalsettings)) allows us to automatically determine if a self-consistently calculated property is converged or not.

The detailed relationship tree is:

<div class="click-zoom">
    <label>
        <input type="checkbox">
        <img src="../assets/part2-nomad-simulations/outputs.png" alt="Outputs quantities and functions UML diagram." width="80%" title="Click to zoom in">
    </label>
</div>


!!! abstract "Assignment 2.7"
    Instantiate an `SCFOutputs` section. We are going to store a self-consistently calculated `FermiLevel`, whose values at each step are `[1, 1.5, 2, 2.1, 2.101]` in eV. Add the appropiate references to the `ModelMethod` and `ModelSystem` sections created in Assignment 2.3 and Assignment 2.6, respectively. For the self-consistently calculated `FermiLevel` section, add the reference to the section `SelfConsistency` created in Assignment 2.4.

    Check if the `FermiLevel` is self-consistently converged or not by using a class method from `SCFOutputs`. What happens if the `SelfConsistency.threshold_change` is now `1e-24`?

??? success "Solution 2.7"
    We can import and create an instance of `SCFOutputs` and append it to simulation:
    ```python
    from nomad_simulations.schema_packages.outputs import SCFOutputs
    scf_outputs = SCFOutputs()
    simulation.outputs.append(scf_outputs)
    ```

    We can add the references to the other `ModelMethod` and `ModelSystem` sections by doing:
    ```python
    scf_outputs.model_method_ref = simulation.model_method[0]
    scf_outputs.model_system_ref = simulation.model_system[0]
    ```

    Now, we need to create the `scf_steps` sub-sections with the information of the `FermiLevel` steps and their values. For that,
    ```python
    from nomad_simulations.schema_packages.outputs import Outputs
    from nomad_simulations.schema_packages.properties import FermiLevel
    for value in [1, 1.5, 2, 2.1, 2.101]:
        fermi_level = FermiLevel()
        fermi_level.value = value * ureg.eV
        scf_outputs.scf_steps.append(Outputs(fermi_levels=[fermi_level]))
    ```
    Note that:

    1. The properties like `fermi_levels` are repeated sub-sections under `Outputs`, so we need to assign a list.
    2. The `scf_steps` sub-sections are `Outputs`, hence we need to import the `Outputs` section and append it to that attribute.

    We also need to add the last step directly under `scf_outputs` and add the reference to the `SelfConsistency` section:
    ```python
    scf_outputs.fermi_levels.append(FermiLevel(value=2.101 * ureg.eV, self_consistency_ref=simulation.model_method[0].numerical_settings[0]))
    ```

    In order to check if the `FermiLevel` is converged or not, we can use the class method `resolve_is_scf_converged()`. This method has various inputs that are explained in the method itself. Here we will simply use the function like:
    ```python
    scf_outputs.resolve_is_scf_converged(property_name='fermi_levels', i_property=0, physical_property=scf_outputs.fermi_levels[0], logger=logger)
    ```
    which indeed returns
    ```sh
    True
    ```
    So the `FermiLevel` is converged.

    Now, if we set:
    ```python
    scf.threshold_change = 1e-24
    ```
    And re-run the `resolve_is_scf_converged()` method, we can see that the `FermiLevel` is not self-consistenly converged:
    ```sh
    False
    ```

    The reason for this is that, in joules, the last two self-consistent steps (where the Fermi level is 2.1 and 2.101 eV) have a difference which can be also computed with another class method:
    ```python
    scf_values = scf_outputs.get_last_scf_steps_value(scf_last_steps=scf_outputs.scf_steps[-2:], property_name='fermi_levels', i_property=0, scf_parameters=scf, logger=logger)
    abs(scf_values[0] - scf_values[1])
    ```
    which returns:
    ```sh
    1.6021766340002688e-22
    ```
    Then, a `threshold_change` of `1e-24` is smaller than the difference, so that the `FermiLevel` is not converged.




!!! abstract "Assignment 2.8"
    We are going to store two `ElectronicBandGap` property sections under the `SCFOutputs` section created in the Assignment 2.7:

    * An `ElectronicBandGap` whose value is 2 eV.
    * An `ElectronicBandGap` varying with `Temperature`, whose values are `[1, 1.5, 2]` in eV for `[100, 150, 200]` temperatures in Kelvin.

    In the second situation of an electronic band gap which varies with the `Temperature`, what happens if you directly assign `value` **before** defining the `Temperature` variables sub-section in `ElectronicBandGap`?


??? success "Solution 2.8"
    We can import the `ElectronicBandGap` property and assign the first case of an electronic band gap which is 2 eV:
    ```python
    from nomad_simulations.schema_packages.properties import ElectronicBandGap
    band_gap = ElectronicBandGap()
    band_gap.value = 2 * ureg.eV
    scf_outputs.electronic_band_gaps.append(band_gap)
    ```

    We can do the same for the temperature-dependent band gap by importing and defining the `Temperature` variable sub-section (note that `variables` is a repeated sub-section, thus we need to assign a list):
    ```python
    from nomad_simulations.schema_packages.variables import Temperature
    band_gap_T = ElectronicBandGap(variables=[Temperature(points=[100, 150, 200] * ureg.kelvin)])
    band_gap_T.value = [1, 1.5, 2] * ureg.eV
    scf_outputs.electronic_band_gaps.append(band_gap_T)
    ```

    Here, we have assigned first `variables` before the `value` of the property. However, if we want to assign first the `value`:
    ```python
    band_gap_T = ElectronicBandGap()
    band_gap_T.value = [1, 1.5, 2] * ureg.eV
    ```
    we will get a `ValueError` due to the fact that `variables` is not set and the shape of `value` is not empty:
    ```sh
    ValueError: The shape of the stored `value` [3] does not match the full shape [] extracted from the variables `n_points` and the `shape` defined in `PhysicalProperty`.
    ```

    Thus, the `variables` sub-sections **must** be set before setting the `value` of a physical property. This is because the `class PhysicalProperty` is doing validations on the shape of the `variables` and `value`, and it only works if `variables` is set first. Only when the shape of `value` is empty and due to the fact that `variables` is set by default to an empty list, then we would not get any error.


## Extra: The `normalize()` class function {#normalize-function}

Each base section defined using the NOMAD schema has a set of public functions which can be used at any moment when reading and parsing files in NOMAD. The `normalize(archive, logger)` function is a special case of such functions, which warrants an in-depth description.

This function is run within the NOMAD infrastructure by the [`MetainfoNormalizer`](https://github.com/nomad-coe/nomad/blob/develop/nomad/normalizing/metainfo.py) in the following order:

1. A child section's `normalize()` function is run before its parents' `normalize()` function.
2. For sibling sections, the `normalize()` function is executed from the smaller to the larger `normalizer_level` attribute. If `normalizer_level` is not set or if they are the same for two different sections, the order is established by the attributes definition order in the parent section.
3. Using `super().normalize(archive, logger)` runs the inherited section normalize function.

Let's see some examples. Imagine having the following `Section` and `SubSection` structure:

```python
from nomad.datamodel.data import ArchiveSection


class Section1(ArchiveSection):
    normalizer_level = 1

    def normalize(self, achive, logger):
        # some operations here
        pass


class Section2(ArchiveSection):
    normalizer_level = 0

    def normalize(self, achive, logger):
        super().normalize(archive, logger)
        # Some operations here or before `super().normalize(archive, logger)`


class ParentSection(ArchiveSection):

    sub_section_1 = SubSection(Section1.m_def, repeats=False)

    sub_section_2 = SubSection(Section2.m_def, repeats=True)

    def normalize(self, achive, logger):
        super().normalize(archive, logger)
        # Some operations here or before `super().normalize(archive, logger)`
```

Now, `MetainfoNormalizer` will be run on the `ParentSection`. Applying **rule 1**, the `normalize()` functions of the `ParentSection`'s childs are executed first. The order of these functions is established by **rule 2** with the `normalizer_level` atrribute, i.e., all the `Section2` (note that `sub_section_2` is a list of sections) `normalize()` functions are run first, then `Section1.normalize()`. Then, the order of execution will be:

1. `Section2.normalize()`
2. `Section1.normalize()`
3. `ParentSection.normalize()`

In case we do not assign a value to `Section1.normalizer_level` and `Section2.normalizer_level`, `Section1.normalize()` will run first before `Section2.normalize()`, due to the order of `SubSection` attributes in `ParentSection`. Thus the order will be in this case:

1. `Section1.normalize()`
2. `Section2.normalize()`
3. `ParentSection.normalize()`

By checking on the `normalize()` functions and **rule 3**, we can establish whether `ArchiveSection.normalize()` will be run or not. In `Section1.normalize()`, it will not, while in the other sections, `Section2` and `ParentSection`, it will.

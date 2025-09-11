# Matlab Atom Probe Toolbox ranging definitions

Matlab figures are not necessarily directly parsable using Python tools. This is relevant for interoperability when using e.g. the
[Matlab Atom Probe Toolbox](https://github.com/peterfelfer/Atom-Probe-Toolbox) from Prof. Felfer's group at the FAU Erlangen.
This toolbox stores results as content-rich Matlab figures and HDF5 files.

The ifes_apt_tc_data_modeling library >=0.2.1 offers a Matlab script matlab/matlab_fig_to_txt.m that users should run first
to convert these figures into an intermediate text-based file with the extension fig.txt.

This text file has a simple structure: Each ranging definition is a single line with three parts separated by spaces:
The first part is a human-readable description of the ion (element, isotope, molecular ion). We follow the naming convention of P. Felfer's atom-probe-toolbox. The second part is the left (minimum) bound while the third part is the right (maximum bound) bound of the mass-to-charge-state-ratio value interval of the ion that is specified in the first part. [Details are available here](https://github.com/atomprobe-tc/ifes_apt_tc_data_modeling/blob/main/tests/data/fig/)

Once converted to fig.txt, pynxtools-apm uses the ifes_apt_tc_data_modeling library's fig parser to process the ranging definitions.

| fig.txt | NeXus/HDF5 |
| --------------- | --------------  |
| (Molecular ion) number of elements and their multiplicity | :heavy_check_mark: |
| Mass-to-charge-state-ratio value interval for each molecular ion | :heavy_check_mark: |
| Charge state | :heavy_check_mark: |

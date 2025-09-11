# ENV

The pynxtools-apm parser and normalizer reads the following content and maps them on respective NeXus concepts that are defined in the NXapm application definition:

| ENV | NeXus/HDF5 |
| --------------- | --------------  |
| (Molecular ion) number of elements and their multiplicity | :heavy_check_mark: |
| Mass-to-charge-state-ratio value interval for each molecular ion | :heavy_check_mark: |

The ENV file format has been developed by the GPM atom probe group in Rouen, France.
The format stores instrument parameters and ranging definitions.
The ifes_apt_tc_data_modeling library >=0.2.1 currently ignores the instrument parameters
but technically these could be parsed. <span style="color:red">The implementation is based on a very limited number
of example files so the robustness of this parser should not be expected to be of as high
quality than that of the other parsers.</span>

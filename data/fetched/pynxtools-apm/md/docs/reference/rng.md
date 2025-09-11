# RNG

The pynxtools-apm parser and normalizer reads the following content and maps them on respective NeXus concepts that are defined in the NXapm application definition:

| RNG | NeXus/HDF5 |
| --------------- | --------------  |
| (Molecular ion) number of elements and their multiplicity | :heavy_check_mark: |
| Mass-to-charge-state-ratio value interval for each molecular ion | :heavy_check_mark: |

The RNG file format is a text file format for storing ranging definitions that contains additional pieces of information like relevant volume of an ion assumed for reconstruction purposes or color.
The ifes_apt_tc_data_modeling library==0.2.1 currently ignores these pieces of information.
Occasionally, users define ions with custom name but unphysical details to it in an effort to
enable a filtering of ions within specific mass-to-charge-state-ratio values. The ifes_apt_tc_data_modeling library >= 0.2.1 reads these iontypes but discards their custom name.
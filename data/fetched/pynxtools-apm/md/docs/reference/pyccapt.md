# OXCART instrument and pyccapt

[pyccapt](https://github.com/mmonajem/pyccapt) is an open-source control system for a custom-built atom probe as well as other instruments pioneered by Prof. Felfer and M. Monajem at the FAU Erlangen. The software is used to control their custom-built atom probe instrument
OXCART. Pyccapt generates several HDF5 files which store key results and parameterization of an atom probe measurement.

Pynxtools-apm can read all pieces of information that is stored in these files. Currently, the following pieces of information are
configured to be mapped by default on respective NeXus concepts to serve as an example.

| pyccapt reconstruction | NeXus/HDF5 |
| --------------- | --------------  |
| Reconstructed positions (x, y, z) | :heavy_check_mark: |
| Mass-to-charge-state-ratio values (m/q) | :heavy_check_mark: |

| pyccapt range | NeXus/HDF5 |
| --------------- | --------------  |
| (Molecular ion) number of elements and their multiplicity | :heavy_check_mark: |
| Mass-to-charge-state-ratio value interval for each molecular ion | :heavy_check_mark: |
| Charge state | :heavy_check_mark: |

# APT

The pynxtools-apm parser and normalizer reads the following content and maps them on respective NeXus concepts that are defined in the NXapm application definition:

| APT | NeXus/HDF5 |
| --------------- | --------------  |
| Reconstructed positions (x, y, z) | :heavy_check_mark: |
| Mass-to-charge-state-ratio values (m/q) | :heavy_check_mark: |

The APT file format is a proprietary binary file format maintained by AMETEK/Cameca that contains additional pieces of information over traditionally used POS and ePOS formats.
The ifes_apt_tc_data_modeling library>=0.2.1 can read all these information to the level of detail that has been communicated to the public by AMETEK/Cameca.
The parser is currently not mapping most of these data to NeXus although this is technically possible.

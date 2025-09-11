# ePOS

The pynxtools-apm parser and normalizer reads the following content and maps them on respective NeXus concepts that are defined in the NXapm application definition:

| ePOS | NeXus/HDF5 |
| --------------- | --------------  |
| Reconstructed positions (x, y, z) | :heavy_check_mark: |
| Mass-to-charge-state-ratio values (m/q) | :heavy_check_mark: |

The file format contains additional pieces of information. The ifes_apt_tc_data_modeling library>=0.2.1
can read all these information but the parser is currently not mapping it on NeXus.

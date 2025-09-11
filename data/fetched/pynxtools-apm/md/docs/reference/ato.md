# ATO

The pynxtools-apm parser and normalizer reads the following content and maps them on respective NeXus concepts that are defined in the NXapm application definition:

| ATO | NeXus/HDF5 |
| --------------- | --------------  |
| Reconstructed positions (x, y, z) | :heavy_check_mark: |
| Mass-to-charge-state-ratio values (m/q) | :heavy_check_mark: |

The ATO format has been used in different places for different types of instruments. The format has
seen an evolution of versions. Documentation for these in the scientific literature though is incomplete
and not fully consistent. The ifes_apt_tc_data_modeling library reads v3 and v5 and applies
a scaling to the reconstructed positions.

<span style="color:red">Users of this parsing functionality should inspect carefully whether results
such as reconstructed ion positions are parsed correctly. If this is not the case, it can safely be
considered as a bug. In this case we would appreciate if you can file a [bug/issue here](https://github.com/atomprobe-tc/ifes_apt_tc_data_modeling)
so that we can fix such remaining issues with this parser.</span>

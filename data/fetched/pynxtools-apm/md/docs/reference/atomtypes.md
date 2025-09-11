# Automated extraction of elements in the dataset

All ranging definitions are post-processed by the parser to infer the elements. The set of unique chemical symbols
for these elements is used to define the `/ENTRY[entry*]/specimen/atom_types` in the resulting NeXus/HDF5 file in accordance with the
requirements that are defined by the `NXapm` application definition. NOMAD reads from this field during the nexus
parsing stage into NOMAD Metainfo to enable element-specific search capabilities via the periodic table widget.

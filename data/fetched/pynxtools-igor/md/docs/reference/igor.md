# Data from Igor Pro

The igor reader allows reading data from Wavemetrics Igor Pro `.ibw` "binary wave" files and `.pxp` "packed experiment" files. These two modes of operation are mutually exclusive, i.e. you can either pass one or multiple ibw files, or one pxp file. The behavior of the reader is controlled via two config files: `config.json` defines the assignment to nexus class paths, whereas `entries.yaml.entry` defines which data to read from the source file(s). Here we explain several examples how to use the reader. These examples convert to the nexus class `NXroot`, the most generic Nexus class, but any other NeXus application definition can also be used.

## Convert from ``.ibw`` Igor binary wave files
The conversion from `.ibw` files does not require the definition of an entry file. In that case, each ibw file generates an entry with the filename (excluding ".ibw") as entry name. Axis data as well as units are read from the ibw wave information (internal wave scaling), and named `axis0` to `axis3`. These are available via the `@data` mechanism. Wave notes are parsed and split according to a `key=value\\n` schema, and are available vie the `@attrs` mechanism.

Alternatively, an entry definition can be passed in addition, which contains a dictionary of entries, where each entry key generates an entry of that name. The dict entries are expected to be dicts as well, containing at least the key `data` with the filename of the respective ibw file to use as data for this entry. Additionally, `axisN_name` keys can be passed to rename the axis entries from the default `axis0` to `axis3`. Similarly, `axisN_units` and `data_units` can be passed to overwrite respective information read from the ibw files. ibw files for which no entry has been defined will generate an entry according to their filename as before. Additionally, each entry can contain a `metadata` dict with additional metadata specific to this entry.

This entry dict can be passed as an object, in which case it is expected as sole and single object in the objects tuple. Alternatively, the `entry` dict can also be passed as yaml file with extension `.entry`.

## Conversion from Igor packed experiment files
Conversion from ``.pxp`` files requires definition of an entry dict. Here also, each key/value defines one entry to generate in the Nexus file. the ``data`` entry contains here the ibw-path to the wave to use as main data entry. Axis information can be either read from the wave scaling, or be provided via an ``axisN`` entry, pointing to a wave containing axis information. Similarly, a ``data_errors`` key can be defined, pointing to a wave containing data uncertainties.

The reader for Igor Pro data can be found [here](https://github.com/FAIRmat-NFDI/pynxtools-igor/blob/main/src/pynxtools_igor/reader.py).

Example data for the igor reader is available [here](https://github.com/FAIRmat-NFDI/pynxtools-igor/tree/main/tests/data).

The example conversion can be run with the following command.
```console
user@box:~$ 
dataconverter --reader igor --nxdl NXroot --output example_pxp.nxs config_file.json Fig2a.pxp Scan57_59.yaml.entry
```

The reader is a tailored parser for research data in a common format. This particular example is able to read and map HDF5 files, as well as JSON and YAML files. Feel free to contact FAIRmat if you want to create a parser for your research data.


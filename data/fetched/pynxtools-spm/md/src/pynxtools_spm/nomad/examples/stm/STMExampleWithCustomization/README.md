# SPM Reader
This is an example of handling STM data (using the STM reader) in NOMAD. The prime purpose of the reader is to transform data from measurement files into community-defined concepts constructed by the SPM community which allows experimentalists to store, organize, search, analyze, and share experimental data (only within the [NOMAD](https://nomad-lab.eu/nomad-lab/) platform) among the scientific communities. The reader builds on the [NXstm](https://fairmat-nfdi.github.io/nexus_definitions/classes/contributed_definitions/NXstm.html#nxstm) application definition. For conversion, the reader needs an experimental file, a config file (a mapping between the raw data and the concepts in the application definitions; the config file could be optional for specific vendor files and software version) and a eln file to transform the experimental data into the [NXstm](https://fairmat-nfdi.github.io/nexus_definitions/classes/contributed_definitions/NXstm.html#nxstm) application concepts.

## Supported File Formats and File Versions

- Can parse Scanning Tunneling Microscopy (STM) from
    - `.sxm` file format from Nanonis:
        - Versions: Generic 5e, Generic 4.5
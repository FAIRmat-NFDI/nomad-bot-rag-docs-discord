# SPM Reader
This is an example of handling STS data (using the STS reader) in NOMAD. The prime purpose of the reader is to transform data from measurement files into community-defined concepts constructed by the SPM community which allows experimentalists to store, organize, search, analyze, and share experimental data (only within the [NOMAD](https://nomad-lab.eu/nomad-lab/) platform) among the scientific communities. The reader builds on the [NXsts](https://fairmat-nfdi.github.io/nexus_definitions/classes/contributed_definitions/NXsts.html#nxsts) application definition. For conversion, the reader needs an experimental file, a config file (a mapping between the raw data and the concepts in the application definitions; the config file could be optional for specific vendor files and software version) and a eln file to transform the experimental data into the [NXsts](https://fairmat-nfdi.github.io/nexus_definitions/classes/contributed_definitions/NXsts.html#nxsts) application concepts.

## Supported File Formats and File Versions

- Can parse Scanning Tunneling Spectroscopy (STS) from
    - `.dat` file format from Nanonis:
        - Versions: Generic 5e, Generic 4.5
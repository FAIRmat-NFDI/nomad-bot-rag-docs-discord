# STS Reader
This is an example of STS in NOMAD. The example can be utilised to upload the experimental data from STS experiment, still needs to modify the the config file according to the data structure in experiments (but you still need to modify the config file according to the data structure in experimental file). In order to understand the reader functionality and config file structure, please visit the [reader documentation](https://fairmat-nfdi.github.io/pynxtools-stm/).

The prime purpose of the reader is to transform data from measurement files into community-defined concepts constructed by the SPM community which allows experimentalists to store, organize, search, analyze, and share experimental data among the scientific communities. The reader builds on the [NXsts](https://github.com/FAIRmat-NFDI/nexus_definitions/blob/fairmat/contributed_definitions/NXsts.nxdl.xml) application definition and needs an experimental file, a config file and a eln file to transform the experimental data into the [NXsts](https://github.com/FAIRmat-NFDI/nexus_definitions/blob/fairmat/contributed_definitions/NXsts.nxdl.xml) application concepts.

## Supported File Formats and File Versions

- Can parse Scanning Tunneling Spectroscopy (STS) from
    - `.dat` file format from Nanonis:
        - Versions: Generic 5e, Generic 4.5
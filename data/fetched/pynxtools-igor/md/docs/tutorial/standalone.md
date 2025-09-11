# Convert Igor pro data and metadata to NeXus

## Who is this tutorial for?

This document is for people who want to use this reader as a standalone application for converting their research data
into a standardized NeXus format.

## What should you should know before this tutorial?

- You should have a basic understanding of [FAIRmat NeXus](https://github.com/FAIRmat/nexus_definitions) and [pynxtools](https://github.com/FAIRmat/pynxtools)
- You should have a basic understanding of using Python and Jupyter notebooks via [JupyterLab](https://jupyter.org)

## What you will know at the end of this tutorial?

You will have a basic understanding how to use pynxtools-igor for converting your Igor Pro data to a NeXus/HDF5 file.

## Steps

### Installation
See [here](./installation.md) for how to install pynxtools together with the Igor reader plugin.

### Running the reader from the command line
An example script to run the igor reader in `pynxtools`:
```sh
 ! dataconverter \
--reader igor \
--nxdl NXroot \
$<igor-file path> \
$<eln-file path> \
$<entry-file path> \
-c $<config-file path> \
--output <output-file path>.nxs
```

### Examples

You can find various examples how to use `pynxtools-igor` for your Igor Pro research data pipeline in [`src/pynxtools-igor/nomad/examples`](../../src/pynxtools_igor/nomad/examples/). These are designed for working with [`NOMAD`](https://nomad-lab.eu/) and its [`NOMAD Remote Tools Hub (NORTH)`](https://nomad-lab.eu/prod/v1/gui/analyze/north).

There are also small example files for using the `pynxtools` dataconverter with the `igor` reader in [`tests/data`](https://github.com/FAIRmat-NFDI/pynxtools-igor/tree/main/tests/data).

For this tutorial, we will work with this data. You can run the conversion as
```shell
dataconverter \\
    --reader igor \\
    --nxdl NXroot \\
    Norm_0057.ibw \\
    Norm_0059.ibw \\
    -c  config_file.json \\
    --output example_ibw.nxs
```

**Congrats! You now have a NeXus file generated from the igor binary wave files!**

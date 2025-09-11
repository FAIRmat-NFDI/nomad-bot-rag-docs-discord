# Convert MPES data and metadata to NeXus

## Who is this tutorial for?

This document is for people who want to use this reader as a standalone application for converting their research data
into a standardized NeXus format.

## What should you should know before this tutorial?

- You should have a basic understanding of [FAIRmat NeXus](https://github.com/FAIRmat/nexus_definitions) and [pynxtools](https://github.com/FAIRmat/pynxtools)
- You should have a basic understanding of using Python and Jupyter notebooks via [JupyterLab](https://jupyter.org)

## What you will know at the end of this tutorial?

You will have a basic understanding how to use pynxtools-mpes for converting your MPES data to a NeXus/HDF5 file.

## Steps

### Installation
See [here](./installation.md) for how to install pynxtools together with the MPES reader plugin.

### Running the reader from the command line
An example script to run the MPES reader in `pynxtools`:
```sh
 ! dataconverter \
--reader mpes \
--nxdl NXmpes_arpes \
$<mpes-file path> \
$<eln-file path> \
-c $<config-file path> \
--output <output-file path>.nxs
```

### Examples

You can find exhaustive examples how to use `pynxtools-mpes` for your ARPES research data pipeline in [`src/pynxtools-mpes/nomad/examples`](../../src/pynxtools_mpes/nomad/examples/). These are designed for working with [`NOMAD`](https://nomad-lab.eu/) and its [`NOMAD Remote Tools Hub (NORTH)`](https://nomad-lab.eu/prod/v1/gui/analyze/north).

There are also small example files for using the `pynxtools` dataconverter with the `mpes` reader and the `NXmpes` application definition in [`tests/data`](https://github.com/FAIRmat-NFDI/pynxtools-mpes/tree/main/tests/data).

For this tutorial, we will work with this data. You can run the conversion as
```shell
dataconverter \\
    --reader mpes \\
    --nxdl NXmpes_arpes \\
    xarray_saved_small_calibration \\
    eln_data.yaml \\
    -c  config_file.json \\
    --output mpes_example.nxs
```

**Congrats! You now have a FAIR NeXus file!**

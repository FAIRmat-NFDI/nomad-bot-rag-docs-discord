# Convert electron microscopy data and metadata to NeXus

## Who is this tutorial for?

This document is for people who want to standardize their research data by converting these
into a NeXus standardized format.

## What should you know before this tutorial?

- You should have a basic understanding of [FAIRmat NeXus](https://github.com/FAIRmat/nexus_definitions) and [pynxtools](https://github.com/FAIRmat/pynxtools)
- You should have a basic understanding of using Python and Jupyter notebooks via [JupyterLab](https://jupyter.org)

## What you will know at the end of this tutorial?

You will have a basic understanding how to use pynxtools-apm for converting your APM data to a NeXus/HDF5 file.
## Steps

### Installation

See [here](installation.html) for how to install pynxtools together with the APM reader plugin. Note that the reader is a combination of multiple readers each supporting a different set of versions of file formats used by key technology partners from the field of electron microscopy.

### Running the reader from the command line

An example script to run the APM reader in `pynxtools`:

```console
user@box:~$ dataconverter $<apm-file path> $<apm-file path> $<eln-file path> --reader apm --nxdl NXapm --output <output-file path>.nxs
```

Note that typically none of the supported file formats have data/values for all required and recommended fields and attributes in ``NXapm``. In order for the validation step of the APM reader to pass, you need to provide an ELN file that contains the missing values if you would like to be fully compliant with the NXapm standard.

### Examples

You can find examples how to use `pynxtools-apm` for your APM research data pipeline in `src/pynxtools_apm/nomad/examples`. These are designed for working with [`NOMAD`](https://nomad-lab.eu/) and its [`NOMAD Remote Tools Hub (NORTH)`](https://nomad-lab.eu/prod/v1/gui/analyze/north).

<!-- [The Jupyter notebook is available here](https://github.com/FAIRmat-NFDI/pynxtools-apm/blob/main/examples/HowToUseTutorial.ipynb)-->

**Congrats! You now have a FAIR NeXus file!**


[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![](https://github.com/FAIRmat-NFDI/pynxtools-raman/actions/workflows/pytest.yml/badge.svg)
![](https://github.com/FAIRmat-NFDI/pynxtools-raman/actions/workflows/pylint.yml/badge.svg)
![](https://github.com/FAIRmat-NFDI/pynxtools-raman/actions/workflows/publish.yml/badge.svg)
![](https://img.shields.io/pypi/pyversions/pynxtools-raman)
![](https://img.shields.io/pypi/l/pynxtools-raman)
![](https://img.shields.io/pypi/v/pynxtools-raman)
![](https://coveralls.io/repos/github/FAIRmat-NFDI/pynxtools_raman/badge.svg?branch=main)

# A reader for raman data

## Installation

It is recommended to use python 3.12 with a dedicated virtual environment for this package.
Learn how to manage [python versions](https://github.com/pyenv/pyenv) and
[virtual environments](https://realpython.com/python-virtual-environments-a-primer/).

This package is a reader plugin for [`pynxtools`](https://github.com/FAIRmat-NFDI/pynxtools) and thus should be installed together with `pynxtools`:


```shell
pip install pynxtools[raman]
```

for the latest development version.

## Purpose
This reader plugin for [`pynxtools`](https://github.com/FAIRmat-NFDI/pynxtools) is used to translate diverse file formats from the scientific community and technology partners
within the field of raman into a standardized representation using the
[NeXus](https://www.nexusformat.org/) application definition [NXraman](https://fairmat-nfdi.github.io/nexus_definitions/classes/contributed_definitions/NXraman.html#nxraman).


## Step-by-Step Example
Download the repository via git clone:
```shell
git clone https://github.com/FAIRmat-NFDI/pynxtools-raman.git
```
Switch to the project root folder:
```shell
cd pynxtools-raman
```
You see three Folders:
- examples: contains example datasets to show how the data conversion is done (currently one example from WITec and one example from the Raman Open Database)
- tests: contains a test procedure and files, which are required for software development
- src/pynxtools_raman: source files, which contain the sub-reader function for Raman experiments. This only works in combination with the Python package [pynxtools](https://github.com/FAIRmat-NFDI/pynxtools). This is a specialization of the [Multiformat Reader](https://fairmat-nfdi.github.io/pynxtools/how-tos/use-multi-format-reader.html). There are as well sub-reader functions for a WITec device and files from the [Raman Open Database](https://solsa.crystallography.net/rod/new.html?CODSESSION=f4b7fb6d2jsataebeph9qkchue). In addition, config.json files are located in src/pynxtools_raman/config. These are necessary to map the input data via the Multiformat Reader to the NeXus concepts. These config files allow individual adjustments, as different laboratories may have different electronic lab notebook structures.

Consider setting up an invididual [python environment](https://realpython.com/python-virtual-environments-a-primer/), to seperate the python fuctnionalities of this package from the python funtionalities of your operating system:
For Ubuntu-based systems:
```shell
python -m venv .pyenv
source .pyenv/bin/activate
```
Verify its location via:
```shell
which python
```
It should point to the python folder, you created above with the name `.pyenv`.


Install the python package:
```shell
pip install .
```
**Perform a data conversion**
for the WITec dataset via:
```shell
dataconverter examples/witec/txt/eln_data.yaml examples/witec/txt/Si-wafer-Raman-Spectrum-1.txt src/pynxtools_raman/config/config_file_witec.json --reader raman --nxdl NXraman --output new_witec_example_neuxs.nxs
```

and for the Raman Open Database dataset set via:
```shell
dataconverter examples/database/rod/rod_file_1000679.rod src/pynxtools_raman/config/config_file_rod.json --reader raman --nxdl NXraman --output new_rod_example_neuxs.nxs
```

**For Example for the Raman Open Database command:**
- You assign the reader name via `--reader raman`.
- You assign the NeXus application definition, on which the output will be based via `--nxdl NXraman`.
- You specify the name and path of the output file via `--output new_rod_example_neuxs.nxs`.
- You assign an individualized config file via `src/pynxtools_raman/config/config_file_rod.json`. The config file is detected by its extension `.json`.
- You give the file which includes the meta and measurement data via `examples/database/rod/rod_file_1000679.rod`. The parser is specified to detect the `.rod` file, and handle the content appropriately.

Then you can inspect the generated file at [this website](https://h5web.panosc.eu/h5wasm) or in VScode via the extension "H5web".

## Docs
Extensive documentation of this pynxtools plugin is available [here](https://fairmat-nfdi.github.io/pynxtools-raman/). You can find information about getting started, how-to guides, the supported file formats, how to get involved, and much more there.

## Contact person in FAIRmat for this reader
Ron Hildebrandt

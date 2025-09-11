[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![](https://github.com/FAIRmat-NFDI/pynxtools-apm/actions/workflows/pytest.yml/badge.svg)
![](https://github.com/FAIRmat-NFDI/pynxtools-apm/actions/workflows/pylint.yml/badge.svg)
![](https://github.com/FAIRmat-NFDI/pynxtools-apm/actions/workflows/publish.yml/badge.svg)
![](https://img.shields.io/pypi/pyversions/pynxtools-apm)
![](https://img.shields.io/pypi/l/pynxtools-apm)
![](https://img.shields.io/pypi/v/pynxtools-apm)
![](https://coveralls.io/repos/github/FAIRmat-NFDI/pynxtools-apm/badge.svg?branch=main)
[![DOI](https://zenodo.org/badge/772049905.svg)](https://zenodo.org/badge/latestdoi/772049905)

# Parse and normalize atom probe tomography and field-ion microscopy data

## Installation
It is recommended to use python 3.12 with a dedicated virtual environment for this package.
Learn how to manage [python versions](https://github.com/pyenv/pyenv) and
[virtual environments](https://realpython.com/python-virtual-environments-a-primer/).

This package is a reader plugin for [`pynxtools`](https://github.com/FAIRmat-NFDI/pynxtools) and thus should be installed together with `pynxtools`:
```shell
pip install pynxtools[apm]
```

for the latest release version from [pypi](https://pypi.org/project/pynxtools-apm/).

If you are interested in the newest version, we recommend to work with a development installation instead.

## Purpose
This reader plugin for [`pynxtools`](https://github.com/FAIRmat-NFDI/pynxtools) is used to translate diverse file formats from the scientific community and technology partners
within the field of atom probe tomography and field-ion microscopy into a standardized representation using the
[NeXus](https://www.nexusformat.org/) application definition [NXapm](https://fairmat-nfdi.github.io/nexus_definitions/classes/applications/NXapm.html#nxapm).

## Supported file formats
This plugin supports the majority of the file formats that are currently used for atom probe research.
A detailed summary is available in the [reference section of the documentation](https://fairmat-nfdi.github.io/pynxtools-apm).

## Getting started
[A getting started tutorial](https://github.com/FAIRmat-NFDI/pynxtools-apm/tree/main/examples) is offered that guides you
on how to use the apm reader for converting your data to NeXus from a Jupyter notebook or command line calls. Note that not every combination of input from a supported file format and other input, such as from an electronic lab notebook, allows filling all required and recommended fields including their attributes of the NXapm
application definition. Therefore, you may need to provide an ELN file that contains the missing values in order for the
validation step of the EM reader to pass.


## Contributing
We are continously working on improving the collection of parsers and their functionalities.
If you would like to implement a parser for your data, feel free to get in contact.

## Development install
Install the package with its dependencies:

```shell
git clone https://github.com/FAIRmat-NFDI/pynxtools-apm.git --branch main --recursive pynxtools_apm
cd pynxtools_apm
python -m pip install --upgrade pip
python -m pip install -e ".[dev,docs]"
pre-commit install
```

The last line installs a [pre-commit hook](https://pre-commit.com/#intro) which
automatically formats (linting) and type checks the code before committing.

## Test this software
Especially relevant for developers, there exists a basic test framework written in
[pytest](https://docs.pytest.org/en/stable/) which can be used as follows:

```shell
python -m pytest -sv tests
```

## Contact person in FAIRmat for this reader
[Markus Kühbach](https://www.fairmat-nfdi.eu/fairmat/about-fairmat/team-fairmat)

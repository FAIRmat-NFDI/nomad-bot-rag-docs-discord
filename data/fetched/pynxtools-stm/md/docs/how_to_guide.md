# How-To-Guide
## How-To Install STM Reader
Installing STM reader is as simple as installing python package from PyPI. We recommend to install the reader in a python virtual environment.
### Installation of STM reader in python virtual envrironment
Run the followoing command step-by-step on your linux terminal

```bash
<user>$ vitualenv --python=3.10 .pyenv
<user>$ source activate .pyenv/bin/activate
(.pyenv) <user>$ pip install pynxtools-stm
```

That's it! You can run the `STM` reader from command line.

### Installation of STM reader in development mode in python virtual environment
Install `STM` reader to develop according to you own expectation
```bash
<user>$ vitualenv --python=3.10 .pyenv
<user>$ source activate .pyenv/bin/activate
(.pyenv) <user>$ git clone https://github.com/FAIRmat-NFDI/pynxtools-stm
(.pyenv) <user>$ cd pynxtools-stm
(.pyenv) <user>$ python -m pip install --upgrade pip
(.pyenv) <user>$ pip install -e .
(.pyenv) <user>$ pip install -e ".[dev]"
```

## How-To Run the Reader from CLI
In the command line interface, input files can be passed as positional arguments. Other arguments like the `reader` and the `nxdl` shall be given as keyword arguments.
## Run STS Reader
The following command can be used to run the `STS` reader from your python environment:
```bash
(.pyenv) <user>$ dataconverter \
--reader sts \
--nxdl NXsts \
--output ./output.nxs \ 
<path-to STS_nanonis_generic_5e_1.dat> \
<path-to config_file_for_dat.json> \
<path-to Nanonis_Eln.yaml>
```

## Run STM Reader
Use the following command to run the `STM` reader from your python environment:
```bash
(.pyenv) <user>$ dataconverter \
--reader sts \
--nxdl NXsts \
--output ./output.nxs \
<path-to STM_nanonis_generic_5e.sxm> \
<path-to config_file_for_sxm.json> \
<path-to Nanonis_Eln.yaml> \
```
## Want to Contribute or Extend the Reader Functionality
We appreciate any comments, extentions or improvements on the existing reader from users. Currently the reader supports the versions `4.5`, `5e` from `Generic` model of `Nanonis` vendor. To include the other versions of the `Generic` model, extend the class `StmNanonisGeneric` and `StsNanonisGeneric` by including versions in `__version__` attribute. Also include the model and version of the brand in `Spm` class. 
### How to Contribute or Extend the Reader Functionality
If you want to add the different versions of the `Nanonis Generic` model for `STM` experiment, please check the `STM_Nanonis` class for `STM` experiment, which parses the data into a python dict of slash (`/`) separated key-value pair (see the right part of the config file). The class uses the `nanonispy` sub-package to read the `sxm` type file. That should also be checked and modified (if needed).

If you add different versions of the `Nanonis Generic` model for `STS` experiment, please check the `BiasSpecData_Nanonis` class for `STS` experiment. The class reads the raw data from the raw files into a dict of slash separated key-value pair (see the config file). 

If you go for a completely different model (e.g., from a different brand), please handle it in a new module with different functions and classes. 

Later on, please add the relevant tests in the plugin test.

Done! Great, then please create a pull request.

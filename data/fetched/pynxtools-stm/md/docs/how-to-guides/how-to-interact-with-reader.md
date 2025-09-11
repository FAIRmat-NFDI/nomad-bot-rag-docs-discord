# How to Use the STM Reader
## How To Install the STM Reader
The STM reader can be installed as a python package from PyPI. We recommend to install the reader in a python virtual environment.
### Installation of STM reader in python virtual envrironment
Run the followoing command step-by-step on your linux terminal

```bash
<user>$ vitualenv --python=3.10 .pyenv
<user>$ source activate .pyenv/bin/activate
(.pyenv) <user>$ pip install pynxtools-stm
```

That's it! You can run the `STM` reader from command line.

### Installation of STM reader in development mode in python virtual environment
If you want to make changes to the `STM` reader, you can install in to development mode
```bash
<user>$ vitualenv --python=3.10 .pyenv
<user>$ source activate .pyenv/bin/activate
(.pyenv) <user>$ git clone https://github.com/FAIRmat-NFDI/pynxtools-stm
(.pyenv) <user>$ cd pynxtools-stm
(.pyenv) <user>$ python -m pip install --upgrade pip
(.pyenv) <user>$ pip install -e .
(.pyenv) <user>$ pip install -e ".[dev]"
```

## How to Run the Reader from CLI
In the command line interface, input files can be passed as positional arguments. Other arguments like the `reader` and the `nxdl` shall be given as keyword arguments.
### Run STS Reader
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

### Run STM Reader
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

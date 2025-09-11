# Data from MPES instruments

The reader supports [HDF5](https://www.hdfgroup.org/solutions/hdf5/) files created using the MPES instruments at the Department of Physical Chemistry of the [Fritz Haber Institute of the Max Planck Society (FHI)](https://pc.fhi-berlin.mpg.de).

The reader for can be found [here](https://github.com/FAIRmat-NFDI/pynxtools-mpes/blob/main/src/pynxtools_mpes/reader.py).

Example data for the MPES reader is available [here](https://github.com/FAIRmat-NFDI/pynxtools-mpes/tree/main/tests/data).

The example conversion can be run with the following command.
```console
user@box:~$ 
dataconverter xarray_saved_small_calibration.h5 eln_data.yaml -c config_file.json --reader mpes --nxdl NXmpes_arpes --output example_eln.nxs
```

The reader is a tailored parser for research data in a common format. This particular example is able to read and map HDF5 files, as well as JSON and YAML files. Feel free to contact FAIRmat if you want to create a parser for your research data.


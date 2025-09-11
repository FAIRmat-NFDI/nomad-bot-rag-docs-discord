# WITec


This is an example dataset to convert a .txt file (exported ASCII file,
Si-wafer-Raman-Spectrum-1.txt) with the addition of a ELN data file (eln_data.yaml)
to a NeXus file.

## Convert example data
- Go into the root folder of this repository (default "pynxtools-raman")
- Copy and paste:
    ```
    dataconverter examples/witec/txt/eln_data.yaml examples/witec/txt/Si-wafer-Raman-Spectrum-1.txt src/pynxtools_raman/config/config_file_witec.json --reader raman --nxdl NXraman --output examples/witec/txt/witec_example_neuxs.nxs
    ```
- A new file should be created at `examples/witec/txt/witec_example_neuxs.nxs`.
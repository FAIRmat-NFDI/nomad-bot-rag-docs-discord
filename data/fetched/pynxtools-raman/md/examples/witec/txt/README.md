## WITEC example Raman Multiformat Reader
This is an example dataset to convert a .txt file
(exported ASCII file, Si-wafer-Raman-Spectrum-1.txt) with the addition of a ELN
data file (eln_data.yaml) to a NeXus file.

## How to use
- 1. Go into the root folder of this repository (default "pynxtools-raman")
- 2. Copy and paste:
    ```
    dataconverter examples/witec/txt/eln_data.yaml examples/witec/txt/Si-wafer-Raman-Spectrum-1.txt src/pynxtools_raman/config/config_file_witec.json --reader raman --nxdl NXraman --output examples/witec/txt/witec_example_neuxs.nxs
    ```
- 3. A new file should be created at "examples/witec/txt/witec_example_neuxs.nxs".
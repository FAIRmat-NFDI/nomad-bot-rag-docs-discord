# ROD
This shows two examples in which `.rod` files from the [Raman Open Database (ROD)](https://solsa.crystallography.net/rod/) are converted to NeXus `.nxs` files.

## Convert example data
- Clone the [GitHub repository and install the latest development version](../how-tos/installation.md)
- Go into the root folder of this repository (default `pynxtools-raman`)
- Copy and paste:
    ```
    dataconverter examples/database/rod/rod_file_1000679.rod src/pynxtools_raman/config/config_file_rod.json --reader raman --nxdl NXraman --output examples/database/rod/rod_example_neuxs.nxs
    ```
- Inspect the created NeXus file. Some warnings may be present.

  

## Convert downloaded ROD files


**Convert single file**

Using the [pynxtools dataconverter](https://fairmat-nfdi.github.io/pynxtools/learn/dataconverter-and-readers.html) with the pynxtools-raman reader plugin:

```shell
dataconverter <PATH_TO>/1000679.rod src/pynxtools_raman/config/config_file_rod.json --reader raman --nxdl NXraman --output rod_example_nexus.nxs
```


**Convert multiple files**

Take a look at the [bash script](https://github.com/FAIRmat-NFDI/pynxtools-raman/blob/main/src/download_rod_files/convert_all_rod_to_nxs.sh) and make it executable: `chmod +x convert_all_rod_to_nxs.sh`.

Call the script `./src/download_rod_files/convert_all_rod_to_nxs.sh`.
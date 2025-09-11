# Convert Data to NeXus files

for the WITec dataset via:
```shell
dataconverter examples/witec/txt/eln_data.yaml examples/witec/txt/Si-wafer-Raman-Spectrum-1.txt src/pynxtools_raman/config/config_file_witec.json --reader raman --nxdl NXraman --output new_witec_example_neuxs.nxs
```

and for the Raman Open Database dataset set via:
```shell
dataconverter examples/database/rod/rod_file_1000679.rod src/pynxtools_raman/config/config_file_rod.json --reader raman --nxdl NXraman --output new_rod_example_neuxs.nxs
```



**Explanation for the Raman Open Database commands:**

- You assign the reader name via `--reader raman`.
- You assign the NeXus application definition, on which the output will be based via `--nxdl NXraman`.
- You specify the name and path of the output file via `--output new_rod_example_neuxs.nxs`.
- You assign an individualized config file via `src/pynxtools_raman/config/config_file_rod.json`. The config file is detected by its extension `.json`.
- You give the file which includes the meta and measurement data via `examples/database/rod/rod_file_1000679.rod`. The parser is specified to detect the `.rod` file, and handle the content appropriately.

Then you can inspect the generated file at [this website](https://h5web.panosc.eu/h5wasm) or in VScode via the extension `H5web`.
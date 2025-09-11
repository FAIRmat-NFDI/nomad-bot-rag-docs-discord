# Downloading multiple .rod files

## Manually downloading

If you have installed pynxtools-raman you cann add a new command to
download .rod files. For example, you can download a rod file with
`ÌD=1000679` via: `download_rod_file 1000679`.


## Download_rods_script.sh

Adjust the file `download_rods_script.sh`to the range of download you want.
Default start is `1` and default end is `3`.
Please, do not trigger unnecessary multiple amounts of downloads.

Take a look [here](https://solsa.crystallography.net/rod/result), to get valid .rod IDs.
The list of .rod IDs can be accessed [here](https://solsa.crystallography.net/rod/result.php?format=lst&CODSESSION=ooqj2idj19cgpe30275okg42df).
## Make the bash script executable

`chmod +x download_rods_script.sh`

## Execute the script

`./src/download_rod_files/download_rods_script.sh`


## Convert the downloaded .rod files

Using the [pynxtools dataconverter](https://fairmat-nfdi.github.io/pynxtools/learn/dataconverter-and-readers.html) with the pynxtools-raman reader plugin:


`dataconverter <PATH_TO>/1000679.rod src/pynxtools_raman/config/config_file_rod.json --reader raman --nxdl NXraman --output rod_example_nexus.nxs`

## Downloading all .rod files

Take a look at the file: "download_all_rod_files_script.sh"

# Automatic conversion of all .rod files to .nxs files

## Make the bash script executable
`chmod +x convert_all_rod_to_nxs.sh`

## Call the script
`./src/download_rod_files/convert_all_rod_to_nxs.sh`


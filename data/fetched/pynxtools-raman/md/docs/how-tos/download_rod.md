# Downloading ROD files

This how-to shows how to download single or multiple files from the
[Raman Open Database](https://solsa.crystallography.net/rod/).

## Download of individual ROD files

If you have installed [pynxtools-raman](https://github.com/FAIRmat-NFDI/pynxtools-raman/) you can add a new command to download `.rod files`. For example, you can download a rod file with the ID
`1000679` via:
```
download_rod_file 1000679
```


## Download of multiple ROD files

Adjust the file `download_rods_script.sh`to the range of download you want.
Default start is `1` and default end is `3`.
Please, do not trigger unnecessary multiple amounts of downloads.

Take a look [here](https://solsa.crystallography.net/rod/result), to get valid .rod IDs.
The list of .rod IDs can be accessed [here](https://solsa.crystallography.net/rod/result.php?format=lst&CODSESSION=ooqj2idj19cgpe30275okg42df).


Make the bash script executable

```shell
chmod +x download_rods_script.sh
```

and execute the script

```
./src/download_rod_files/download_rods_script.sh
```



## Download of all ROD files

Take a look at the file: `download_all_rod_files_script.sh`



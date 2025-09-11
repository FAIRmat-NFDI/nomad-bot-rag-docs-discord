# Config file and customized data conversion

The `pynxtools-raman` package enables the dataconversion from experimental data to
a NeXus file whereby the [NXraman](https://fairmat-nfdi.github.io/nexus_definitions/classes/contributed_definitions/NXraman.html) application definition is used.
The dataconverter of `pynxtools-raman` is based on the [`MultiformatReader`](https://fairmat-nfdi.github.io/pynxtools/how-tos/use-multi-format-reader.html) from the `pynxtools` package. This allows using JSON config files to map pre-structured experimental data to NeXus concepts. You can learn more about the `MultiFormatReader` in the documentation of the `pynxtools` package ([here](https://fairmat-nfdi.github.io/pynxtools/learn/multi-format-reader.html) and [here](https://fairmat-nfdi.github.io/pynxtools/how-tos/use-multi-format-reader.html).

## How does the pre-structured experimental data look like?

Human-readable structured text formats are used for this. Examples are `.yaml`or `.json`. This looks like that:

```yaml
data:
  unit_x: nm
  unit_y: counts
  longname_x: Wavelength
  longname_y: Raman Intensity
  longname_x_raman: Raman Shift
instrument:
  scattering_configuration: z(xx)-z
  beam_incident:
    wavelength:
      value: 532.1
      unit: nm
    average_power:
      value: 60
      unit: mW
```

This file is called `eln_data.yaml`and can be found [here](https://github.com/FAIRmat-NFDI/pynxtools-raman/blob/main/tests/data/witec/eln_data.yaml). This is an example for a WITec Raman spectrometer. If you want to use `pynxtools-raman`, you need a small programm or script to parse your own experimental output data to such a pre-structured format.

## What else is required for the data conversion?

Lets take a look at the command, to convert the data for the WITec instrument:

```shell
dataconverter examples/witec/txt/eln_data.yaml examples/witec/txt/Si-wafer-Raman-Spectrum-1.txt src/pynxtools_raman/config/config_file_witec.json --reader raman --nxdl NXraman --output examples/witec/txt/witec_example_nexus.nxs
```

The indiviual commands are explained [here](../how-tos/convert_data.md).

Aside from telling the program which NeXus definition you want to use (`NXraman`) and what reader for the dataconverion to use (`raman`), you have to:

- Define the name of the output file ([`witec_example_neuxs.nxs`](https://github.com/FAIRmat-NFDI/pynxtools-raman/blob/main/tests/data/witec/example.nxs))
- Provide Raman spectra ([`examples/witec/txt/Si-wafer-Raman-Spectrum-1.txt`](https://github.com/FAIRmat-NFDI/pynxtools-raman/blob/main/tests/data/witec/Si-wafer-Raman-Spectrum-1.txt))
- Provide the config file ([`config_file_witec.json`](https://github.com/FAIRmat-NFDI/pynxtools-raman/blob/main/src/pynxtools_raman/config/config_file_witec.json))

While the first two files are rather trivial and just definitions or given by the setup output, the config file is important to tell the program what to do.

## What is the config file good for?

The config file tells the dataconverter to map the information of your data file and the `eln_data.yaml` file to NeXus concepts. This connects your individual experimental data to generalized FAIR-enabling NeXus concepts. In this way, other experimentalists or even machines can pick up the information you provided, and understand exactly, that the information you providedis indeed the excitation wavelength of the beam, which is incident on the sample. It is not the laser, which is used for second-harmonic generation. This description of mapping is essential for FAIR data processing. You have to set this up. This is what the config file is good for.

## Structure of config file

This is how a config file looks like:

```json
{
  "/ENTRY[entry]/INSTRUMENT[instrument]/scattering_configuration": "@eln",
  "/ENTRY[entry]/INSTRUMENT[instrument]/beam_incident/wavelength": "@eln",
  "/ENTRY[entry]/INSTRUMENT[instrument]/beam_incident/wavelength/@units": "@eln",
  "/ENTRY[entry]/INSTRUMENT[instrument]/beam_incident/parameter_reliability": "@eln",
  "/ENTRY[entry]/INSTRUMENT[instrument]/beam_incident/average_power": "@eln",
  "/ENTRY[entry]/INSTRUMENT[instrument]/beam_incident/average_power/@units": "@eln",
  "/ENTRY[entry]/INSTRUMENT[instrument]/beam_incident/associated_source": "@eln",
  "/ENTRY[entry]/DATA[data]/y_values/@units": "@eln:/ENTRY[entry]/data/unit_y",
  "/ENTRY[entry]/DATA[data]/x_values/@units": "@eln:/ENTRY[entry]/data/unit_x",
  "/ENTRY[entry]/DATA[data]/y_values/@long_name": "@eln:/ENTRY[entry]/data/longname_y",
  "/ENTRY[entry]/DATA[data]/x_values/@long_name": "@eln:/ENTRY[entry]/data/longname_x",
  "/ENTRY[entry]/DATA[data]/x_values_raman/@long_name": "@eln:/ENTRY[entry]/data/longname_x_raman",
  "/ENTRY[entry]/DATA[data]/x_values_raman": "@data:data/x_values_raman",
  "/ENTRY[entry]/DATA[data]/x_values_raman/@units": "1/cm"
  }
```

The general structure of the config file is therefore:

```json
{
    "key1":"value1",
    "key2":"value2"
  }
```

You can find more information of the config file in the [pynxtools documentation for the multiformat reader](https://fairmat-nfdi.github.io/pynxtools/learn/multi-format-reader.html#parsing-the-config-file).

### Key Structure

The `key` has the structure of a NeXus concept path. This means that for:

```
"/ENTRY[entry]/INSTRUMENT[instrument]/beam_incident/wavelength"
```
in the NeXus file, the group with the name `entry` is created. This group is given
the attribute `NXclass=NXentry`due to the uppercase `ENTRY`.

Inside the group `entry`, the group with the name `instrument` is created. This group is given
the attribute `NXclass=NXinstrument` due to the uppercase `INSTRUMENT`.

Inside the group `instrument`, the group with the name `beam_incident` is created. As the input of the used NeXus definition is given as well (in this case, `NXraman`), the dataconvert infers that you refer to `beam_incident` in `INSTRUMENT`, as shown in [`NXraman`](https://fairmat-nfdi.github.io/nexus_definitions/classes/contributed_definitions/NXraman.html). Therefore, the group is given the attribute `NXclass=NXbeam`.


Inside the group `beam_incident`, the field with the name `wavelength` is created.

Overall, the key represents a combination of a NeXus concept path with an uppercase notation, to assign the invididual group entries specific NeXus classes.

### Value Structure

The `value`has the structure:

```
@<PREFIX>:<PATH>
```

`@<PREFIX>` can be `@eln`, `@data`or it can be empty.

For example, `@eln:X` calls the function `get_eln_data`in the `reader.py` of `pynxtools-raman` (see [here](https://github.com/FAIRmat-NFDI/pynxtools-raman/blob/ca8f058c35ae0861d8805915e79990a9ee89520e/src/pynxtools_raman/reader.py#L195C1-L195C56)).

Similarly, `@data:X` calls the function `get_data` in the `reader.py` of `pynxtools-raman` (see [here](https://github.com/FAIRmat-NFDI/pynxtools-raman/blob/ca8f058c35ae0861d8805915e79990a9ee89520e/src/pynxtools_raman/reader.py#L246)).

If no prefix is given, i.e. just `X`, assigns the value `X` is assigned to the given NeXus concept path (without a special function to process the data).

### Example of data mapping via config file

Given is the `key:value` pair:

```json
  {
  "/ENTRY[entry]/DATA[data]/y_values/@units":"@eln:/ENTRY[entry]/data/unit_y",
  }
```

The value is `"@eln:/ENTRY[entry]/data/unit_y"`. Therefore, the `@eln` function gets the input `/ENTRY[entry]/data/unit_y`. This tells the dataconverter, to look for the `key = data/unit_y` in the `eln_data.yaml` file. The respective output is `counts`. So, the NeXus concept `entry/data/y_values/@units` will be assigned the string value `counts`. The `@` in `@units` indicates, that the attribute (called `units`) is assigned to the field `y_values`. `y_values` itself is part of the group with name `data` and with the NeXus concept class `NXdata`. The `NXdata` group itself, is inside the `NXentry` group.

**Why are there different functions?**

The reason is, that the values sometimes require different processing steps. Here, for example, the values for `@eln` come
from the `eln_data.yaml` file, while the values for `@data` originate from the `Si-wafer-Raman-Spectrum-1.txt` file.


**Why is for sometimes only the `@<PREFIX>` given, but no `<PATH>`?**

This is a shorter notation, to ease the writing of the config file. For example, the `key:value` pair:
```json
  "/ENTRY[entry]/INSTRUMENT[instrument]/beam_incident/wavelength": "@eln"
```
refers to directly to NeXus concept entry, as the `eln_data.yaml` is structured similar to the NeXus concept (i.e., it has the same keys as the config files). The equivalent notation is: 

```json
  "/ENTRY[entry]/INSTRUMENT[instrument]/beam_incident/wavelength": "@eln:entry/instrument/beam_incident/wavelength"
```
i.e., the data converter removes the `uppercase` symbols and the brackets `[]` from the key. This output then becomes the `<PATH>` in `@<PREFIX>:<PATH>` (the value in the `key:value` pair). In this way, the `@eln` function just performs a path transformation.

## Examples for adjusting the config file

1. You remove `"/ENTRY[entry]/INSTRUMENT[instrument]/beam_incident/wavelength": "@eln"` from the config file, but keep the respective entry in the `eln_data.yaml` file:
The `wavelength` value will not be written into the output NeXus file. Similarly, if your config file is empty, no entry will be generated at all. Even if your `eln_data.yaml` file is full of entries.

2. You keep `"/ENTRY[entry]/INSTRUMENT[instrument]/beam_incident/wavelength": "@eln"` from the config file, but remove the respective entry in the `eln_data.yaml` file:
No value will be assigned and the NeXus entry will not be in the output nexus file. Though, a warning will be invoked in the dataconversion (`WARNING: No key found`).


3. You want to specify, that `beam_incident` is a `NXbeam` class:
Replace `beam_incident` by `BEAM[beam_incident]`

4. The determination of the incident beam wavelength is incorrect, as the device has malfunctioned. But you know the correct value, from earlier measurements (which is 532nm). So you always want that the same value appears in the NeXus file. In that case, you need to write`"/ENTRY[entry]/INSTRUMENT[instrument]/beam_incident/wavelength":532`.

5. You want to add the wavelength of the incident beam wavelength: Change `"@eln"` to `"nm"` for `"/ENTRY[entry]/INSTRUMENT[instrument]/beam_incident/wavelength/@units"`. If the value in the `eln_data.yaml` is still correctly processed, you can keep `"@eln"`.

6. You want to have the NeXus `NXentry` not named `entry` but instead `measurement1`: Change all `/ENTRY[entry]` to `/ENTRY[measurement1]`. To avoid renaming all individual entries in the `.json` config file, you can also structure the file with nested dictionaries, as shown [here](https://fairmat-nfdi.github.io/pynxtools/how-tos/use-multi-format-reader.html) for the `config_file.json`.

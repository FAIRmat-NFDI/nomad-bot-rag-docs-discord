# STS Reader
The prime purpose of the reader is to transform data from measurement files into community-defined concepts constructed by the SPM community which allows experimentalists to store, organize, search, analyze, and share experimental data (only within the [NOMAD](https://nomad-lab.eu/nomad-lab/) platform) among the scientific communities. The reader builds on the [NXsts](https://github.com/FAIRmat-NFDI/nexus_definitions/blob/fairmat/contributed_definitions/NXsts.nxdl.xml) application definition and needs an experimental file, a config file and a eln file to transform the experimental data into the [NXsts](https://github.com/FAIRmat-NFDI/nexus_definitions/blob/fairmat/contributed_definitions/NXsts.nxdl.xml) application concepts. 

## Supported File Formats and File Versions

- Can parse Scanning Tunneling Spectroscopy (STS) from
    - `.dat` file format from Nanonis: 
        - Versions: Generic 5e, Generic 4.5
- Can parse Scanning Tunneling Microscopy (STM) from
    - `.sxm` file format from Nanonis: 
        - Versions: Generic 5e, Generic 4.5

## NeXus Application Definition
To define a standardized schema, we chose the [NeXus format](https://www.nexusformat.org/) and we defined an application definition `NXsts` for standardizing data from `STM` as well as `STS` experiments. You can find the application definition and information on related NeXus base classes on the NeXus-FAIRmat page for [Scanning Tunneling Spectroscopy](https://fairmat-nfdi.github.io/nexus_definitions/sts-structure.html).

## Introduction to Reader Input Files
To utilize, reuse, or extend the reader, the different reader input files must be understood. The files are using specific semantic rules so that reader can understand the files and work with their content.
The input files are:

1. Raw File(s) containing data from experiments
2. ELN (Electronic Lab Notebook) to collect user input data
3. Config file that connect the data to concepts in the NeXus application definition `NXsts`.

### Raw File
This type of file (such as `example.dat` or `example.sxm`) is the data file generated during the experiment. 
### ELN (Electronic Lab Notebook)
This file supports user input data that is not part of the experimental data file. There are two ways to define or write ELN files. The first one can be distinguished, for sake of explanation, as **command line ELN**. This should be a YAML file (with `.yaml` file extension ). Such type of ELN needs to be used to run the reader from the command line. The second one can be called, for sake of explanation, **NOMAD Schema ELN**. This is also a YAML file, but with the extension `.scheme.archive.yaml`. This ELN is needed if the reader is being used from NOMAD. Note that NOMAD will parse the NOMAD Schema ELN into a YAML file of the first type.

The given example below is a short description of the **NOMAD schema ELN** (a complete example can be found [here](https://gitlab.mpcdf.mpg.de/nomad-lab/nomad-remote-tools-hub/-/blob/develop/docker/sts/example/sts_example/STS.scheme.archive.yaml?ref_type=heads)).
```yaml
definitions:
  name: Eln example for STS
  sections:
    stm:
      base_sections:
        - nomad.datamodel.metainfo.eln.NexusDataConverter
        - nomad.datamodel.data.EntryData
      m_annotations:
        template:
          reader: sts
          nxdl: NXsts
        eln:
          hide: []
      quantities:
        default:
          type: str
          m_annotations:
            eln:
              component: StringEditQuantity
          description: |
            The name of the default plot (e.g. li_demod_1_x, current) to be displayed on the entry of NeXus file.
        definition:
          type: 
            type_kind: Enum
            type_data:
              - NXsts
          m_annotations:
            eln:
              component: EnumEditQuantity
          description: ''
        experiment_type:
          type:
            type_kind: Enum
            type_data:
              - sts
              - stm
          m_annotations:
            eln:
              component: EnumEditQuantity
          description: 'Only two type of experiments are allowed: sts and stm.'
      sub_sections:
        Instrument:
          section:
            m_annotations:
              eln:
                overview: true
            quantities:
              stm_head_temp:
                type: np.float64
                unit: K
                m_annotations:
                  eln:
                    component: NumberEditQuantity
                    defaultDisplayUnit: K
                description: |
                  Temperature of STM head. Note: At least one field from stm_head_temperature,
                  cryo_bottom_temp and cryo_sheild_temp must be provided. '
        sample:
          section:
            m_annotations:
              eln:
                overview: true
            quantities:
              name:
                type: str
                m_annotations:
                  eln:
                    component: StringEditQuantity
                description: |
                  Name of the sample.
```

The `section`, `sub_sections`, and `quantities` refer to the root level entitiy (behaves like a `group`), `group`, and `field` of the NeXus definition, respectively. The given schema ELN can be read as follows, `stm` ELN has direct fields `default`, `definition` and direct groups `Instrument`, `Sample`, with each group optionally containing nested `group`s and `field`s.

The example given below is to explain the **command line ELN**.
```yaml
Instrument:
  hardware:
    name: Nanonis
  lock_in:
    lock_in_data_flip_number: -1.0
    modulation_amplitude:
      unit: V
      value: 0.005
    modulation_frequency:
      unit: Hz
      value: 973.0
    status: 'OFF'
  piezo_config:
    active_calib: LHe
  sample_bias:
    bias:
      unit: V
      value: 0.005
    bias_calibration: 1.0
    bias_offset:
      unit: V
      value: '0'
  software:
    rt_release: '10771'
    ui_release: '10771'
    vendor: nanonis
    version: Generic 5e
  stm_head_temp:
    unit: K
    value: 5.04866
collection_identifier: TiSe2_2303a_annealing_300C_5min_evaporate_Pyrene_1_
default: backward
definition: NXsts
entry_identifier: TiSe2_2303a_annealing_300C_5min_evaporate_Pyrene_1_0070
experiment_description: A new TiSe2, annealed at 300 C for 5 min, then cool down to
  RT, evaporate the Pyrene on RT, 2.2 E -7, totally 10 s.
experiment_identifier: C:\Users\SPM-PEEM\Desktop\DATA_Nanonis\20220711_CreaTec_Service_Benchmarks_LHe\Nanonis-Session-PMD100-HVHU_CreaTec_Service_PalmaLabBerlin220711
experiment_type: stm
type: background
```
This type of ELN needs to be used if the reader is run from the command line. To know which fields and groups refer to which type of data, one needs to read the NeXus definition on the [FAIRmat NeXus Proposal](https://fairmat-nfdi.github.io/nexus_definitions/classes/contributed_definitions/NXsts.html#nxsts) page or in the [GitHub repository](https://github.com/FAIRmat-NFDI/nexus_definitions/blob/fairmat/contributed_definitions/NXsts.nxdl.xml). 
### Config File
The config file is used to map the raw data coming from the STS experiment file and the user input data (from the ELN) to the concepts defined in the NeXus definitions.

```json
{
    "/ENTRY[entry]/INSTRUMENT[instrument]/ENVIRONMENT[environment]/sweep_control/circuit/animations_period/@units": "/NanonisMain/Animations Period/unit",
    "/ENTRY[entry]/INSTRUMENT[instrument]/lock_in/demodulated_signal/@units": "/Lock-in/Demodulated signal/unit",
    "/ENTRY[entry]/INSTRUMENT[instrument]/lock_in/high_pass": "@eln",
    "/ENTRY[entry]/INSTRUMENT[instrument]/lock_in/low_pass": "@eln",
    "/ENTRY[entry]/INSTRUMENT[instrument]/lock_in/hardware": "@eln",
    "/ENTRY[entry]/INSTRUMENT[instrument]/piezo_config/2nd_order_corr_N": {"X":{"value":"/Piezo Configuration/2nd order corr X/value",
                                                                                "unit":"/Piezo Configuration/2nd order corr X/unit"},
                                                                           "Y":{"value":"/Piezo Configuration/2nd order corr Y/value",
                                                                                "unit":"/Piezo Configuration/2nd order corr Y/unit"}},
    "/ENTRY[entry]/INSTRUMENT[instrument]/piezo_config/active_calib": "/Piezo Configuration/Active Calib./value",
    "/ENTRY[entry]/INSTRUMENT[instrument]/piezo_config/calib_N": {"X":{"value":"/Piezo Configuration/Calib. X/value",
                                                                       "unit":"/Piezo Configuration/Calib. X/unit"},
                                                                  "Y":{"value":"/Piezo Configuration/Calib. Y/value",
                                                                       "unit":"/Piezo Configuration/Calib. Y/unit"},
                                                                  "Z":{"value":"/Piezo Configuration/Calib. Z/value",
                                                                       "unit":"/Piezo Configuration/Calib. Z/unit"}},
    "/ENTRY[entry]/INSTRUMENT[instrument]/piezo_config/curvature_radius_N": {"X":{"value":"/Piezo Configuration/Curvature radius X/value"},
                                                                              "Y":{"value":"/Piezo Configuration/Curvature radius Y/value"},
                                                                             "Z":{"value":"/Piezo Configuration/Curvature radius Z/value"}},
    "/ENTRY[entry]/INSTRUMENT[instrument]/piezo_config/curvature_radius_N/@units": {"X":{"value": "/Piezo Configuration/Curvature radius X/unit"},
                                                                                    "Y":{"value": "/Piezo Configuration/Curvature radius Y/unit"},
                                                                                    "Z":{"value": "/Piezo Configuration/Curvature radius Z/unit"}},
    "/ENTRY[entry]/INSTRUMENT[instrument]/piezo_config/drift_N": {"X":{"value":"/Piezo Configuration/Drift X/value",
                                                                       "unit":"/Piezo Configuration/Drift X/unit"},
                                                                  "Y":{"value":"/Piezo Configuration/Drift Y/value",
                                                                       "unit":"/Piezo Configuration/Drift Y/unit"},
                                                                  "Z":{"value":"/Piezo Configuration/Drift Z/value",
                                                                       "unit":"/Piezo Configuration/Drift Z/unit"}},
    "/ENTRY[entry]/INSTRUMENT[instrument]/piezo_config/drift_correction_status": "/Piezo Configuration/Drift correction status/value",
    "/ENTRY[entry]/INSTRUMENT[instrument]/piezo_config/drift_correction_status/@units": "/Piezo Configuration/Drift correction status/unit",
    "/ENTRY[entry]/INSTRUMENT[instrument]/piezo_config/hv_gain_N": {"X":{"value": "/Piezo Configuration/HV Gain X/value"},
                                                                    "Y":{"value": "/Piezo Configuration/HV Gain Y/value"},
                                                                    "Z":{"value": "/Piezo Configuration/HV Gain Z/value"}},
    "/ENTRY[entry]/INSTRUMENT[instrument]/piezo_config/tilt_N": {"X":{"value": "/Piezo Configuration/Tilt X/value"},
                                                                 "Y":{"value": "/Piezo Configuration/Tilt Y/value"},
                                                                 "Z":{"value": "/Piezo Configuration/Tilt Z/value"}},
    "/ENTRY[entry]/INSTRUMENT[instrument]/piezo_config/tilt_N/@units": {"X":{"value": "/Piezo Configuration/Tilt X/unit"},
                                                                        "Y":{"value": "/Piezo Configuration/Tilt Y/unit"},
                                                                        "Z":{"value": "/Piezo Configuration/Tilt Z/unit"}},
    "/ENTRY[entry]/INSTRUMENT[instrument]/sample_bias/bias": "/Bias/Bias/value",
    "/ENTRY[entry]/single_point": "None",
    "/ENTRY[entry]/type": "None",
    "/ENTRY[entry]/DATA[data]": {"0": ["/dat_mat_components/Bias calc/value",
                                 "/dat_mat_components/Bias calc/unit"],
                              "1": ["/dat_mat_components/Bias/value",
                                   "/dat_mat_components/Bias/unit",
                                   "/dat_mat_components/Current/value",
                                   "/dat_mat_components/Current/unit",
                                   "/dat_mat_components/Temperature 1/value",
                                   "/dat_mat_components/Temperature 1/unit",
                                   "/dat_mat_components/LI Demod 1 X/value",
                                   "/dat_mat_components/LI Demod 1 X/unit",
                                   "/dat_mat_components/LI Demod 1 Y/value",
                                   "/dat_mat_components/LI Demod 1 Y/unit",
                                   "/dat_mat_components/LI Demod 2 X/value",
                                   "/dat_mat_components/LI Demod 2 X/unit",
                                   "/dat_mat_components/LI Demod 2 Y/value",
                                   "/dat_mat_components/LI Demod 2 Y/unit"],
                              "2": ["/dat_mat_components/Bias [filt]/value",
                                   "/dat_mat_components/Bias [filt]/unit",
                                   "dat_mat_components/Bias [filt]/metadata",
                                   "/dat_mat_components/Current [filt]/value",
                                   "/dat_mat_components/Current [filt]/unit",
                                   "/dat_mat_components/Current [filt]/metadata",
                                   "/dat_mat_components/Temperature 1 [filt]/value",
                                   "/dat_mat_components/Temperature 1 [filt]/unit",
                                   "/dat_mat_components/Temperature 1 [filt]/metadata",
                                   "/dat_mat_components/LI Demod 1 X [filt]/value",
                                   "/dat_mat_components/LI Demod 1 X [filt]/unit",
                                   "/dat_mat_components/LI Demod 1 X [filt]/metadata",
                                   "/dat_mat_components/LI Demod 1 Y [filt]/value",
                                   "/dat_mat_components/LI Demod 1 Y [filt]/unit",
                                   "/dat_mat_components/LI Demod 1 Y [filt]/metadata",
                                   "/dat_mat_components/LI Demod 2 X [filt]/value",
                                   "/dat_mat_components/LI Demod 2 X [filt]/unit",
                                   "/dat_mat_components/LI Demod 2 X [filt]/metadata",
                                   "/dat_mat_components/LI Demod 2 Y [filt]/value",
                                   "/dat_mat_components/LI Demod 2 Y [filt]/unit",
                                   "/dat_mat_components/LI Demod 2 Y [filt]/metadata"]}
}
```
**NOTES**

- Each key is pointing to the NeXus concept (e.g. `/ENTRY[entry]/INSTRUMENT[instrument]/piezo_config/active_calib` key nevigates `ENTRY` -> `INSTRUMENT` -> `piezo_config` -> `active_calib` field in `NXsts` application definition.) in the NeXus application definition.  
- If the value is denoted by the token `@eln`, the data must come from the ELN (user provided), but this can be changed if the raw file contains that piece of data as well. 
- To update (if needed) the config file, a set of rules needs to be followed:
  - The dictionaries in the config files have the following meaning:
    ```
    "/ENTRY[entry]/INSTRUMENT[instrument]/lock_in/harmonic_order_N": {"D1": {"value": "/Lock-in/Harmonic D1/value"},
                                                                      "D2": {"value": "/Lock-in/Harmonic D2/value"}},
    ```
    Here, the part `N` in field `harmonic_order_N` can be considered as the name of dimensions and can be replaced by `D1` and `D2` to  write two fields of `harmonic_order` . This can be extended to further dimensions.
  - List for the same concept
    ```
    "/ENTRY[entry]/INSTRUMENT[instrument]/piezo_config/active_calib": ["/Piezo Configuration/Active Calib.",
                                                                       "/Piezo Calibration/Active Calib."],
    ```
    For different type of software versions the raw data path could be different for the same concept. For example, Nanonis software `generic 5e` has `/Piezo Configuration/Active Calib.` and generic 4.5 has `/Piezo Calibration/Active Calib.` for the same concept `/ENTRY[entry]/INSTRUMENT[instrument]/piezo_config/active_calib`.
  - In the config file, concepts that take data from the ELN are denoted by `@eln`. Otherwise, data will come from experimental raw files.
  - Importantly, the `NXdata` concept `/ENTRY[entry]/DATA[data]` takes a dict of lists. Each key (`0`, `1` ...) of the dict refers to an NXdata group with fields `bias` and `current` for multiple given setups, i.e, with and without `filter` check points. For another setup, one can extend the dict following the same convention used here.



## Useful Functions:
There are a few functions that you can utilize to make this reader compatible with your data:

- **get_stm_raw_file_info()**: For `STM` experiments, the function can return the slash separated dict in a text file. This dict helps to write or modify the config file according to the raw data file. 

  ```python
  from pynxtools_stm import get_stm_raw_file_info

  # for stm (.sxm) file
  get_stm_raw_file_info('STM_nanonis_generic_5e.sxm')
  ```

- **get_sts_raw_file_info**: For `STS` experiment to get the slash separated dict from the `STS` raw file one can use this function. It will write a txt file in the working directory.

  ```python
  from pynxtools_stm import get_sts_raw_file_info

  # for sts (.dat) file
  get_sts_raw_file_info('STS_nanonis_generic_5e_1.dat')
  ```

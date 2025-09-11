# Scanning Probe Microscopy (SPM)
!!! danger "Work in progress"
<!-- Scanning Probe Microscopy (SPM) is a high resolution imaging technique used to study material surface at nano scale. The technique can take on a wide range form of experiments catagorized by operating environment (e.g., ambient, valcuum), interaction range, and actuation mode, leading STM (Scanning Tunneling Microscopy), AFM (Atomic Force Microscopy), STS (Scanning Probe Spectroscopy), SPSTM (Spin Polarised STM), MFM (Magnetic Force Microscopy). Thses complex experiments require complex setup of instruments provided by different technology company which turns out diverse data model and data format. How can we compare the diversed data model and data format? Can we interprete the data in a common data model and format accessible to all SPM community? Does the proposed data model follow FAIR data principle?

Regarding a common data models or schema, we have developed community driven standard application definition, using NeXus[link_goes_here] data format, for SPM[link_goes_here] subdomains e.g., STM[link_goes here], STS[link_goes_here], AFM[link_goes_here] and a few base classes to describe instrument components (e.g. Lock-in[link-goes-here], Cantilever[link-goes-here]). Base on our data model, we build the reader that connects the data from experiment generated raw files to the standard application definition inscribed in a HDF5 file (as we are using NeXus data format in HDF5 file, we may also call it NeXus file with '.nxs' extension).


## SPM Readers
The prime purpose of the readers is to transform data from measurement files into community-defined concepts constructed by the SPM community which allows experimentalists to store, organize, search, analyze, and share experimental data (only within the [NOMAD](https://nomad-lab.eu/nomad-lab/) research data management (RDM) platform) among the scientific communities. The SPM readers is the bundle of readers from STM, STS and AFM. The readers follow a [common structure](link_to_common_code_structure) that allows to extend existing reader and include new readers for other members (e.g. SPSTM) of SPM family.

### Acquaintance with Reader Input Files
To utilize, reuse, or extend the reader, the different reader input files must be understood. The files are using specific semantic rules so that reader can understand the files and work with their contents.
The input files are:

1. Raw File(s) containing data from experiments; `.dat`, `.sxm`, for example.
2. ELN (Electronic Lab Notebook) to collect user input data. There are two ELN types to be used in NOMAD and standalon python environmenet such as jupyter-lab, we will discuss if later.
3. Config file that connects the raw data to concepts in corresponding NeXus application definition `NXsts` or `NXspm` for STS, `NXstm` for STM and so on.

### STS reader
The reader builds on the [NXsts](link from nexus-fairmat page) or [SPM](link from nexus-fairmat page) application definition and needs an experimental file, a config file (optional, we will discuss later) and a eln (eln stands for electronic lab notebook) file to transform the experiment generated data and user provided data into the [NXsts](link from nexus-fairmat page) or [NXspm](link from nexus-fairmat page) application concepts. 

Warning: The config file is a map between the data model from raw experimental file and data model inscribed in application definition, which infer different config files for different software version of the technology company provided setup. Less likely, config file may be different for different lab setups if experimentalist a allowed to modify the default raw data model in experimental file.

#### Supproted File Formats and Versions

- Current version of SPM reader can parse STS from
    - `.dat` file format from Nanonis: 
        - Versions: Generic 5e

### STM Reader
Like STS reader, STM reader has also the same interface and input files except a different application definition NXstm. 


#### Supproted File Formats and Versions
- Current version of SPM can parse STM from
    - `.sxm` file format from Nanonis: 
        - Versions: Generic 4.5

### AFM Reader
Like STS and STM readers, AFM follows the same principles for user interface with a application definition specification of NXafm

#### Supproted File Formats and Versions
  - Current version of SPM can parse AFM from
      - `.sxm` file format from Nanonis: 
          - Versions: Generic 4




### Raw File
This type of file (such as `example.dat` for `STS` or `example.sxm` for `STM` or `AFM`) is the data file generated during the experiments. 
### ELN (Electronic Lab Notebook)
This file supports user input data that is not part of the `raw file` by default. There are two ways to define or write ELN files. The first one can be distinguished, for sake of explanation, as **command line ELN**. This should be a YAML file (with `.yaml` extension ). Such type of ELN needs to be used to run the reader from the command line. The second one can be called, for sake of explanation, **NOMAD Schema ELN**. This is also a YAML file, but with the extension `.scheme.archive.yaml`. This ELN is needed if the reader is being used from NOMAD. Note that NOMAD will parse the NOMAD Schema ELN into a YAML file of the first type.
TODO: Add functionality in reader to get the entry default plot from child NXdata.
The example given below is to explain the **command line ELN**.
TODO: Keep a copy of this command line ELN under the STM reader section 
```yaml
experiment_technique: STM
hardware:
  vendor:
    value: 'Nanonis'
  model:
    value: 'Generic 4.5'
  model/@version:
    value: 'Generic 4.5'
software:
  vendor:
    value: 'Nanonis'
  model:
    value: 'Generic 4.5'
  model/@version:
    value: 'Generic 4.5'
INSTRUMENT[instrument]:
  lockin_amplifier:
    modulation_frequency: null
    modulation_signal: null
  current_sensor:
    current_calibration:
      calibration_time:
        value: null
        unit: null
      coefficients:
        value: null
        unit: null
    current_offset:
      value: null
      unit: null
  piezo_sensor:
    piezo_configuration:
      calibration:
        calibration_name: '4K'
        calibration_date: '2019-01-01'
        calibration_type: 'Active'
  scan_environment:
    cryo_bottom_temp:
      value: null
      unit: null
    cryo_shield_temp:
      value: null
      unit: null
    tip_temp:
      value: null
      unit: null
reproducibility_indicators:
  bias_sweep: null
resolution_indicators:
  bias_sweep: null
default: backward # To visualise the plot on entry level, the nxdata group name must be immediate child of entry
definition: NXstm 
experiment_description: A new TiSe2, annealed at 300 C for 5 min, then cool down to
  RT, evaporate the Pyrene on RT, 2.2 E -7, totally 10 s.
```

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
          reader: stm
          nxdl: NXstm
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
              - NXstm
          m_annotations:
            eln:
              component: EnumEditQuantity
          description: ''
        experiment_description:
          type:
            type: str
          m_annotations:
            eln:
              component: StringEditQuantity
          description: 'The description of the experiment like comments, ontes from from the experiment.'
      sub_sections:
        hardware:
          section:
            m_annotations:
              eln:
                overview: true
            quantities:
              vendor:
                type: str
                m_annotations:
                  eln:
                    component: StringEditQuantity
                description: |
                  Company name of the manufacturer (e.g. Nanonis, Bruker).
              model:
                type:
                  type_kind: Enum
                  type_data:
                    - Generic 4.5
                m_annotations:
                  eln:
                    component: EnumEditQuantity
                description: |
                    Version or model of the hardware setup provided by the manufacturer (e.g. Nanonis, Bruker).
                # TODO add option for model
              model/@version:
                type: str
                m_annotations:
                  eln:
                    component: StringEditQuantity
                description: |
                  If model has a distinquishable version (e.g. BP5e).
        software:
          section:
            m_annotations:
              eln:
                overview: true
            quantities:
              vendor:
                type: str
                m_annotations:
                  eln:
                    component: StringEditQuantity
                description: |
                  Company name of the manufacturer (e.g. Nanonis, Bruker).
              model:
                type:
                  type_kind: Enum
                  type_data:
                    - Generic 4.5
                m_annotations:
                  eln:
                    component: EnumEditQuantity
                description: |
                    Version or model of the hardware setup provided by the manufacturer (e.g. Nanonis, Bruker).
                # TODO add option for model
              model/@version:
                type: str
                m_annotations:
                  eln:
                    component: StringEditQuantity
                description: |
                  If model has a distinquishable version (e.g. BP5e).
        INSTRUMENT[instrument]:
          section:
            m_annotations:
              eln:
                overview: true
            sub_sections:
              lockin_amplifier:
                section:
                  m_annotations:
                    eln:
                      overview: true
                  quantities:
                    modulation_frequency:
                      type: np.float64
                      unit: Hz
                      m_annotations:
                        eln:
                          component: NumberEditQuantity
                    modulation_signal:
                      type_kind: enum
                      type_data: 
                        - Voltage
                        - Current
                      m_annotations:
                        eln:
                          component: EnumEditQuantity
              piezo_sensor:
                section:
                  m_annotations:
                    eln:
                      overview: true
                  sub_sections:
                    piezo_configuration:
                      section:
                        m_annotations:
                          eln:
                            overview: true
                        sub_sections:
                          calibration:
                            sections:
                              m_annotations:
                                eln: 
                                  overview: true
                              quantities:
                                calibration_name:
                                  type: str
                                  m_annotations:
                                    eln:
                                      component: StringEditQuantity
                                calibration_date:
                                  type: str
                                  m_annotations:
                                    eln:
                                      component: DateEditQuantity
                                calibration_type:
                                  type: str
                                  m_annotations:
                                    eln:
                                      component: StringEditQuantity
                                  description: |
                                     The type of calibration, e.g., active calibration, passive calibration, 
                                     or according to the laboratory defined type.
              scan_environment:
                section:
                  m_annotations:
                    eln:
                      overview: true
                  quantities:
                    cryo_bottom_temp:
                      type: np.float64
                      unit: K
                      m_annotations:
                        eln:
                          component: NumberEditQuantity
                    cryo_shield_temp:
                      type: np.float64
                      unit: K
                      m_annotatinos:
                        eln:
                          component: NumberEditQuantity
                    tip_temp:
                      type: np.float64
                      unit: K
                      m_annotations:
                        eln:
                          component: NumberEditQuantity
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


This type of ELN needs to be used if the reader is run from the command line. To know which fields and groups refer to which type of data, one needs to read the NeXus definition on the [FAIRmat NeXus Proposal](https://fairmat-nfdi.github.io/nexus_definitions/classes/contributed_definitions/NXsts.html#nxsts) page or in the [GitHub repository](https://github.com/FAIRmat-NFDI/nexus_definitions/blob/fairmat/contributed_definitions/NXsts.nxdl.xml). 
### Config File
The config file is used to map the raw data coming from the STS experiment file and the user input data (from the ELN) to the concepts defined in the NeXus definitions.

```json
{
    "ENTRY[entry]": {
        "@default": {
            "raw_path": "@default:current_backward"
        },
        "identifier_collection": "",
        "definition": "",
        "end_time": "",
        "entry_identifier": "",
        "identifier_experiment": {"identifier": ""},
        "experiment_description": {"raw_path": "/COMMENT"},
        "INSTRUMENT[instrument]": {
            "scan_environment": {
                "tip_temp": {
                    "raw_path": "/Temperature 1/Temperature 1",
                    "@units": "@default:K"
                },
                "SCAN_CONTROL[scan_control]": {
                    "scan_name": {  
                        "raw_path": "/Scan/series name"
                    },
                    "mesh_SCAN[mesh_scan]": {
                        "backward_speed_N[backward_speed_n]": {
                            "#note": "Derived in construct_scan_pattern_grp",
                            "raw_path": "/Scan/speed backw.",
                            "@units": "/Scan/speed backw./@unit"
                        },
                        "forward_speed_N[forward_speed_n]": {
                            "#note": "Derived in construct_scan_pattern_grp",
                            "raw_path": "/Scan/speed forw.",
                            "@units": "/Scan/speed forw./@unit"
                        },
                        "scan_speed_N[scan_speed_n]": "",
                        "channel_NAME_N[scan_name_n]": "",
                        "scan_points_N[scan_points_n]": {
                            "#note": "Derived in construct_scan_pattern_grp",
                            "raw_path": "/SCAN/PIXELS",
                            "@units": ""
                        },
                        "stepping_N[stepping_n]": {
                            "raw_path": "@default:1",
                            "@units": ""
                        },
                        "step_size_N[step_size_n]": {"raw_path": "", "@units": ""},
                        "scan_time": "",
                        "SCAN_DATA[scan_data]": ""
                    },
                    "scan_region": {
                        "scan_angle_N[scan_angle_n]": {
                            "raw_path": "/SCAN/ANGLE",
                            "@units": "@default:deg"
                        },
                        "scan_offset_N[scan_offset_n]": {
                            "#note": "Derived in function 'construct_scan_region_grp'.",
                            "raw_path": "/SCAN/OFFSET",
                            "@units": "/Z-Controller/Z/@unit"
                        },
                        "scan_range_N[scan_range_n]": {
                            "#note": "Derived in function 'construct_scan_region_grp'.",
                            "raw_path": "/SCAN/RANGE",
                            "@units": "/Z-Controller/Z/@unit"
                        }
                    },
                    "scan_time_start": "",
                    "scan_time_end": "",
                    "independent_scan_axes": {
                        "#note": "Handled in function _construct_nxscan_controllers",
                        "raw_path": "/SCAN/DIR",
                        "@units": ""
                    },
                    "scan_resolution_N": "",
                    "accuracy_N": "",
                    "scan_type": {"raw_path": "@default:mesh", "@units": ""},
                    "scan_control_type": {
                        "raw_path": "@default:continuous",
                        "@units": ""
                    }
                },
            },
            "lockin_amplifier": {
                "demodulated_signal": {
                    "raw_path": "/Lock-in/Demodulated signal",
                },
                "modulation_status": {"raw_path": "/Lock-in/Lock-in status"},
                "low_pass_N": [
                    {
                        "d1": {
                            "raw_path": "/Lock-in/LP Filter Cutoff D1",
                            "@units": "/Lock-in/LP Filter Cutoff D1/@unit"
                        }
                    },
                    {
                        "d2": {
                            "raw_path": "/Lock-in/LP Filter Cutoff D2",
                            "@units": "/Lock-in/LP Filter Cutoff D2/@unit"
                        }
                    }
                ],
            },
        },
        "DATA[data]": [
            {
                "data": {
                    "name": "z",
                    "raw_path": "/Z/forward",
                    "@units": "@default:m"
                },
  
                "title": {"raw_path": "@default:Height Plot of STM Experiment (Foward Direction)"},
                "grp_name": "z_forward"
            },
            {
                "data": {
                    "name": "z",
                    "raw_path": "/Z/backward",
                    "@units": "@default:m"
                },
                "title": {"raw_path": "@default:Height Plot of STM Experiment (Backward Direction)"},
                "grp_name": "z_backward"
            },
            {
                "data": {
                    "name": "current",
                    "raw_path": "/Current/forward",
                    "@units": "@default:A"
                },
                "title": {"raw_path": "@default:Current Plot of STM Experiment (Foward Direction)"},
                "grp_name": "current_forward"
            },
            {
                "data": {
                    "name": "current",
                    "raw_path": "/Current/backward",
                    "@units": "@default:A"
                },
                "title": {"raw_path": "@default:Current Plot of STM Experiment (Backward Direction)"},
                "grp_name": "current_backward"
            }
        ],
        "reproducibility_indicators": {
            "current": "",
        },
        "resolution_indicators": {
            "reference_frequency": ""
        }
    }
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
  from pynxtools_spm import get_stm_raw_file_info

  # for stm (.sxm) file
  get_stm_raw_file_info('STM_nanonis_generic_5e.sxm')
  ```

- **get_sts_raw_file_info**: For `STS` experiment to get the slash separated dict from the `STS` raw file one can use this function. It will write a txt file in the working directory.

  ```python
  from pynxtools_spm import get_sts_raw_file_info

  # for sts (.dat) file
  get_sts_raw_file_info('STS_nanonis_generic_5e_1.dat')
  ``` -->

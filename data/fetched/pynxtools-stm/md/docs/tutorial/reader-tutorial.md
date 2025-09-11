# Know More About Reader

!!! warning "Work in progress"

Complete documentation of this reader is still in progress.

## Want to Contribute or Extend the Reader Functionality
We appreciate any comments, extentions or improvements on the existing reader from users. Currently the reader supports the versions `4.5`, `5e` from `Generic` model of `Nanonis` vendor. To include the other versions of the `Generic` model, extend the class `StmNanonisGeneric` and `StsNanonisGeneric` by including versions in `__version__` attribute. Also include the model and version of the brand in `Spm` class. 
### How to Contribute or Extend the Reader Functionality
If you want to add the different versions of the `Nanonis Generic` model for `STM` experiment, please check the `STM_Nanonis` class for `STM` experiment, which parses the data into a python dict of slash (`/`) separated key-value pair (see the right part of the config file). The class uses the `nanonispy` sub-package to read the `sxm` type file. That should also be checked and modified (if needed).

If you add different versions of the `Nanonis Generic` model for `STS` experiment, please check the `BiasSpecData_Nanonis` class for `STS` experiment. The class reads the raw data from the raw files into a dict of slash separated key-value pair (see the config file). 

If you go for a completely different model (e.g., from a different brand), please handle it in a new module with different functions and classes. 

Later on, please add the relevant tests in the plugin test.

Done! Great, then please create a pull request.

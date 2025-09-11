# Install This Plugin

This plugin can be used in a NOMAD Oasis installation. Please visit the NOMAD documentation for details on how to setup an NOMAD Oasis.

## Add This Plugin to Your NOMAD Oasis installation

Read the [NOMAD plugin documentation](https://nomad-lab.eu/prod/v1/docs/howto/plugins/plugins.html) for all details on how to deploy the plugin on your NOMAD instance.

We recommend writing your own NOMAD docker image which includes the NOMAD plugins you want to deploy. Please follow [these instructions](https://nomad-lab.eu/prod/v1/docs/howto/oasis/install.html) to set up your own NOMAD image writing workflow.


To include the plugin your NOMAD Oasis modify your pyproject.toml file and add the CAMELS plugin dependancy:

```toml
dependencies = [
    ...
    "nomad-camels-plugin",
    ...
]
```
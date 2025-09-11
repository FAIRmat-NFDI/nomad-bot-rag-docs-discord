# What is NXellipsometry?

The [NXellipsometry](https://fairmat-nfdi.github.io/nexus_definitions/classes/contributed_definitions/NXellipsometry.html#nxellipsometry) NeXus application definition is a standard for converting ellipsometry data to make it FAIR.

# How to use it?

Navigate to the examples directory. Therein, execute the following command
which instructs the `ellips` reader to convert the example data using the `NXellipsometry` NeXus application definition resulting in a NeXus/HDF5 file:

```shell
dataconverter --reader ellips --nxdl NXellipsometry eln_data.yaml --output SiO2onSi.nxs
```

# Are there detailed examples?

Yes, [here](https://gitlab.mpcdf.mpg.de/nomad-lab/nomad-remote-tools-hub/-/tree/develop/docker/ellips) you can find an exhaustive example how to use `pynxtools` for your ellipsometry research data pipeline.

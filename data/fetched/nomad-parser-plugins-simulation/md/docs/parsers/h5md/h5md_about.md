# H5MD-NOMAD: A flexible data-storage schema for uploading molecular simulations to NOMAD

## Overview

Most computational data in NOMAD is harvested with code-specific parsers that recognize the output files from a particular software and retrieve the appropriate (meta)data accordingly.
However, this approach is not possible for many modern molecular simulation engines that use fully-flexible scriptable input and non-fixed output files.
["HDF5 for molecular data" (H5MD)](http://h5md.nongnu.org/) is a data schema for storage of molecular simulation data, based on the HDF5 file format.
This page describes an extension of the H5MD schema, denoted H5MD-NOMAD, which adds specificity to several of the H5MD guidelines while also retaining reasonable flexibility. This enables simulation data stored according to the H5MD-NOMAD schema to be stored in the NOMAD.

**Due to the nature of extending upon the original H5MD schema, portions of this doc page was duplicated, extended, or summarized from the [H5MD webpage](http://h5md.nongnu.org/).**
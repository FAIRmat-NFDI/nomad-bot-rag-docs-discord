# Data from Woollam instruments

The reader supports ellipsometry files exported from Woollam instruments in the .dat format.

The reader can be found [here](https://github.com/FAIRmat-NFDI/pynxtools-ellips/blob/main/src/pynxtools_ellips/reader.py).

## Example

An example dataset can be found [here](https://github.com/FAIRmat-NFDI/pynxtools-ellips/tree/main/examples).

The example conversion can be run with the following command:

```console
dataconverter --reader ellips --nxdl NXellipsometry eln_data.yaml --output SiO2onSi.nxs
```

## Acknowledgments

We thank Carola Emminger and Chris Sturm for providing the implementation and respective example data for this reader.

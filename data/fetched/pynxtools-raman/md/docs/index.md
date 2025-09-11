---
hide: toc
---

# Documentation for pynxtools-raman

pynxtools-raman is a free, and open-source data software for harmonizing Raman spectroscopy data and metadata for research data management using [NeXus](https://www.nexusformat.org/), implemented with the goal to make scientific research data FAIR (findable, accessible, interoperable and reusable).

pynxtools-raman, which is a plugin for [pynxtools](https://github.com/FAIRmat-NFDI/pynxtools), provides a tool for reading data from proprietary and open data formats from technology partners and the wider Raman community  (currently: `WITec` or `ROD`)  and standardizing it such that it is compliant with the NeXus application definitions [`NXoptical_spectroscopy`](https://fairmat-nfdi.github.io/nexus_definitions/classes/contributed_definitions/NXoptical_spectroscopy.html) and [`NXraman`](https://fairmat-nfdi.github.io/nexus_definitions/classes/contributed_definitions/NXraman.html), which is an extension of `NXoptical_spectroscopy`. pynxtools-raman is developed both as a standalone reader and as a tool within [NOMAD](https://nomad-lab.eu/), which is the open-source data management platform for materials science we are developing with [FAIRmat](https://www.fairmat-nfdi.eu/fairmat/).

pynxtools-raman solves the challenge of using heterogeneous and unfindable data formats which is common in the field of Raman spectroscopy.

pynxtools-raman is useful for scientists from the Raman spectroscopy community that deal with heterogeneous data, for technology partners and data providers looking for ways to make their data FAIRer, and for research groups that want to organize their data using NeXus and NOMAD.

A current use case can be found [here](https://spectra.adma.ai/search/) with an example NeXus file [here](https://spectra.adma.ai/search/?h5web=/RRUF/Anatase__R060277-3__Raman__514__0__ccw__Raman_Data_Processed__14960.nxs#/R060277%20Anatase_RRUF-4c1d6889-f9f1-5657-a80d-5738b50c4f9f/PROCESSED/R060277%20Anatase_1).

<div markdown="block" class="home-grid">

<div markdown="block"> 

### Tutorials

- [Config file and customized data conversion](tutorial/adjust_config_file.md)

</div>


<div markdown="block"> 

### How-to guides

- [Installation](how-tos/installation.md)
- [Convert data to NeXus files](how-tos/convert_data.md)
- [Download Raman Open Database files](how-tos/download_rod.md)

</div>

<div markdown="block"> 

### Learn

- You may want to take a look at general concepts of NeXus and how pynxtools works in the [documentation of pynxtools](https://fairmat-nfdi.github.io/pynxtools/)

</div>

<div markdown="block">


### References

Current examples of implementations are: 

- [WITEC Alpha](reference/witec.md)
- [Raman Open Database](reference/rod.md)

</div>
</div>

<h2>Project and community</h2>

Any questions or suggestions? [Get in touch!](https://www.fair-di.eu/fairmat/about-fairmat/team-fairmat)

---
hide: toc
---

# Documentation for pynxtools-ellips

`pynxtools-ellips` is a free and open-source data software for harmonizing ellipsometry data and metadata for research data management using [NeXus](https://www.nexusformat.org/), implemented with the goal to make scientific research data FAIR (findable, accessible, interoperable, and reusable).

`pynxtools-ellips`, which is a plugin for [pynxtools](https://github.com/FAIRmat-NFDI/pynxtools), provides a tool for reading data from (currently Woollam VASE) proprietary and open data formats from technology partners and the wider ellipsometry community. The tool standardizes these data such that it is compliant with the NeXus application definitions [`NXoptical_spectroscopy`](https://fairmat-nfdi.github.io/nexus_definitions/classes/applications/NXoptical_spectroscopy.html) and its extension [`NXellipsometry`](https://fairmat-nfdi.github.io/nexus_definitions/classes/applications/NXellipsometry.html). `pynxtools-ellips` is developed both as a standalone reader and as a tool within [NOMAD](https://nomad-lab.eu/), which is the open-source data management platform for materials science we are developing with [FAIRmat](https://www.fairmat-nfdi.eu/fairmat/).

`pynxtools-ellips` solves the challenge of using heterogeneous and unfindable data formats which is common in the field of ellipsometry.

`pynxtools-ellips` is useful for scientists from the ellipsometry community that deal with heterogeneous data, for technology partners and data providers looking for ways to make their data FAIRer, and for research groups that want to organize their data using NeXus and NOMAD.

<div markdown="block" class="home-grid">
<div markdown="block"> 

### Tutorial

- [Installation guide](tutorial/installation.md)

</div>
<div markdown="block">

### How-to guides

Coming soon!
<!-- How-to guides provide step-by-step instructions for a wide range of tasks, with the overarching topics: -->

</div>

<div markdown="block">

### Learn

Coming soon!
<!-- The explanation section provides background knowledge on the implementation design, how the data is structured, how data processing can be incorporated, how the integration works in NOMAD, and more.

- [`NXoptical_spectroscopy` and `NXellipsometry`](explanation/appdefs.md) -->

</div>
<div markdown="block">

### Reference

Here you can learn which specific measurement setups and file formats from technology partners `pynxtools-ellips` currently supports.

- [Woollam VASE](reference/vase.md)

</div>
</div>

<h2> Contact </h2>

For questions or suggestions:

- Open an issue on the [`pynxtools-ellips` GitHub](https://github.com/FAIRmat-NFDI/pynxtools-ellips/issues)
- Join our [Discord channel ](https://discord.gg/Gyzx3ukUw8)
- Get in contact with our [lead developers](contact.md).

<h2>Project and community</h2>

The work is funded by the Deutsche Forschungsgemeinschaft (DFG, German Research Foundation) - [460197019 (FAIRmat)](https://gepris.dfg.de/gepris/projekt/460197019?language=en).

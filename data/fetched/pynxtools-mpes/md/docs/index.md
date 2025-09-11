---
hide: toc
---

# Documentation for pynxtools-mpes

pynxtools-mpes is a free, and open-source data software for harmonizing multidimensional photoemission spectroscopy (MPES) data and metadata for research data management using [NeXus](https://www.nexusformat.org/).

pynxtools-mpes is a plugin for [pynxtools](https://github.com/FAIRmat-NFDI/pynxtools) for reading, translating, and standardizing MPES data from different sources such that it is compliant with the NeXus application definition [`NXmpes`](https://fairmat-nfdi.github.io/nexus_definitions/classes/contributed_definitions/NXmpes.html). In addition, it also supports the specialized application definition [`NXmpes_arpes`](https://fairmat-nfdi.github.io/nexus_definitions/classes/contributed_definitions/NXmpes_arpes.html) for angle-resolved photoemission spectroscopy (ARPES) experiments.

pynxtools-mpes is developed both as a standalone reader and as a tool within [NOMAD](https://nomad-lab.eu/), which is the open-source data management platform for materials science we are developing within [FAIRmat](https://www.fairmat-nfdi.eu/fairmat/).


<div markdown="block" class="home-grid">
<div markdown="block"> 

### Tutorial

A series of tutorials giving you an overview on how to store or convert your XPS data to NeXus compliant files.

- [Installation guide](tutorial/installation.md)
- [Standalone usage and examples](tutorial/standalone.md)

</div>
<div markdown="block">

### How-to guides

How-to guides provide step-by-step instructions for a wide range of tasks, with the overarching topics:

- [How to build a new MPES reader](how-tos/build-a-reader.md)

</div>

<div markdown="block">

### Learn

- coming soon!

</div>
<div markdown="block">

### Reference

Here you can learn which specific readers are currently implemented in `pynxtools-mpes`.

- [MPES reader](reference/mpes.md) for data from the [FHI Berlin](https://www.fhi.mpg.de/de) 

</div>
</div>

<h2>Project and community</h2>

- [NOMAD code guidelines](https://nomad-lab.eu/prod/v1/staging/docs/reference/code_guidelines.html) 

Any questions or suggestions? [Get in touch!](https://www.fair-di.eu/fairmat/about-fairmat/team-fairmat)

[The work is funded by the Deutsche Forschungsgemeinschaft (DFG, German Research Foundation) - 460197019 (FAIRmat).](https://gepris.dfg.de/gepris/projekt/460197019?language=en)

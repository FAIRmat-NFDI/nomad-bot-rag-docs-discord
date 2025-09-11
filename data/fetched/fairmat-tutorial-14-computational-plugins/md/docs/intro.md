# Part 1 - Introduction to the NOMAD software and repository

This section of the tutorial consists of a slide presentation: [Introduction Talk Slides](https://box.hu-berlin.de/f/285129802164464eb62f/){:target="_blank"}

For future use, we also include some important concepts below.

## Background

[NOMAD](https://nomad-lab.eu/nomad-lab/){:target="_blank"} is an open-source, community-driven data infrastructure, focusing on materials science data. Originally built as a repository for data from DFT calculations, the NOMAD software can automatically extract data from the output of a large variety of simulation codes. Our previous computation-focused tutorials ([CECAM workshop](https://fairmat-nfdi.github.io/AreaC-Tutorial-CECAM-2023/){:target="_blank"}, [Tutorial 10](https://fairmat-nfdi.github.io/AreaC-Tutorial10_2023/){:target="_blank"}, and [Tutorial 7](https://www.fairmat-nfdi.eu/events/fairmat-tutorial-7/tutorial-7-materials){:target="_blank"}) have highlighted the extension of NOMAD’s functionalities to support advanced many-body calculations, classical molecular dynamics simulations, and complex simulation workflows.

The key advantages of the NOMAD schema are summed up in **FAIR**mat's core values:

- **F**indable: a wide selection of the extracted data is indexed in a database, powering a the search with highly customizable queries and modular search parameters.
- **A**ccessible: the same database specifies clear API and GUI protocols on how retrieve the _full_ data extracted.
- **I**nteroperable: we have a diverse team of experts who interface with various materials science communities, looking into harmonizing data representations and insights among them. Following the NOMAD standard also opens up the (meta)data to the "NOMAD apps" ecosystem. <!-- Repeated in Parsers intro -->
- **R**eproducible: data is not standalone, but has a history, a vision, a workflow behind it. Our schema aims to capture the full context necessary for understanding and even regenerating via metadata.

## Modular Design and Plugins

Historically, the NOMAD parsers have always come packaged in a neat bundle.
As interest in research data management has become more widespread and recognized across scientific disciplines, NOMAD has adapted along with those interests.
Nowadays, in addition to the [central NOMAD service](https://nomad-lab.eu/prod/v1/gui/search/entries), there are many standalone NOMAD *Oasis* deployments geared towards the needs of individual institutes or research groups.

As such, NOMAD is shifting to a _plugin model_, where each deployment administrator can customize their setup.
This permits a light-weight base installation and effective data processing pipelines.
Conversely, it also lowers the threshold for whomever wants to contribute to this open-source community: you can focus on just a single schema or parser.
The possibilities are as wide as you can make them, we just facilitate the common basis.

The remainder of the tutorial will provide you with the basic knowledge for starting to develop your own computational parsers and schemas.
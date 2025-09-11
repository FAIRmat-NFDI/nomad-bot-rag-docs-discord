# fairmat-tutorial-14-computational-plugins

### Full Title:

FAIRmat Tutorial 14: Developing schemas and parsers for FAIR computational data storage using NOMAD-Simulations

### Description:

NOMAD is an open-source, community-driven data infrastructure, focusing on materials science data. Originally built as a repository for data from DFT calculations, the NOMAD software can automatically extract data from the output of a large variety of simulation codes. Our previous computation-focused tutorials (CECAM workshop, Tutorial 10, and Tutorial 7) have highlighted the extension of NOMAD’s functionalities to support advanced many-body calculations, classical molecular dynamics simulations, and complex simulation workflows.

But how can you utilize this infrastructure and associated suite of tools if your simulation code or method is not yet supported? This tutorial will provide foundational knowledge for customizing NOMAD to fit the specific needs of your computational research project. The following provides an outline of the major topics that will be covered:

- Introduction to the NOMAD software and repository
- Working with the NOMAD-Simulations schema plugin
- Extending NOMAD-Simulations to support custom methods and outputs
- Creating parser plugins from scratch
- Extra: Interfacing complex simulation and analysis workflows with NOMAD

### How to launch locally for debugging

In the workflow-documentation directory, create your own virtual environment with Python3.9:
```
python3 -m venv .pyenvtuto
```
and activate it in your shell:
```
. .pyenvtuto/bin/activate
```
Always ensure that the environment is active.
Else run the command above again.

Regarding the dependencies, there are 2 specification packages.
To run the `mkdocs` server locally, `requirements.txt` suffices.
If you also want to deploy the notebooks enclosed in `jupyter lab` from your local environment, use `requirements.full.txt`.
In case of doubt, you can start with the leaner `requirements.txt`.
This leaves open the option to extend to the more comprehensive `requirements.full.txt` later on.

Once you have decided your dependencies, installing them is as easy as:
```
pip install -r <requirements>
```

Launch locally:
```
mkdocs serve
```

The output on the terminal should have these lines:
```
...
INFO     -  Building documentation...
INFO     -  Cleaning site directory
INFO     -  Documentation built in 0.29 seconds
INFO     -  [14:31:29] Watching paths for changes: 'docs', 'mkdocs.yml'
INFO     -  [14:31:29] Serving on http://127.0.0.1:8000/
...
```
Then click on the http address to launch the MKDocs.

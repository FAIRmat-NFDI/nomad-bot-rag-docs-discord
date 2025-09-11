# Developing schemas and parsers for FAIR computational data storage using NOMAD-Simulations

This tutorial will provide foundational knowledge for customizing NOMAD to fit the specific needs of your computational research project.

## Tutorial information and preparation

The FAIRmat Tutorial 14, presented by FAIRmat Area C Computation, took place on Wednesday, July 10, 2024.

A [recording of the tutorial](https://www.youtube.com/watch?v=Al_wY2eqn6g&list=PLrRaxjvn6FDXiHpOKpRN_Phv14Qdqg7lp&pp=iAQB){:target="_blank"} is available on the FAIRmat and NOMAD YouTube channel

The focus of this tutorial is the `nomad-simulations` schema package, which can be installed as follows:

First, create the directory and the virtual environment in the terminal. Note that the Python version must be 3.9-3.11 for `nomad-simulations` to work:

```sh
mkdir test_nomadsimulations
cd test_nomadsimulations/
python3.11 -m venv .pyenv
source .pyenv/bin/activate
```

Once this is done, we can pip install the `nomad-simulations` package:

```sh
pip install --upgrade pip
pip install nomad-simulations --index-url https://gitlab.mpcdf.mpg.de/api/v4/projects/2187/packages/pypi/simple
```

We hope that this tutorial helps you to leverage NOMAD to enhance your own research! If you have any questions or would like to suggest future development directions, please come talk to us on the [NOMAD Discord Server under](https://discord.gg/Gyzx3ukUw8){:target="_blank"} the "Computation" section.





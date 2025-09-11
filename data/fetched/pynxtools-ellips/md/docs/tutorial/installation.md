# Installation guide

To get started, it does not hurt to read the following explanations:

- [Guide on getting started with pynxtools](https://fairmat-nfdi.github.io/pynxtools/getting-started.html)
- [Installation tutorial for pynxtools](https://fairmat-nfdi.github.io/pynxtools/tutorial/installation.html)

## What you will know at the end of this tutorial?

You will know

- how to install `pynxtools-ellips`

## Setup

It is recommended to use python 3.12 with a dedicated virtual environment for this package.
Learn how to manage [python versions](https://github.com/pyenv/pyenv) and
[virtual environments](https://realpython.com/python-virtual-environments-a-primer/).

=== "uv"
    `uv` is capable of creating a virtual environment and install the required Python version at the same time.

    ```bash
    uv venv --python 3.12
    ```

=== "venv"

    Note that you will need to install the Python version manually beforehand.

    ```bash
    python -m venv .venv
    ```
That command creates a new virtual environment in a directory called `.venv`.

There are many alternatives to managing virtual environments and package dependencies (requirements). We recommend using [`uv`](https://github.com/astral-sh/uv), an extremely fast Python package and project manager. In this tutorial, you will find paralleled descriptions, using either `uv` or a more classical approach using `venv` and `pip`.



## Installation

Install the latest stable version of this package from PyPI with

=== "uv"

    ```bash
    uv pip install pynxtools-ellips
    ```

=== "pip"

    ```bash
    pip install pynxtools-ellips
    ```

Since this package is a reader plugin for [`pynxtools`](https://github.com/FAIRmat-NFDI/pynxtools), it can also be installed together with `pynxtools` as an [extra](https://packaging.python.org/en/latest/specifications/dependency-specifiers/#extras):

=== "uv"

    ```bash
    uv pip install pynxtools[ellips]
    ```

=== "pip"

    ```bash
    pip install pynxtools[ellips]
    ```

You can also install the latest _development_ version of `pynxtools-ellips` with

=== "uv"

    ```bash
    uv pip install git+https://github.com/FAIRmat-NFDI/pynxtools-ellips.git
    ```

=== "pip"

    ```bash
    pip install git+https://github.com/FAIRmat-NFDI/pynxtools-ellips.git
    ```

### How to install `pynxtools-ellips` with NOMAD

To use `pynxtools-ellips` with NOMAD, simply install it in the same environment as the `nomad-lab` package. NOMAD will recognize `pynxtools` and `pynxtools-ellips` as plugins automatically.

## Start using `pynxtools-ellips`

That's it! You can now use `pynxtools-ellips`!

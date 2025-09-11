# nomad-porous-materials

NOMAD plugin for porous materials

----

This `nomad`_ plugin was generated with `Cookiecutter`_ along with `@nomad`_'s `cookiecutter-nomad-plugin`_ template.


### Install

You should create a virtual environment. You will need the `nomad-lab` package (and `pytest`).
We recommend using Python 3.9.

```sh
python3 -m venv .pyenv
source .pyenv/bin/activate
pip install --upgrade pip
pip install -e '.[dev]' --index-url https://gitlab.mpcdf.mpg.de/api/v4/projects/2187/packages/pypi/simple
```

**Note!**
Until we have an official pypi NOMAD release with the plugins functionality. Make
sure to include NOMAD's internal package registry (e.g. via `--index-url`).

### Testing

You can run automated tests with `pytest`:

```sh
pytest -svx tests
```

### Run linting

```sh
ruff check .
```

### Run auto-formatting

This is entirely optional. To add this as a check in github actions pipeline, uncomment the `ruff-formatting` step in `./github/workflows/actions.yaml`.

```sh
ruff format .
```

### Developing a NOMAD plugin

Follow the [guide](#TODO: insert new URL here) on how to develop NOMAD plugins.

### Build the python package

The `pyproject.toml` file contains everything that is necessary to turn the project
into a pip installable python package. Run the python build tool to create a package distribution:

```
pip install build
python -m build --sdist
```

You can install the package with pip:

```
pip install dist/nomad-porous-materials-0.1.0
```

Read more about python packages, `pyproject.toml`, and how to upload packages to PyPI
on the [PyPI documentation](https://packaging.python.org/en/latest/tutorials/packaging-projects/).


### License
Distributed under the terms of the `Apache Software License 2.0`_ license, "nomad-porous-materials" is free and open source software

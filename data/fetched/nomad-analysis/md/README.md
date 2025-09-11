![](https://github.com/nomad-coe/nomad-schema-plugin-example/actions/workflows/actions.yml/badge.svg)
![](https://coveralls.io/repos/github/FAIRmat-NFDI/nomad-analysis/badge.svg?branch=main)
[![NOMAD](https://img.shields.io/badge/Open%20NOMAD-lightgray?logo=data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0idXRmLTgiPz4KPCEtLSBHZW5lcmF0b3I6IEFkb2JlIElsbHVzdHJhdG9yIDI3LjUuMCwgU1ZHIEV4cG9ydCBQbHVnLUluIC4gU1ZHIFZlcnNpb246IDYuMDAgQnVpbGQgMCkgIC0tPgo8c3ZnIHZlcnNpb249IjEuMSIgaWQ9IkxheWVyXzEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiIHg9IjBweCIgeT0iMHB4IgoJIHZpZXdCb3g9IjAgMCAxNTAwIDE1MDAiIHN0eWxlPSJlbmFibGUtYmFja2dyb3VuZDpuZXcgMCAwIDE1MDAgMTUwMDsiIHhtbDpzcGFjZT0icHJlc2VydmUiPgo8c3R5bGUgdHlwZT0idGV4dC9jc3MiPgoJLnN0MHtmaWxsOiMxOTJFODY7c3Ryb2tlOiMxOTJFODY7c3Ryb2tlLXdpZHRoOjE0MS4zMjI3O3N0cm9rZS1taXRlcmxpbWl0OjEwO30KCS5zdDF7ZmlsbDojMkE0Q0RGO3N0cm9rZTojMkE0Q0RGO3N0cm9rZS13aWR0aDoxNDEuMzIyNztzdHJva2UtbWl0ZXJsaW1pdDoxMDt9Cjwvc3R5bGU+CjxwYXRoIGNsYXNzPSJzdDAiIGQ9Ik0xMTM2LjQsNjM2LjVjMTUwLjgsMCwyNzMuMS0xMjEuOSwyNzMuMS0yNzIuMlMxMjg3LjIsOTIuMSwxMTM2LjQsOTIuMWMtMTUwLjgsMC0yNzMuMSwxMjEuOS0yNzMuMSwyNzIuMgoJUzk4NS42LDYzNi41LDExMzYuNCw2MzYuNXoiLz4KPHBhdGggY2xhc3M9InN0MSIgZD0iTTEzMjksOTQ2Yy0xMDYuNC0xMDYtMjc4LjgtMTA2LTM4Ni4xLDBjLTk5LjYsOTkuMy0yNTguNywxMDYtMzY1LjEsMTguMWMtNi43LTcuNi0xMy40LTE2LjItMjEuMS0yMy45CgljLTEwNi40LTEwNi0xMDYuNC0yNzgsMC0zODQuOWMxMDYuNC0xMDYsMTA2LjQtMjc4LDAtMzg0LjlzLTI3OC44LTEwNi0zODYuMSwwYy0xMDcuMywxMDYtMTA2LjQsMjc4LDAsMzg0LjkKCWMxMDYuNCwxMDYsMTA2LjQsMjc4LDAsMzg0LjljLTYzLjIsNjMtODkuMSwxNTAtNzYuNywyMzIuMWM3LjcsNTcuMywzMy41LDExMy43LDc3LjYsMTU3LjZjMTA2LjQsMTA2LDI3OC44LDEwNiwzODYuMSwwCgljMTA2LjQtMTA2LDI3OC44LTEwNiwzODYuMSwwYzEwNi40LDEwNiwyNzguOCwxMDYsMzg2LjEsMEMxNDM1LjQsMTIyNCwxNDM1LjQsMTA1MiwxMzI5LDk0NnoiLz4KPC9zdmc+Cg==)](https://nomad-lab.eu/prod/v1/staging/gui/)  ![](https://coveralls.io/repos/github/FAIRmat-NFDI/nomad-analysis/badge.svg?branch=main)

# NOMAD's Analysis plugin
This is a plugin for [NOMAD](https://nomad-lab.eu) to facilitate analysis of processed
entry archives. The plugin provides schemas to create entries for analysis that can 
interact with other entries, using them as analysis inputs. Jupyter Analysis schemas
generate analysis entries that are connected with an external programming interface,
JupyterHub, which allows users to run custom code on the connected input entries.

To install the package as a dependency for your NOMAD Oasis, add it to your
`pyproject.toml` as under `project.dependencies` table:
```toml
[project]
dependencies = [
    ...
    "nomad-analysis",
]
```

Or you can use `pip` to install the package in your Python environment:
```sh
pip install nomad-analysis
```


## Development

The plugin is still under development. If you would like to contribute, follow these
steps:

### Install the dependencies

Clone the project and go into the cloned directory. Create and start a virtual
environment (note this project uses Python 3.11):
```sh
git clone https://github.com/FAIRmat-NFDI/nomad-analysis.git
cd nomad-analysis
python3.11 -m venv .pyenv
source .pyenv/bin/activate
```

Install the `nomad-analysis` package in editable mode (with `-e` flag) along
with development dependencies (with '`.[dev]`'):
```sh
pip install --upgrade pip
uv pip install -e '.[dev]'
```

> **Note**: `uv` uses NOMAD's internal package registry via `index-url` defined under
`tool.uv.index-url` in `pyproject.toml`. If you want to use `pip` directly
without `uv` wrapper, use the following:
```sh
pip install -e '.[dev]' --index-url https://gitlab.mpcdf.mpg.de/api/v4/projects/2187/packages/pypi/simple
```

### Run the tests

You can run the unit testing using the `pytest` package:

```sh
python -m pytest -sv
```

We recommend to install the `coverage` and `coveralls` packages for a more comprehensive
output of the testing:
```sh
pip install coverage coveralls
python -m coverage run -m pytest -sv
```



### Set up the plugin on your local installation
Read the [NOMAD plugin documentation](https://nomad-lab.eu/prod/v1/staging/docs/howto/plugins/plugins.html#controlling-loading-of-plugin-entry-points) for all details on how to deploy the
plugin on your local NOMAD installation. In summary:

1. Install the plugin repo in your local installation environment
    ```sh
    pip install -e <path to the plugin repo>
    ```

2. From the following available entry points, include the ones you want (or all) in the
nomad.yaml of your local installation:

    ```yaml
    plugins:
      include:
        - nomad_analysis.general:schema
        - nomad_analysis.jupyter:schema
    ```

### Run linting and auto-formatting
Ruff auto-formatting is also a part of the GitHub workflow actions. Make sure that
before you make a Pull Request to add your contributions to this repo, the following
commands run in your local without any errors otherwise the workflow action will fail.
```sh
ruff check .
```
```sh
ruff format . --check
```

Alternatively, if you are using VSCode as your IDE, we added the settings configuration
file, `.vscode/settings.json`, such that it performs `ruff format` whenever you save
progress in a file.

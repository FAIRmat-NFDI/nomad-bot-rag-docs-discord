# nomad-crystallm

`nomad-crystallm` is a NOMAD plugin that can be used to run inference of
[CrystaLLM](https://crystallm.com/) models and create entries based on the generated CIFs.



## Development

If you want to develop locally this plugin, clone the project and in the plugin folder, create a virtual environment (you can use Python 3.10, 3.11 or 3.12):
```sh
git clone https://github.com/FAIRmat-NFDI/nomad-crystallm.git
cd nomad-crystallm
python3.11 -m venv .pyenv
. .pyenv/bin/activate
```

Make sure to have `pip` upgraded:
```sh
pip install --upgrade pip
```

We recommend installing `uv` for fast pip installation of the packages:
```sh
pip install uv
```

Install the `nomad-lab` package:
```sh
uv pip install -e '.[gpu-workflow, dev]'
```
### Developing on `nomad-distro-dev`
We now recommend using the dedicated
[`nomad-distro-dev`](https://github.com/FAIRmat-NFDI/nomad-distro-dev)
repository to simplify the process. Please refer to that repository for
detailed instructions on how to add this plugin to your development environment.

When adding this plugin to `nomad-distro-dev`, make sure to add it
with the `gpu-workflow` dependencies. For this, add the following
to the `pyproject.toml`:
```toml
dependencies = [
  ...
  "nomad-crystallm[gpu-workflow]",
]
```

This plugin relies on some new developments in the `nomad-lab` package that are
currently available in a feature branch. To use it in your `nomad-distro-dev`,
you have to change the branch of the `nomad-lab` sub-module available at
`packages/nomad-FAIR` to the feature branch:
```sh
# assuming you are in the root of your nomad-distro-dev repo
cd packages/nomad-FAIR
git checkout temporal-workflows
cd -
```

Further, you need to modify `nomad.yaml` config file to contain the following
table:
```yaml
temporal:
  enabled: true
```

We use [temporal](https://temporal.io/) as a workflow scheduler to run the
inference pipeline. For this, you will need temporal container configurations
in `docker-compose.yaml`, which should be available once you update your
`nomad-distro-dev` fork. Specifically, here are the required changes: https://github.com/FAIRmat-NFDI/nomad-distro-dev/commit/16e6129c43d9e6d56f2ff5a92c041c88a6a2eac2.

With these changes in place, make sure to run `uv run poe setup` to reset
the environment.

Finally, you can run your local installation with `uv run poe start` and
`uv run poe gui start` in separate terminals. Additionally, start a temporal
worker in a third terminal using `uv run nomad admin run orchestrator-gpu-worker`.

### Run the tests

You can run locally the tests:
```sh
python -m pytest -sv tests
```

where the `-s` and `-v` options toggle the output verbosity.

Our CI/CD pipeline produces a more comprehensive test report using the `pytest-cov` package. You can generate a local coverage report:
```sh
uv pip install pytest-cov
python -m pytest --cov=src tests
```

### Run linting and auto-formatting

We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting the code. Ruff auto-formatting is also a part of the GitHub workflow actions. You can run locally:
```sh
ruff check .
ruff format . --check
```

### Debugging

For interactive debugging of the tests, use `pytest` with the `--pdb` flag. We recommend using an IDE for debugging, e.g., _VSCode_. If that is the case, add the following snippet to your `.vscode/launch.json`:
```json
{
  "configurations": [
      {
        "name": "<descriptive tag>",
        "type": "debugpy",
        "request": "launch",
        "cwd": "${workspaceFolder}",
        "program": "${workspaceFolder}/.pyenv/bin/pytest",
        "justMyCode": true,
        "env": {
            "_PYTEST_RAISE": "1"
        },
        "args": [
            "-sv",
            "--pdb",
            "<path-to-plugin-tests>",
        ]
    }
  ]
}
```

where `<path-to-plugin-tests>` must be changed to the local path to the test module to be debugged.

The settings configuration file `.vscode/settings.json` automatically applies the linting and formatting upon saving the modified file.

### Documentation on Github pages

To view the documentation locally, install the related packages using:
```sh
uv pip install -r requirements_docs.txt
```

Run the documentation server:
```sh
mkdocs serve
```

## Adding this plugin to NOMAD

Currently, NOMAD has two distinct flavors that are relevant depending on your role as an user:
1. [A NOMAD Oasis](#adding-this-plugin-in-your-nomad-oasis): any user with a NOMAD Oasis instance.
2. [Local NOMAD installation and the source code of NOMAD](#adding-this-plugin-in-your-local-nomad-installation-and-the-source-code-of-nomad): internal developers.

### Adding this plugin in your NOMAD Oasis

Read the [NOMAD plugin documentation](https://nomad-lab.eu/prod/v1/staging/docs/howto/oasis/plugins_install.html) for all details on how to deploy the plugin on your NOMAD instance.

### Adding this plugin in your local NOMAD installation and the source code of NOMAD

We now recommend using the dedicated [`nomad-distro-dev`](https://github.com/FAIRmat-NFDI/nomad-distro-dev) repository to simplify the process. Please refer to that repository for detailed instructions.

### Template update

We use [`cruft`](https://github.com/cruft/cruft) to update the project based on template changes. To run the check for updates locally, run `cruft update` in the root of the project. More details see the instructions on [`cruft` website](https://cruft.github.io/cruft/#updating-a-project).

## Main contributors
| Name | E-mail     |
|------|------------|
| Ahmed Ilyas | [ahmed.ilyas@physik.hu-berlin.de](mailto:ahmed.ilyas@physik.hu-berlin.de)
| Sarthak Kapoor | [sarthak.kapoor@physik.hu-berlin.de](mailto:sarthak.kapoor@physik.hu-berlin.de)

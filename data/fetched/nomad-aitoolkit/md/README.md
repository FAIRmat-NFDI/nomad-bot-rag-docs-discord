# nomad-aitoolkit

Schema and app for AI Toolkit notebooks.



### Developing a NOMAD plugin

Follow the [guide](https://nomad-lab.eu/prod/v1/staging/docs/howto/plugins/plugins.html) on how to develop NOMAD plugins.

### Build the python package

The `pyproject.toml` file contains everything that is necessary to turn the project
into a pip installable python package. Run the python build tool to create a package distribution:

```
pip install build
python -m build --sdist
```

You can install the package with pip:

```
pip install dist/nomad-aitoolkit-0.1.0
```

Read more about python packages, `pyproject.toml`, and how to upload packages to PyPI
on the [PyPI documentation](https://packaging.python.org/en/latest/tutorials/packaging-projects/).

### Documentation on Github pages

To deploy documentation on Github pages, make sure to [enable GitHub pages via the repo settings](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site#publishing-from-a-branch).

To view the documentation locally, install the documentation related packages using:

```sh
pip install -e '.[docs]'
```

Run the documentation server:
```sh
mkdocs serve
```

### License
Distributed under the terms of the `Apache Software License 2.0`_ license, "nomad-aitoolkit" is free and open source software

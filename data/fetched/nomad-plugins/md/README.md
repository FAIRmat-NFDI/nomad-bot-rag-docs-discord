![](https://github.com/FAIRmat-NFDI/nomad-plugins/actions/workflows/python-publish.yml/badge.svg)
![](https://img.shields.io/pypi/pyversions/nomad-plugins)
![](https://img.shields.io/pypi/l/nomad-plugins)
![](https://img.shields.io/pypi/v/nomad-plugins)

# NOMAD Plugins

A plugin for discovering other plugins.

## Using this plugin

If you want to view the compiled list of NOMAD plugins indexed by this plugin you can
find these on
[nomad-lab.eu/prod/v1/oasis/gui/search/plugins](https://nomad-lab.eu/prod/v1/oasis/gui/search/plugins).

### Installing the plugin

If you want to add this plugin to your own oasis you need to add it to the plugins list
in the `pyproject.toml` of your
[NOMAD Oasis distribution repository](https://github.com/FAIRmat-NFDI/nomad-distro-template):

```toml
[project.optional-dependencies]
plugins = [
  "nomad-plugins"
]
```

### Running the crawler

To run the crawler you need to install the plugin with e.g. pip:

```
pip install nomad-plugins
```

and run the `plugin-crawler` script:

```
Usage: plugin-crawler [OPTIONS]

  Crawl GitHub repositories for NOMAD plugins and upload them to the NOMAD
  server.

  The nomad-url can be provided as an argument or in the nomad.yaml config
  file as:

  client:

      url: <nomad-url>

  The upload-id can be provided as an argument or in the nomad.yaml config
  file as:

  plugins:

      entry_points:

          options:

              nomad_plugins.apps:plugin_app_entry_point:
              upload_id: <upload-id>

Options:
  --github-token TEXT    Your GitHub personal access token to use when
                         querying for plugins.
  --nomad-username TEXT  NOMAD username for the owner of the plugins upload.
  --nomad-password TEXT  NOMAD password for the owner of the plugins upload.
  --nomad-url TEXT       The NOMAD API URL, defaults to client.url in
                         nomad.yaml.
  --upload-id TEXT       Optional upload ID for updating an existing upload.
  --help                 Show this message and exit.
```


## Main contributors
| Name | E-mail     |
|------|------------|
| Hampus Näsström | [hampus.naesstroem@physik.hu-berlin.de](mailto:hampus.naesstroem@physik.hu-berlin.de)

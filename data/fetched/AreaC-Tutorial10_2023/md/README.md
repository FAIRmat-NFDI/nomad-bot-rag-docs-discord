# Area C - Tutorial 10 on 14.06.2023

### How to launch locally for debugging

In the workflow-documentation directory, create your own virtual environment with Python3.9:
```
python3 -m venv .pyenvtuto
```
and activate it in your shell:
```
. .pyenvdoc/bin/activate
```

Make sure you have the latest pip version:
```
pip install --upgrade pip
```

Pip-install the right dependencies:
```
pip install mkdocs
pip install mkdocs-material
pip install mkdocs-bibtex
pip install https://github.com/mitya57/python-markdown-math/archive/master.zip
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
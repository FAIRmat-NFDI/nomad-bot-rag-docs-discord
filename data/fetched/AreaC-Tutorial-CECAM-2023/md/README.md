# Area C - Tutorial for CECAM flagship workshop "Fair and True Data Processing for Soft Matter Simulations"

### How to launch locally for debugging

In the workflow-documentation directory, create your own virtual environment with Python3.9:
```
python3 -m venv .pyenvtuto
```
and activate it in your shell:
```
. .pyenvdoc/bin/activate
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

# Working with the NOMAD archive (~40 min)

In this part of the tutorial we will demonstrate how to query data from the NOMAD repository and work with it within a python environment.

For this demonstration, we will utilize some tools from the nomad-lab software, as well as some third-party software (e.g., MDAnalysis, nglview).

We suggest creating a virtual environment for this purpose. For example, using `conda`, you can set up the appropriate environment by first downloading the environment.yml file:

<center>
[Download environment.yml](assets/md_tutorial_3/environment.yml){ .md-button }
</center>

Then create a new conda environment with the following command:

```python
conda env create -f environment.yml
```

??? tip
    In case you have problems, here are the original commands used to set up the environment:

    ```python
    conda create -n "CECAM_tutorial" python==3.9
    conda activate CECAM_tutorial
    pip install nomad-lab
    conda install nglview
    conda install "ipywidgets <8" -c conda-forge
    ```

Or if you are using `virtualenv`:

<center>
[Download requirements.txt](assets/md_tutorial_3/requirements.txt){ .md-button }
</center>

```python
python3 -m venv .pyenv
source .pyenv/bin/activate
pip install -r requirements.txt
```

!!! warning "warning"

    You may have to restart your code editor (IDE) to get the in-notebook visualizations to work.

???+ info "info"
    We stress that none of these packages are **required** to work with the NOMAD archive data. As you will see below, the archive data will be retrieved in a dictionary format, which you are free to work with in a *plain* python environment.

Now, start a Jupyter notebook to carry out the remainder of this part of the tutorial.

Import all the necessary modules:

```python
# Python
import numpy as np

# timing
import time as t

# I/O
import json

# NOMAD API
import requests

# NOMAD tools
from nomad.atomutils import archive_to_universe
from nomad.atomutils import BeadGroup
from nomad.datamodel import EntryArchive
from nomad.units import ureg

# Visualization
import matplotlib.pyplot as plt
import nglview as nv

# MDAnalysis
import MDAnalysis.analysis.rdf as MDA_RDF
from MDAnalysis.analysis.distances import self_distance_array, distance_array
```

## Downloading entire entry archives

In general, you can use the [NOMAD Application Programming Interface (API)](https://nomad-lab.eu/prod/rae/docs/api.html) to

- upload data (especially useful when you are producing data via a workflow)
- delete data
- query all kinds of (meta)data: processed (from the archive), raw (from the repository), large bundles, individual entries, etc

Each functionality has its own url, i.e. _endpoints_. There are over 60 different endpoints, each specialized in their own little subtask. You can find the full overview over at the [API dashboard](https://nomad-lab.eu/prod/v1/staging/api/v1/extensions/docs#/){:target="_blank"}. It is highly recommended to have this page open when writing queries. Lastly, you can also use the dashboard to try out queries on the fly.

In this first exercise, we will download the **processed molecular dynamics trajectory** of an **individual entry** to perform our own visualization and analysis.
For this, we will be using the `/entries/{entry_id}`/archive. The `{entry_id}` here is variable, which you can get from the NOMAD website (or other API queries). Note that there are 3 versions of this endpoint: one that only gives you the metadata, one that returns the entire archive (`/download`), and a last wildcard that we will get into later (`/query`). These latter 2 options will be demonstrated below.

Let's imagine that we searched the NOMAD repository using the filter bar of the GUI, as demonstrated in [Part I](part1.md) of the tutorial, and found a [short simulation of an atomistic box of hexane molecules](https://nomad-lab.eu/prod/v1/gui/search/entries/entry/id/hxaepf6x12Xt2IX2jCt4DyfLG0P4) that we might want to reuse. Open the link for this entry for reference as we analyze the queried data.

From the Overview page of the entry, copy the `entry_id` from the left-hand side where the entry metadata is displayed. Define a variable with this information:

```python
entry_id = ## PLACE ENTRY_ID HERE
```
We also need to define the API endpoint:

```python
nomad_api_prefix = 'https://nomad-lab.eu/prod/v1/api/v1/'
```

To download the entire archive for the entry of interest, we only have to execute a single command, and then we set the response to the variable `data`:

```python
response = requests.get(nomad_api_prefix + 'entries/' + entry_id + '/archive/download')

data = response.json()
```

!!! warning "warning"

        The download may take 5 minutes or more, depending on your Internet's bandwidth.

???+ info

    Python provides a module for packaging and sending requests, aptly named `requests`. It comes with the methods `put`, `delete`, `get`, and `post`. Notice how the API dashboard lists each supported function next to its endpoint. The first 3 exactly serve the functionalities that we listed abovee (upload, delete, download). The last one, `post`, we will get into later.

    The formatted URL itself actually suffices to start the download. It just needs an interface. If you click on it (don't, it's just a hypothetical), your OS should open a browser to start the download. From the command line, you can use `curl`. The `requests` module is simply our Python interface. As with any https protocol, you will receive a [status code](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status). Additional information is transmitted in a JSON format (another web standard), which we deserialize to a dictionary here. When everything is successful, this contains the data we were looking for. In case of an error, the NOMAD API uses it to better articulate the reason under the keyword `detail`. For the full format we again refer the reader to the API dashboard.

??? tip

    Here is a more thorough set of functions for executing the download, while timing the download, and printing out some response info:

    ```python
    nomad_api_prefix = 'https://nomad-lab.eu/prod/v1/api/v1/'

    def nomad_individual_archive_url(entry_id: str, endpoint_type: str=''):
        '''Produces the endpoint URL for downloading a NOMAD individual archive.
        `entry_id` specifies the entry ID of the particular archive you want to download.
        Use `endpoint_type` to further specify the particular subtype (`download` or `query`).'''

        endpoint_specifications = ('download', 'query')
        endpoint = f'{nomad_api_prefix}/entries/{entry_id}/archive'

        if endpoint_type :
            if endpoint_type in endpoint_specifications:
                endpoint += f'/{endpoint_type}'
            else:
                raise ValueError(f'endpoint_type must be one of {endpoint_specifications}')
        return endpoint
    ```


    ```python
    def measure_method(method, *args, **kwargs):
        """
        Measure the execution time of a given method with arguments.

        Args:
            method: The method/function to be measured.
            *args: Positional arguments to be passed to the method.
            **kwargs: Keyword arguments to be passed to the method.
        """
        start_time = t.time()
        result = method(*args, **kwargs)
        end_time = t.time()
        elapsed_time = end_time - start_time

        elapsed_minutes = int(elapsed_time // 60)
        elapsed_seconds = int(elapsed_time % 60)

        print(f"Method took {elapsed_minutes} minutes and {elapsed_seconds} seconds to execute.")
        return result
    ```

    ```python
    # execute the download
    nomad_url = nomad_individual_archive_url('hxaepf6x12Xt2IX2jCt4DyfLG0P4', endpoint_type='download')
    response = measure_method(requests.get, nomad_url)
    data = response.json()

    # print some of the responses
    print(f'This is the endpoint URL: {nomad_url}. Click on it start downloading the archive via your browser.')
    print(f"This is the {response} message. In case of an error, check `response['detail']` to get the additional information.")
    print(f"This is the top-level data structure of the deserialized message: {data.keys()}")
    ```

        Method took 8 minutes and 47 seconds to execute.
        This is the endpoint URL: https://nomad-lab.eu/prod/v1/api/v1//entries/hxaepf6x12Xt2IX2jCt4DyfLG0P4/archive/download. Click on it start downloading the archive via your browser.
        This is the <Response [200]> message. In case of an error, check `response['detail']` to get the additional information.
        This is the top-level data structure of the deserialized message: dict_keys(['processing_logs', 'run', 'workflow2', 'metadata', 'results', 'm_ref_archives'])


The keys of this dictionary corresponds one-to-one with the [**DATA** tab of this entry's page](https://nomad-lab.eu/prod/v1/gui/search/entries/entry/id/hxaepf6x12Xt2IX2jCt4DyfLG0P4/data):

```python
print(data.keys())
```

    dict_keys(['processing_logs', 'run', 'workflow2', 'metadata', 'results', 'm_ref_archives'])


 If you are interested in exploring the full schema with all its possible sections / quantities, check out the [Metainfo Browser](https://nomad-lab.eu/prod/v1/gui/analyze/metainfo/nomad.datamodel.datamodel.EntryArchive). You can use these representations of NOMAD's Metainfo schema to navigate the upcoming sections.

??? tip

    Here is an alternative way for viewing the data within your local python environment (although we recommend the DATA tab or Metainfo Browser):

    ```python
    def print_dict_as_tree(d, prefix="", is_last=True):
        """Function for printing a dictionary as a tree."""
        keys = list(d.keys())
        for i, key in enumerate(keys):
            if i == len(keys) - 1:
                new_prefix = prefix + "└─ "
            else:
                new_prefix = prefix + "├─ "

            value = d[key]
            type_str = f" ({type(value).__name__})"
            length_str = ""

            if isinstance(value, dict):
                print(new_prefix + str(key) + type_str)
                is_last_child = i == len(keys) - 1
                print_dict_as_tree(value, prefix + ("    " if is_last_child else "│   "), is_last_child)
            elif isinstance(value, list):
                has_dict = any(isinstance(item, dict) for item in value)
                if has_dict:
                    print(new_prefix + str(key) + type_str)
                    for item in value:
                        if isinstance(item, dict):
                            is_last_child = i == len(keys) - 1
                            print(prefix + ("    " if is_last_child else "│   ") + "├─ [")
                            print_dict_as_tree(item, prefix + ("    " if is_last_child else "│   ") + "│   ", True)
                            print(prefix + ("    " if is_last_child else "│   ") + "│   ]")
                        else:
                            is_last_child = i == len(keys) - 1
                            length_str = f" (Length: {len(value)})"
                else:
                    is_last_child = i == len(keys) - 1
                    length_str = f" (Length: {len(value)})"
                    print(new_prefix + str(key) + type_str + length_str)
            else:
                print(new_prefix + str(key) + type_str)

            if length_str:
                is_last_child = i == len(keys) - 1
                print(prefix + ("    " if is_last_child else "│   ") + "├─" + length_str)
    ```

!!! abstract "Assignment"

    Get the atom positions for the first frame of the trajectory from this dictionary.

??? success
    ```python
    data['run'][0]['system'][0]['atoms']['positions']
    ```

## Using tools from nomad-lab

### The NOMAD archive entry format

While it is perfectly acceptable to work directly with the archive dictionary, we can also convert this dictionary into a more sophisticated **NOMAD archive object.** This object supports **unit conversion** and a variety of ways for **traversing the data tree**.

```python
archive = EntryArchive.m_from_dict(data)
```

We then define some **easy access points** for later use. You can see how the Python object style of navigating is exploited (i.e., using `.` instead of `['']`). Also pay close attention to when indices are used. They appear whenever a section is flagged as `repeats` in the Metainfo Browser.


```python
section_run = archive.run[-1]
section_system = section_run.system
section_system_topology = section_run.system[0].atoms_group
section_atoms = section_system[0].atoms
```

Recall that the section **run** &rarr; **system**  is a list containing configurational information from each frame in the trajectory. Let's extract some information about the system, including positions, velocities, and box vectors:

```python
# get the number of atoms and frames, along with the atom names.
n_atoms = section_atoms.get('n_atoms')
n_frames = len(section_system) if section_system is not None else None
atom_names = section_atoms.get('labels')

# get the atom positions, velocites, and box dimensions
positions = np.empty(shape=(n_frames, n_atoms, 3))
velocities = np.empty(shape=(n_frames, n_atoms, 3))
dimensions = np.empty(shape=(n_frames, 6))
for frame_ind, frame in enumerate(section_system):
    sec_atoms_fr = frame.get('atoms')
    if sec_atoms_fr is not None:
        positions_frame = sec_atoms_fr.positions
        positions[frame_ind] = ureg.convert(positions_frame.magnitude, positions_frame.units,
                                            ureg.angstrom) if positions_frame is not None else None
        velocities_frame = sec_atoms_fr.velocities
        velocities[frame_ind] = ureg.convert(velocities_frame.magnitude, velocities_frame.units,
                                                ureg.angstrom / ureg.picosecond) if velocities_frame is not None else None
        latt_vec_tmp = sec_atoms_fr.get('lattice_vectors')
        if latt_vec_tmp is not None:
            length_conversion = ureg.convert(1.0, sec_atoms_fr.lattice_vectors.units, ureg.angstrom)
            dimensions[frame_ind] = [
                sec_atoms_fr.lattice_vectors.magnitude[0][0] * length_conversion,
                sec_atoms_fr.lattice_vectors.magnitude[1][1] * length_conversion,
                sec_atoms_fr.lattice_vectors.magnitude[2][2] * length_conversion,
                90, 90, 90]  # nb -- for cubic box!
```

!!! abstract "Assignment"

    Fill in the missing variables assignments in the following code to make the temperature trajectory plot for this calculation. Compare your result to the plot from the Overview page in the NOMAD GUI.

    ```python
    fig = plt.figure(figsize=(10,4))
    section_calculation =  ## FIND THE SECTION CALCULATION IN THE ARCHIVE ##
    temperature = []
    time = []
    temperature_unit =  ## FIND THE UNIT OF TEMPERATURE USED IN THE ARCHIVE ##
    time_unit =  ## FIND THE UNIT OF TIME USED IN THE ARCHIVE ##
    for calc in section_calculation:
        temperature.append()  ## FIND THE TEMPERATURE FOR THIS CALC ##
        time.append()  ## FIND THE TIME FOR THIS CALC ##


    plt.plot(time, temperature)
    plt.ylabel(temperature_unit, fontsize=12)
    plt.xlabel(time_unit, fontsize=12)
    plt.show()
    ```

??? success

    ```python
        fig = plt.figure(figsize=(10,4))
        section_calculation = archive.run[-1].calculation  ## FIND THE SECTION CALCULATION IN THE ARCHIVE ##
        temperature = []
        time = []
        temperature_unit = section_calculation[0].temperature.units  ## FIND THE UNIT OF TEMPERATURE USED IN THE ARCHIVE ##
        time_unit = section_calculation[0].time.units  ## FIND THE UNIT OF TIME USED IN THE ARCHIVE ##
        for calc in section_calculation:
            temperature.append(calc.temperature.magnitude)  ## FIND THE TEMPERATURE FOR THIS CALC ##
            time.append(calc.time.magnitude)  ## FIND THE TIME FOR THIS CALC ##


        plt.plot(time, temperature)
        plt.ylabel(temperature_unit, fontsize=12)
        plt.xlabel(time_unit, fontsize=12)
        plt.show()
    ```

<div class="click-zoom">
    <label>
        <input type="checkbox">
        <img src="../assets/md_tutorial_3/Protein-Water_Structure_15_0.png" alt="temperature_trajectory" width="90%" title="Temperature Trajectory.">
    </label>
</div>

As you may have noticed, one of our bottlenecks in visualizing the trajectory is downloading the data. This is due to the archive's size (35.8 MB, not too uncommon with MD entries). It may be the case that before committing to downloading the entire archive for further analysis we want to examine a particular quantity, e.g., the temperature trajectory. This is a job for the `/query` endpoint. Go back to the [API dashboard](https://nomad-lab.eu/prod/v1/staging/api/v1/extensions/docs#/entries%2Farchive/post_entry_archive_query_entries__entry_id__archive_query_post){:target="_blank"} and check out its schema.

This endpoint uses `post`, which is either used to add data (such as under `uploads`) or more complex queries and additional parameters, i.e. a more customizable `get` statement. This is in line with the standard semantics in HTTPS messages. In the case of our `/query` endpoint, the parameter we are looking for is `required` -the sections / quantities to be downloaded. Their specification follows the archive's tree structure as a nested dictionary. `requests` can append this information to the HTTPS body using the `json` argument. Below you will find the query specification. Pay attention to the optional use of indexes.

```python
query_specification = {
    "required": {
        "run[0]": {
            "calculation": {
                "temperature": "*",
                "time": "*"
            }
        }
    }
}
```

```python
response = requests.get(nomad_api_prefix + 'entries/' + entry_id + '/archive/query', json=query_specification)

data = response.json()
```

??? tip

    Or using the functions provided in the previous tips:
    ```python
    nomad_url_filtered = nomad_individual_archive_url('hxaepf6x12Xt2IX2jCt4DyfLG0P4', endpoint_type='query')
    response_filtered = measure_method(requests.post, nomad_url_filtered, json=query_specification)
    data_filtered = response_filtered.json()
    ```

        Method took 0 minutes and 2 seconds to execute.


Note the difference in time! There is a noticeable speedup.

The only disadvantage is that `EntryArchive` will fail with a partial archive. We can use still use the data as we would any dictionary to reproduce the same plot above. Just be careful to take care of unit conversions! To reintroduce units, multiply the quantity with its corresponding `ureg` unit, e.g. `ureg.second`. The quantities, as downloaded, are SI by default.

??? tip

    You can convert between units easily with the ureg module. For example, if a quantity `quantity_with_units` has units of seconds, you can convert to picoseconds with: `quantity_with_units = ureg.convert(quantity_with_units, quantity_with_units.units(), ureg.picoseconds)`.

Now, take some time to search through the calculation section to see what other quantities are stored for this simulation.

!!! abstract "Assignment"
    Now let's plot the center of mass molecular radial distribution function, averaged over the last 80% of the trajectory, as seeen in the Structural Properties card of the Overview page (red curve in plot). Fill in the missing variables assignments in the following code:

    ```python
    fig = plt.figure(figsize=(8,4))
    section_MD =  ## FIND THE MOLECULAR DYNAMICS WORKFLOW SECTION IN THE ARCHIVE ##
    rdf_HEX_HEX =  ## FIND THE LAST HEX-HEX RDF STORED IN THE ARCHIVE ##
    rdf_start =  ## FIND THE STARTING FRAME FOR AVERAGING FOR THIS RDF ##
    rdf_end =  ## FIND THE ENDING FRAME FOR AVERAGING FOR THIS RDF ##

    bins = ureg.convert(rdf_HEX_HEX.bins.magnitude, rdf_HEX_HEX.bins.units, ureg.angstrom)

    plt.plot(bins, rdf_HEX_HEX.value)
    plt.xlabel(ureg.angstrom, fontsize=12)
    plt.ylabel('HEX-HEX rdf', fontsize=12)
    plt.xlim(0.1,15.0)
    plt.show()
    ```

??? success

    ```python
    fig = plt.figure(figsize=(8,4))
    section_MD = archive.workflow2  ## FIND THE MOLECULAR DYNAMICS WORKFLOW SECTION IN THE ARCHIVE ##
    rdf_HEX_HEX = section_MD.results.radial_distribution_functions[0].radial_distribution_function_values[-1]  ## FIND THE LAST HEX-HEX RDF STORED IN THE ARCHIVE ##
    rdf_start = rdf_HEX_HEX.frame_start  ## FIND THE STARTING FRAME FOR AVERAGING FOR THIS RDF ##
    rdf_end = rdf_HEX_HEX.frame_end  ## FIND THE ENDING FRAME FOR AVERAGING FOR THIS RDF ##

    bins = ureg.convert(rdf_HEX_HEX.bins.magnitude, rdf_HEX_HEX.bins.units, ureg.angstrom)

    plt.plot(bins, rdf_HEX_HEX.value)
    plt.xlabel(ureg.angstrom, fontsize=12)
    plt.ylabel('HEX-HEX rdf', fontsize=12)
    plt.xlim(0.1,15.0)
    plt.show()
    ```

<div class="click-zoom">
    <label>
        <input type="checkbox">
        <img src="../assets/md_tutorial_3/Protein-Water_Structure_19_0.png" alt="temperature_trajectory" width="90%" title="Temperature Trajectory.">
    </label>
</div>

Take some time to search through the workflow2 section to see what other quantities are stored there for this simulation.

### The archive_to_universe function

We have seen above how to access quantities stored within a NOMAD archive entry using either the dictionary or NOMAD archive entry representation. This approach is sufficient for extracting singular quantities from the archive for further analysis.

However, it would also be useful to have converters to store the archive for an MD simulation in a format more convenient to perform analysis. In particular, one may want to utilize existing analysis software to perform standard calculations. We have already implemented a converter to the *MDAnalysis* format. Run the following command to convert the archive into an MDAnalysis `universe`:

```python
universe = archive_to_universe(archive)
```

Check which molecule types are present in the simulation:

```python
print('Molecule Types')
print('--------------')
for moltype in np.unique(universe.atoms.moltypes):
    print(moltype)
```

    Molecule Types
    --------------
    HEX

### Simple analysis with MDAnalysis

Let's calculate the center of mass rdf and compare with the plot stored in the archive. First define the appriate molecular groups:

```python
# Get an atom group for the Hexane molecules
AG_HEX = universe.select_atoms('moltype HEX')

# Create a "bead group" for the HEXANE molecules
BG_HEX = BeadGroup(AG_HEX, compound="fragments")

# Define parameters for the rdf calculation
min_box_dimension = np.min(universe.trajectory[0].dimensions[:3])
max_rdf_dist = min_box_dimension / 2
n_bins = 200
n_smooth = 2
n_prune = 1
```

??? tip

    In MDAnalysis, it is not trivial to calculate center of mass rdfs.
    The concept of bead groups comes from a known work-around.
    This class is imported from the NOMAD software.


Now run the rdf calculation using the MDAnalysis function `InterRDF`:

```python
# should take ~2 min
exclusion_block = (1, 1)  # for removing self-distance
rdf = MDA_RDF.InterRDF(
    BG_HEX, BG_HEX, range=(0, max_rdf_dist),
    exclusion_block=exclusion_block, nbins=n_bins).run(
    rdf_start, rdf_end, n_prune)
```

Smooth the rdf:

```python
rdf.results.bins = rdf.results.bins[int(n_smooth / 2):-int(n_smooth / 2)]
rdf.results.rdf = np.convolve(
    rdf.results.rdf, np.ones((n_smooth,)) / n_smooth,
    mode='same')[int(n_smooth / 2):-int(n_smooth / 2)]
```

Plot the rdf:

```python
fig = plt.figure(figsize=(8,4))
plt.plot(bins, rdf_HEX_HEX.value, label='NOMAD archive', color='k', lw=2)
plt.plot(rdf.results.bins, rdf.results.rdf, label='MDAnalysis', linestyle='--', color='r', lw=2)

plt.legend(fontsize=16)
plt.xlabel(ureg.angstrom, fontsize=12)
plt.ylabel('SOL-SOL rdf', fontsize=12)
plt.xlim(0.1, 10.)
plt.show()
```

<div class="click-zoom">
    <label>
        <input type="checkbox">
        <img src="../assets/md_tutorial_3/Protein-Water_Structure_28_0.png" alt="hexane_rdf" width="90%" title="Hexane RDF.">
    </label>
</div>


Using MDAnalysis, we can also easily featurize the configurations for data-driven analysis. For example, calculate the pairwise distance matrix for carbons throughout the trajectory:

```python
carbon_indices = [ind for ind, type in enumerate(universe.atoms.types) if type.startswith('C')]
selection = 'index ' + ' '.join([str(ind) for ind in carbon_indices])
carbons_group = universe.select_atoms(f'{selection}')

for i_fr, frame in enumerate(universe.trajectory):
    if i_fr == 0:
        distances = self_distance_array(carbons_group.positions, box=frame._unitcell)
    else:
        distances = np.vstack((distances, self_distance_array(carbons_group.positions, box=frame._unitcell)))
print(distances.shape)
```

    (11, 1282401)


### Visualization using NGLViewer

We can use the MDAnalysis representation along the the module `nglview` to visualize the trajectory within our notebook. First, unwrap the coordinates to make the molecules whole for visualization:

```python
AG_all = universe.select_atoms('all')
for ts in universe.trajectory:
    AG_all.unwrap(compound='fragments')
```

Now, set up the viewer with a minimal representation:
```python
view = nv.show_mdanalysis(AG_all)
view.center()
view.clear()  # clear the initial representation automatically set up by nglview
view.add_point('all')  # employ lightest rep
# adjust the widget size
view._set_size('700px', '600px')


view
```

<div class="click-zoom">
    <label>
        <input type="checkbox">
        <img src="../assets/md_tutorial_3/Vis_0.png" alt="hexane_rdf" width="70%" title="Hexane RDF.">
    </label>
</div>


Then, you can adjust the visualization using nglview [selection commands](https://nglviewer.org/ngl/api/manual/usage/selection-language.html):

```python
moltype = 'HEX'
view.clear()
view.add_point('all')
selection = '@' + ', '.join([str(i) for i in universe.select_atoms('molnum 0')._ix])
view.add_spacefill(selection)
```

<div class="click-zoom">
    <label>
        <input type="checkbox">
        <img src="../assets/md_tutorial_3/Vis_1.png" alt="hexane_rdf" width="70%" title="Hexane RDF.">
    </label>
</div>


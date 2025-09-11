# systems

## GET /systems/{entry_id}

**Summary:** Build and retrieve an atomistic structure file from data within an entry.

Build and retrieve a structure file containing an atomistic system stored
within an entry.

All length dimensions in the structure files are in Ångstroms (=1e-10 meter).

Note that some formats are more restricted and cannot fully
describe certains kinds of systems. For examples some entries within NOMAD
do not contain a unit cell (e.g. molecules), whereas some formats require it
to be present.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `entry_id` | path | string | True | The unique entry id of the entry to retrieve archive data from. |
| `path` | query | string | True | Path to a NOMAD System inside the archive. The targeted path should
point to a system in `run.system` or `results.material.topology`.
The following path types are supported:

- `run/0/system/0`: Path to system in `run.system`
- `results/material/topology/0`: Path to system in `results.material.topology`
- `run/0/system/-1`: Negative indices are supported. |
| `format` | query | FormatEnum | False | The file format for the system. The following formats are supported:

- `cif`: Crystallographic Information File
- `xyz`: XYZ file. The comment line contains information that
        complies with the extended XYZ specification.
- `pdb`: Protein Data Bank file. Note that valid PDB files
        require a CRYST1 record, while certains systems in NOMAD may not have a
        unit cell associated with them. In this case the returned structure file
        will contain a dummy CRYST1 record in order to load the atomic
        positions.

Here is a brief rundown of the different features each format supports:

Format|Cartesian positions without unit cell|Full lattice vectors|Periodic boundary conditions (PBC)
:---|:---:|:---:|:---:
cif|&#9745;|&#9744;|&#9744;
xyz|&#9745;|&#9745;|&#9745;
pdb|&#9744;|&#9744;|&#9744; |
| `wrap_mode` | query | WrapModeEnum | False | Determines how to handle atomic positions for the requested system. The available options are:

- `original`: The original positions as set in the data
- `wrap`: Positions are wrapped to be inside the cell respecting periodic boundary conditions
- `unwrap`: Positions are reconstructed so that the structure is not split by
periodic cell boundaries. Note that this produces meaningful results
only if the system dimensions are smaller than the unit cell.

             |
| `signature_token` | query | string | False | Signature token used to sign download urls. |

### Response (200) — short

*Type:* object

### Examples

**curl**

```bash
curl -X GET '/prod/v1/api/v1/systems/{entry_id}?path=<value>'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/systems/{entry_id}'
params = {'path': '<value>'}
r = requests.get(url, params=params, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `get_entry_raw_file_systems__entry_id__get`  

*source_url:* /prod/v1/api/v1/extensions/docs

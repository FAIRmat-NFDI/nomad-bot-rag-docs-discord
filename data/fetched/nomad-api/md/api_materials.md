# materials

## GET /materials

**Summary:** Search materials and retrieve their metadata

Executes a *query* and returns a *page* of the results with *required* result data.
This is a version of `/entries/query`. Queries work a little different, because
we cannot put complex queries into URL parameters.

In addition to the `q` parameter (see parameter documentation for details), you can use all NOMAD
search quantities as parameters, e.g. `?atoms=H&atoms=O`. Those quantities can be
used with additional operators attached to their names, e.g. `?n_atoms__gte=3` for
all entries with more than 3 atoms. Operators are `all`, `any`, `none`, `gte`,
`gt`, `lt`, `lte`.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `owner` | query | object | False | The `owner` allows to limit the scope of the search based on entry ownership.
This is useful if you only want to search among all publicly downloadable
entries or only among your own entries, etc.

These are the possible owner values and their meaning:

* `admin`: No restriction. Only usable by an admin user.
* `all`: Published entries (with or without embargo), or entries that belong to you
    or are shared with you.
* `public`: Published entries without embargo.
* `shared`: Entries that belong to you or are shared with you.
* `staging`: Unpublished entries that belong to you or are shared with you.
* `user`: Entries that belong to you.
* `visible`: Published entries without embargo, or unpublished entries that belong to
    you or are shared with you. |
| `json_query` | query | object | False | To pass a query string in the format of JSON e.g. '{{"results.material.elements": ["H", "O"]}}'. |
| `q` | query | object | False | Since we cannot properly offer forms for all parameters in the OpenAPI dashboard,
you can use the parameter `q` and encode a query parameter like this
`atoms__H` or `n_atoms__gt__3`. Multiple usage of `q` will combine parameters with
logical *and*. |
| `page_size` | query | object | False | The page size, e.g. the maximum number of items contained in one response.
A `page_size` of 0 will return no results. |
| `order_by` | query | object | False | The results are ordered by the values of this field. You can order
by any indexed scalar value, or one following two special fields:

 - `_score`: Sorts by relevance score.
 - `_doc`: Use when sorting does not matter, gives the best performance.

If omitted, default ordering is applied. |
| `order` | query | object | False | The ordering direction of the results based on `order_by`. Its either
ascending `asc` or descending `desc`. Default is `asc`. |
| `page_after_value` | query | object | False | This attribute defines the position after which the page begins, and is used
to navigate through the total list of results.

When requesting the first page, no value should be provided for
`page_after_value`. Each response will contain a value `next_page_after_value`,
which can be used to obtain the next page (by setting `page_after_value` in
your next request to this value).

The field is encoded as a string, and the format of `page_after_value` and
`next_page_after_value` depends on which API method is used.

Some API functions additionally allows a simplified navigation, by specifying
the page number in the key `page`. It is however always possible to use
`page_after_value` and `next_page_after_value` to iterate through the results. |
| `page` | query | object | False | For simple, index-based pagination, this should contain the number of the
requested page (1-based). When provided in a request, this attribute can be
used instead of `page_after_value` to jump to a particular results page.

However, you can only retrieve up to the 10.000th entry with a page number.
Only one, `page`, `page_offset` or `page_after_value`, can be used. |
| `page_offset` | query | object | False | Return the page that follows the given number of entries. Overwrites
`page` and `page_after_value`.

However, you can only retrieve up to the 10.000th entry.
Only one, `page`, `page_offset` or `page_after_value`, can be used. |
| `include` | query | object | False | Quantities to include for each result. Only those quantities will be
returned. At least one id quantity (e.g. `entry_id`) will always be included. |
| `exclude` | query | object | False | Quantities to exclude for each result. Only all other quantities will
be returned. The entity's id quantity (e.g. `entry_id`) cannot be excluded. |

### Response (200) — short

*Schema:* `MetadataResponse`

### Examples

**curl**

```bash
curl -X GET '/prod/v1/api/v1/materials?owner=<value>'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/materials'
params = {'owner': '<value>'}
r = requests.get(url, params=params, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `get_entries_metadata_materials_get`  

*source_url:* /prod/v1/api/v1/extensions/docs

## POST /materials/query

**Summary:** Search materials and retrieve their metadata

Executes a *query* and returns a *page* of the results with *required* result data
as well as *statistics* and *aggregated* data.

This is the basic search operation to retrieve metadata for entries that match
certain search criteria (`query` and `owner`). All parameters (including `query`, `owner`)
are optional. Look at the body schema or parameter documentation for more details.

By default the *empty* search (that returns everything) is performed. Only a small
page of the search results are returned at a time; use `pagination` in subsequent
requests to retrive more data. Each entry has a lot of different *metadata*, use
`required` to limit the data that is returned.

The `statistics` and `aggregations` keys will further allow to return statistics
and aggregated data over all search results.

### Request Body (short)

*Schema:* `Metadata`

### Response (200) — short

*Schema:* `MetadataResponse`

### Examples

**curl**

```bash
curl -X POST '/prod/v1/api/v1/materials/query'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/materials/query'
r = requests.request('POST', url, json={}, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `post_entries_metadata_query_materials_query_post`  

*source_url:* /prod/v1/api/v1/extensions/docs

## GET /materials/{material_id}

**Summary:** Get the metadata of a material by its id

Retrives the material metadata for the given id.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `material_id` | path | string | True | The unique material id of the material to retrieve metadata from. |
| `include` | query | object | False | Quantities to include for each result. Only those quantities will be
returned. At least one id quantity (e.g. `entry_id`) will always be included. |
| `exclude` | query | object | False | Quantities to exclude for each result. Only all other quantities will
be returned. The entity's id quantity (e.g. `entry_id`) cannot be excluded. |

### Response (200) — short

*Schema:* `MaterialMetadataResponse`

### Examples

**curl**

```bash
curl -X GET '/prod/v1/api/v1/materials/{material_id}?include=<value>'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/materials/{material_id}'
params = {'include': '<value>'}
r = requests.get(url, params=params, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `get_material_metadata_materials__material_id__get`  

*source_url:* /prod/v1/api/v1/extensions/docs

# entries/metadata

## GET /entries

**Summary:** Search entries and retrieve their metadata

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
curl -X GET '/prod/v1/api/v1/entries?owner=<value>'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/entries'
params = {'owner': '<value>'}
r = requests.get(url, params=params, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `get_entries_metadata_entries_get`  

*source_url:* /prod/v1/api/v1/extensions/docs

## POST /entries/edit

**Summary:** Edit the user metadata of a set of entries

Updates the metadata of the specified entries.

**Note:**
  - Only admins can edit some of the fields.
  - Only entry level attributes (like `comment`, `references` etc.) can be set using
    this endpoint; upload level attributes (like `upload_name`, `coauthors`, embargo
    settings, etc) need to be set through the endpoint **uploads/upload_id/edit**.
  - If the upload is published, the only operation permitted using this endpoint is to
    edit the entries in datasets that where created by the current user.

### Request Body (short)

*Schema:* `MetadataEditRequest-Input`

### Response (200) — short

*Schema:* `MetadataEditRequest-Output`

### Examples

**curl**

```bash
curl -X POST '/prod/v1/api/v1/entries/edit'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/entries/edit'
r = requests.request('POST', url, json={}, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `post_entries_edit_entries_edit_post`  

*source_url:* /prod/v1/api/v1/extensions/docs

## POST /entries/edit_v0

**Summary:** Edit the user metadata of a set of entries

Performs or validates edit actions on a set of entries that match a given query.

### Request Body (short)

*Schema:* `EntryMetadataEdit`

### Response (200) — short

*Schema:* `EntryMetadataEditResponse`

### Examples

**curl**

```bash
curl -X POST '/prod/v1/api/v1/entries/edit_v0'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/entries/edit_v0'
r = requests.request('POST', url, json={}, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `post_entry_metadata_edit_entries_edit_v0_post`  

*source_url:* /prod/v1/api/v1/extensions/docs

## GET /entries/export

**Summary:** Search entries and download their metadata in selected format

(**Experimental**) Export metadata entries in a selected format.

This endpoint allows users to export metadata entries in either JSON or CSV format.
The format must be specified via the `Content-Type` HTTP header:
    - `application/json` → Returns the metadata as a JSON response.
    - `text/csv` → Returns the metadata as a CSV file.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `page_size` | query | integer | False |  |
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
| `include` | query | object | False | Quantities to include for each result. Only those quantities will be
returned. At least one id quantity (e.g. `entry_id`) will always be included. |
| `exclude` | query | object | False | Quantities to exclude for each result. Only all other quantities will
be returned. The entity's id quantity (e.g. `entry_id`) cannot be excluded. |
| `signature_token` | query | string | False | Signature token used to sign download urls. |
| `content-type` | header | string | False |  |

### Response (200) — short

*Type:* object

### Examples

**curl**

```bash
curl -X GET '/prod/v1/api/v1/entries/export?page_size=<value>'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/entries/export'
params = {'page_size': '<value>'}
r = requests.get(url, params=params, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `export_entries_metadata_entries_export_get`  

*source_url:* /prod/v1/api/v1/extensions/docs

## POST /entries/query

**Summary:** Search entries and retrieve their metadata

Executes a *query* and returns a *page* of the results with *required* result data
as well as *statistics* and *aggregated* data.

This is the basic search operation to retrieve metadata for entries that match
certain search criteria (`query` and `owner`). All parameters (including `query`, `owner`)
are optional. Look at the body schema or parameter documentation for more details.

By default the *empty* search (that returns everything) is performed. Only a small
page of the search results are returned at a time; use `pagination` in subsequent
requests to retrieve more data. Each entry has a lot of different *metadata*, use
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
curl -X POST '/prod/v1/api/v1/entries/query'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/entries/query'
r = requests.request('POST', url, json={}, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `post_entries_metadata_query_entries_query_post`  

*source_url:* /prod/v1/api/v1/extensions/docs

## GET /entries/{entry_id}

**Summary:** Get the metadata of an entry by its id

Retrives the entry metadata for the given id.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `entry_id` | path | string | True | The unique entry id of the entry to retrieve metadata from. |
| `include` | query | object | False | Quantities to include for each result. Only those quantities will be
returned. At least one id quantity (e.g. `entry_id`) will always be included. |
| `exclude` | query | object | False | Quantities to exclude for each result. Only all other quantities will
be returned. The entity's id quantity (e.g. `entry_id`) cannot be excluded. |

### Response (200) — short

*Schema:* `EntryMetadataResponse`

### Examples

**curl**

```bash
curl -X GET '/prod/v1/api/v1/entries/{entry_id}?include=<value>'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/entries/{entry_id}'
params = {'include': '<value>'}
r = requests.get(url, params=params, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `get_entry_metadata_entries__entry_id__get`  

*source_url:* /prod/v1/api/v1/extensions/docs

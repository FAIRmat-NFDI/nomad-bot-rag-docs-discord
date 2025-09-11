# entries/raw

## GET /entries/raw

**Summary:** Search entries and download their raw files

This operation will perform a search and stream a .zip file with the raw files of the
found entries.

Each entry on NOMAD has a set of raw files. These are the files in their original form,
i.e. as provided by the uploader. More specifically, an entry has a *mainfile*, identified as
parseable. For CMS entries, the mainfile is usually the main output file of the code. All other
files in the same directory are considered the entries *auxiliary* no matter their role
or if they were actually parsed by NOMAD.

After performing a search (that uses the same parameters as in all search operations),
NOMAD will iterate through all results and create a .zip-file with all the entries'
main and auxiliary files. The files will be organized in the same directory structure
that they were uploaded in. The respective upload root directories are further prefixed
with the `upload_id` of the respective uploads. The .zip-file will further contain
a `manifest.json` with `upload_id`, `entry_id`, and `mainfile` of each entry.

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
| `compress` | query | object | False | By default the returned zip file is not compressed. This allows to enable compression.
Compression will reduce the rate at which data is provided, often below
the rate of the compression. Therefore, compression is only sensible if the
network connection is limited. |
| `glob_pattern` | query | object | False | An optional *glob* (or unix style path) pattern that is used to filter the
returned files. Only files matching the pattern are returned. The pattern is only
applied to the end of the full path. Internally
[fnmatch](https://docs.python.org/3/library/fnmatch.html) is used. |
| `re_pattern` | query | object | False | An optional regexp that is used to filter the returned files. Only files matching
the pattern are returned. The pattern is applied in search mode to the full
path of the files. With `$` and `^` you can control if you want to match the
whole path.

A re pattern will replace a given glob pattern. |
| `include_files` | query | object | False | Optional list of file names. Only files with these names are included in the
results. This will overwrite any given glob or re pattern. |
| `signature_token` | query | string | False | Signature token used to sign download urls. |

### Response (200) — short

*Type:* object

### Examples

**curl**

```bash
curl -X GET '/prod/v1/api/v1/entries/raw?owner=<value>'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/entries/raw'
params = {'owner': '<value>'}
r = requests.get(url, params=params, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `get_entries_raw_entries_raw_get`  

*source_url:* /prod/v1/api/v1/extensions/docs

## POST /entries/raw/query

**Summary:** Search entries and download their raw files

This operation will perform a search and stream a .zip file with the raw files of the
found entries.

Each entry on NOMAD has a set of raw files. These are the files in their original form,
i.e. as provided by the uploader. More specifically, an entry has a *mainfile*, identified as
parseable. For CMS entries, the mainfile is usually the main output file of the code. All other
files in the same directory are considered the entries *auxiliary* no matter their role
or if they were actually parsed by NOMAD.

After performing a search (that uses the same parameters as in all search operations),
NOMAD will iterate through all results and create a .zip-file with all the entries'
main and auxiliary files. The files will be organized in the same directory structure
that they were uploaded in. The respective upload root directories are further prefixed
with the `upload_id` of the respective uploads. The .zip-file will further contain
a `manifest.json` with `upload_id`, `entry_id`, and `mainfile` of each entry.

### Request Body (short)

*Schema:* `EntriesRaw`

### Response (200) — short

*Type:* object

### Examples

**curl**

```bash
curl -X POST '/prod/v1/api/v1/entries/raw/query'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/entries/raw/query'
r = requests.request('POST', url, json={}, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `post_entries_raw_query_entries_raw_query_post`  

*source_url:* /prod/v1/api/v1/extensions/docs

## GET /entries/rawdir

**Summary:** Search entries and get their raw files metadata

Will perform a search and return a *page* of raw file metadata for entries fulfilling
the query. This allows you to get a complete list of all rawfiles with their full
path in their respective upload and their sizes. The first returned files for each
entry, is their respective *mainfile*.

Each entry on NOMAD has a set of raw files. These are the files in their original form,
i.e. as provided by the uploader. More specifically, an entry has a *mainfile*, identified as
parseable. For CMS entries, the mainfile is usually the main output file of the code. All other
files in the same directory are considered the entries *auxiliary* no matter their role
or if they were actually parsed by NOMAD.

This operation supports the usual `owner`, `query`, and `pagination` parameters.

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

### Response (200) — short

*Schema:* `EntriesRawDirResponse`

### Examples

**curl**

```bash
curl -X GET '/prod/v1/api/v1/entries/rawdir?owner=<value>'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/entries/rawdir'
params = {'owner': '<value>'}
r = requests.get(url, params=params, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `get_entries_rawdir_entries_rawdir_get`  

*source_url:* /prod/v1/api/v1/extensions/docs

## POST /entries/rawdir/query

**Summary:** Search entries and get their raw files metadata

Will perform a search and return a *page* of raw file metadata for entries fulfilling
the query. This allows you to get a complete list of all rawfiles with their full
path in their respective upload and their sizes. The first returned files for each
entry, is their respective *mainfile*.

Each entry on NOMAD has a set of raw files. These are the files in their original form,
i.e. as provided by the uploader. More specifically, an entry has a *mainfile*, identified as
parseable. For CMS entries, the mainfile is usually the main output file of the code. All other
files in the same directory are considered the entries *auxiliary* no matter their role
or if they were actually parsed by NOMAD.

This operation supports the usual `owner`, `query`, and `pagination` parameters.

### Request Body (short)

*Schema:* `EntriesRawDir`

### Response (200) — short

*Schema:* `EntriesRawDirResponse`

### Examples

**curl**

```bash
curl -X POST '/prod/v1/api/v1/entries/rawdir/query'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/entries/rawdir/query'
r = requests.request('POST', url, json={}, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `post_entries_rawdir_query_entries_rawdir_query_post`  

*source_url:* /prod/v1/api/v1/extensions/docs

## POST /entries/{entry_id}/edit

**Summary:** Edit a raw mainfile in archive format.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `entry_id` | path | string | True | The unique entry id of the entry to edit. |

### Request Body (short)

*Schema:* `EntryEdit`

### Response (200) — short

*Schema:* `EntryEditResponse`

### Examples

**curl**

```bash
curl -X POST '/prod/v1/api/v1/entries/{entry_id}/edit'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/entries/{entry_id}/edit'
r = requests.request('POST', url, json={}, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `post_entry_edit_entries__entry_id__edit_post`  

*source_url:* /prod/v1/api/v1/extensions/docs

## GET /entries/{entry_id}/raw

**Summary:** Get the raw data of an entry by its id

Streams a .zip file with the raw files from the requested entry.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `entry_id` | path | string | True | The unique entry id of the entry to retrieve raw data from. |
| `compress` | query | object | False | By default the returned zip file is not compressed. This allows to enable compression.
Compression will reduce the rate at which data is provided, often below
the rate of the compression. Therefore, compression is only sensible if the
network connection is limited. |
| `glob_pattern` | query | object | False | An optional *glob* (or unix style path) pattern that is used to filter the
returned files. Only files matching the pattern are returned. The pattern is only
applied to the end of the full path. Internally
[fnmatch](https://docs.python.org/3/library/fnmatch.html) is used. |
| `re_pattern` | query | object | False | An optional regexp that is used to filter the returned files. Only files matching
the pattern are returned. The pattern is applied in search mode to the full
path of the files. With `$` and `^` you can control if you want to match the
whole path.

A re pattern will replace a given glob pattern. |
| `include_files` | query | object | False | Optional list of file names. Only files with these names are included in the
results. This will overwrite any given glob or re pattern. |
| `signature_token` | query | string | False | Signature token used to sign download urls. |

### Response (200) — short

*Type:* object

### Examples

**curl**

```bash
curl -X GET '/prod/v1/api/v1/entries/{entry_id}/raw?compress=<value>'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/entries/{entry_id}/raw'
params = {'compress': '<value>'}
r = requests.get(url, params=params, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `get_entry_raw_entries__entry_id__raw_get`  

*source_url:* /prod/v1/api/v1/extensions/docs

## GET /entries/{entry_id}/raw/{path}

**Summary:** Get the raw data of an entry by its id

Streams the contents of an individual file from the requested entry.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `entry_id` | path | string | True | The unique entry id of the entry to retrieve raw data from. |
| `path` | path | string | True | A relative path to a file based on the directory of the entry's mainfile. |
| `offset` | query | object | False | Integer offset that marks the start of the contents to retrieve. Default
is the start of the file. |
| `length` | query | object | False | The amounts of contents in bytes to stream. By default, the remainder of
the file is streamed. |
| `decompress` | query | object | False | Attempt to decompress the contents, if the file is .gz or .xz. |
| `signature_token` | query | string | False | Signature token used to sign download urls. |

### Response (200) — short

*Type:* object

### Examples

**curl**

```bash
curl -X GET '/prod/v1/api/v1/entries/{entry_id}/raw/{path}?offset=<value>'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/entries/{entry_id}/raw/{path}'
params = {'offset': '<value>'}
r = requests.get(url, params=params, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `get_entry_raw_file_entries__entry_id__raw__path__get`  

*source_url:* /prod/v1/api/v1/extensions/docs

## GET /entries/{entry_id}/rawdir

**Summary:** Get the raw files metadata for an entry by its id

Returns the file metadata for all input and output files (including auxiliary files)
of the given `entry_id`. The first file will be the *mainfile*.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `entry_id` | path | string | True | The unique entry id of the entry to retrieve raw data from. |

### Response (200) — short

*Schema:* `EntryRawDirResponse`

### Examples

**curl**

```bash
curl -X GET '/prod/v1/api/v1/entries/{entry_id}/rawdir'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/entries/{entry_id}/rawdir'
r = requests.get(url, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `get_entry_rawdir_entries__entry_id__rawdir_get`  

*source_url:* /prod/v1/api/v1/extensions/docs

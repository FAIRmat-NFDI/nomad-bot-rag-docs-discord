# entries/archive

## GET /entries/archive

**Summary:** Search entries and access their archives

This operation will perform a search with the given `query` and `owner` and return
the a *page* of `required` archive data. Look at the body schema or parameter documentation
for more details. The **GET** version of this operation will only allow to provide
the full archives.

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

*Schema:* `EntriesArchiveResponse`

### Examples

**curl**

```bash
curl -X GET '/prod/v1/api/v1/entries/archive?owner=<value>'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/entries/archive'
params = {'owner': '<value>'}
r = requests.get(url, params=params, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `get_entries_archive_query_entries_archive_get`  

*source_url:* /prod/v1/api/v1/extensions/docs

## GET /entries/archive/download

**Summary:** Search entries and download their archives

This operation will perform a search with the given `query` and `owner` and stream
a .zip-file with the full archive contents for all matching entries. This is not
paginated. Look at the body schema or parameter documentation for more details.

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
curl -X GET '/prod/v1/api/v1/entries/archive/download?owner=<value>'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/entries/archive/download'
params = {'owner': '<value>'}
r = requests.get(url, params=params, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `get_entries_archive_download_entries_archive_download_get`  

*source_url:* /prod/v1/api/v1/extensions/docs

## POST /entries/archive/download/query

**Summary:** Search entries and download their archives

This operation will perform a search with the given `query` and `owner` and stream
a .zip-file with the full archive contents for all matching entries. This is not
paginated. Look at the body schema or parameter documentation for more details.

### Request Body (short)

*Schema:* `EntriesArchiveDownload`

### Response (200) — short

*Type:* object

### Examples

**curl**

```bash
curl -X POST '/prod/v1/api/v1/entries/archive/download/query'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/entries/archive/download/query'
r = requests.request('POST', url, json={}, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `post_entries_archive_download_query_entries_archive_download_query_post`  

*source_url:* /prod/v1/api/v1/extensions/docs

## POST /entries/archive/query

**Summary:** Search entries and access their archives

This operation will perform a search with the given `query` and `owner` and return
the a *page* of `required` archive data. Look at the body schema or parameter documentation
for more details. The **GET** version of this operation will only allow to provide
the full archives.

### Request Body (short)

*Schema:* `EntriesArchive`

### Response (200) — short

*Schema:* `EntriesArchiveResponse`

### Examples

**curl**

```bash
curl -X POST '/prod/v1/api/v1/entries/archive/query'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/entries/archive/query'
r = requests.request('POST', url, json={}, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `post_entries_archive_query_entries_archive_query_post`  

*source_url:* /prod/v1/api/v1/extensions/docs

## GET /entries/{entry_id}/archive

**Summary:** Get the archive for an entry by its id

Returns the full archive for the given `entry_id`.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `entry_id` | path | string | True | The unique entry id of the entry to retrieve archive data from. |

### Response (200) — short

*Schema:* `EntryArchiveResponse`

### Examples

**curl**

```bash
curl -X GET '/prod/v1/api/v1/entries/{entry_id}/archive'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/entries/{entry_id}/archive'
r = requests.get(url, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `get_entry_archive_entries__entry_id__archive_get`  

*source_url:* /prod/v1/api/v1/extensions/docs

## GET /entries/{entry_id}/archive/download

**Summary:** Get the archive for an entry by its id as plain archive json

Returns the full archive for the given `entry_id`.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `entry_id` | path | string | True | The unique entry id of the entry to retrieve archive data from. |
| `signature_token` | query | string | False | Signature token used to sign download urls. |

### Response (200) — short

*Type:* object

### Examples

**curl**

```bash
curl -X GET '/prod/v1/api/v1/entries/{entry_id}/archive/download?signature_token=<value>'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/entries/{entry_id}/archive/download'
params = {'signature_token': '<value>'}
r = requests.get(url, params=params, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `get_entry_archive_download_entries__entry_id__archive_download_get`  

*source_url:* /prod/v1/api/v1/extensions/docs

## POST /entries/{entry_id}/archive/query

**Summary:** Get the archive for an entry by its id

Returns a partial archive for the given `entry_id` based on the `required` specified
in the body.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `entry_id` | path | string | True | The unique entry id of the entry to retrieve archive data from. |

### Request Body (short)

*Schema:* `EntryArchiveRequest`

### Response (200) — short

*Schema:* `EntryArchiveResponse`

### Examples

**curl**

```bash
curl -X POST '/prod/v1/api/v1/entries/{entry_id}/archive/query'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/entries/{entry_id}/archive/query'
r = requests.request('POST', url, json={}, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `post_entry_archive_query_entries__entry_id__archive_query_post`  

*source_url:* /prod/v1/api/v1/extensions/docs

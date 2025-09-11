# uploads/metadata

## GET /uploads

**Summary:** List uploads of authenticated user.

Retrieves metadata about all uploads that match the given query criteria.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `roles` | query | array | False | Only return uploads where the user has one of the given roles. |
| `include_all` | query | boolean | False | Include uploads that are shared with all users. |
| `upload_id` | query | object | False | Search for uploads matching the given id. Multiple values can be specified. |
| `upload_name` | query | object | False | Search for uploads matching the given upload_name. Multiple values can be specified. |
| `is_processing` | query | object | False | If True, only include currently processing uploads.
If False, do not include currently processing uploads.
If unset, include everything. |
| `is_published` | query | object | False | If True: only include published uploads.
If False: only include unpublished uploads.
If unset: include everything. |
| `process_status` | query | object | False | Search by the process status. |
| `is_owned` | query | object | False | If True: only include owned uploads.
If False: only include shared uploads.
If unset: include everything. |
| `page_size` | query | object | False | The page size, e.g. the maximum number of items contained in one response.
A `page_size` of 0 will return no results. |
| `order_by` | query | object | False | The results are ordered by the values of this field. If omitted, default
ordering is applied. |
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
| `page` | query | object | False | The number of the page (1-based). When provided in a request, this attribute
can be used instead of `page_after_value` to jump to a particular results page.

**NOTE #1**: the option to request pages by submitting the `page` number is
limited. There are api calls where this attribute cannot be used for indexing,
or where it can only be used partially. **If you want to just iterate through
all the results, always use the `page_after_value` and `next_page_after_value`!**

**NOTE #2**: Only one, `page`, `page_offset` or `page_after_value`, can be used. |
| `page_offset` | query | object | False | The number of skipped entries. When provided in a request, this attribute
can be used instead of `page_after_value` to jump to a particular results page.

**NOTE #1**: the option to request pages by submitting the `page_offset` number is
limited. There are api calls where this attribute cannot be used for indexing,
or where it can only be used partially. **If you want to just iterate through
all the results, always use the `page_after_value` and `next_page_after_value`!**

**NOTE #2**: Only one, `page`, `page_offset` or `page_after_value`, can be used. |

### Response (200) — short

*Schema:* `UploadProcDataQueryResponse`

### Examples

**curl**

```bash
curl -X GET '/prod/v1/api/v1/uploads?roles=<value>'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/uploads'
params = {'roles': '<value>'}
r = requests.get(url, params=params, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `get_uploads_uploads_get`  

*source_url:* /prod/v1/api/v1/extensions/docs

## GET /uploads/{upload_id}

**Summary:** Get a specific upload

Fetches a specific upload by its upload_id.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `upload_id` | path | string | True | The unique id of the upload to retrieve. |

### Response (200) — short

*Schema:* `UploadProcDataResponse`

### Examples

**curl**

```bash
curl -X GET '/prod/v1/api/v1/uploads/{upload_id}'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/uploads/{upload_id}'
r = requests.get(url, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `get_upload_uploads__upload_id__get`  

*source_url:* /prod/v1/api/v1/extensions/docs

## POST /uploads/{upload_id}/edit

**Summary:** Updates the metadata of the specified upload.

Updates the metadata of the specified upload and entries. An optional `query` can be
specified to select only some of the entries of the upload (the query results are
automatically restricted to the specified upload).

**Note:**
  - Only admins can edit some of the fields.
  - The embargo of a published upload is lifted by setting the `embargo_length` attribute
    to 0.
  - If the upload is published, the only operations permitted using this endpoint is to
    lift the embargo, i.e. set `embargo_length` to 0, and to edit the entries in datasets
    that where created by the current user.
  - If a query is specified, it is not possible to edit upload level metadata (like
    `upload_name`, `coauthors`, etc.), as the purpose of queries is to select only a
    subset of the upload entries to edit, but changing upload level metadata would affect
    **all** entries of the upload.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `upload_id` | path | string | True | The unique id of the upload. |

### Request Body (short)

*Schema:* `MetadataEditRequest-Input`

### Response (200) — short

*Schema:* `UploadProcDataResponse`

### Examples

**curl**

```bash
curl -X POST '/prod/v1/api/v1/uploads/{upload_id}/edit'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/uploads/{upload_id}/edit'
r = requests.request('POST', url, json={}, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `post_upload_edit_uploads__upload_id__edit_post`  

*source_url:* /prod/v1/api/v1/extensions/docs

## GET /uploads/{upload_id}/entries

**Summary:** Get the entries of the specific upload as a list

Fetches the entries of a specific upload. Pagination is used to browse through the
results.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `upload_id` | path | string | True | The unique id of the upload to retrieve entries for. |
| `page_size` | query | object | False | The page size, e.g. the maximum number of items contained in one response.
A `page_size` of 0 will return no results. |
| `order_by` | query | object | False | The results are ordered by the values of this field. If omitted, default
ordering is applied. |
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
| `page` | query | object | False | The number of the page (1-based). When provided in a request, this attribute
can be used instead of `page_after_value` to jump to a particular results page.

**NOTE #1**: the option to request pages by submitting the `page` number is
limited. There are api calls where this attribute cannot be used for indexing,
or where it can only be used partially. **If you want to just iterate through
all the results, always use the `page_after_value` and `next_page_after_value`!**

**NOTE #2**: Only one, `page`, `page_offset` or `page_after_value`, can be used. |
| `page_offset` | query | object | False | The number of skipped entries. When provided in a request, this attribute
can be used instead of `page_after_value` to jump to a particular results page.

**NOTE #1**: the option to request pages by submitting the `page_offset` number is
limited. There are api calls where this attribute cannot be used for indexing,
or where it can only be used partially. **If you want to just iterate through
all the results, always use the `page_after_value` and `next_page_after_value`!**

**NOTE #2**: Only one, `page`, `page_offset` or `page_after_value`, can be used. |

### Response (200) — short

*Schema:* `EntryProcDataQueryResponse`

### Examples

**curl**

```bash
curl -X GET '/prod/v1/api/v1/uploads/{upload_id}/entries?page_size=<value>'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/uploads/{upload_id}/entries'
params = {'page_size': '<value>'}
r = requests.get(url, params=params, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `get_upload_entries_uploads__upload_id__entries_get`  

*source_url:* /prod/v1/api/v1/extensions/docs

## GET /uploads/{upload_id}/entries/{entry_id}

**Summary:** Get a specific entry for a specific upload

Fetches a specific entry for a specific upload.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `upload_id` | path | string | True | The unique id of the upload. |
| `entry_id` | path | string | True | The unique id of the entry, belonging to the specified upload. |

### Response (200) — short

*Schema:* `EntryProcDataResponse`

### Examples

**curl**

```bash
curl -X GET '/prod/v1/api/v1/uploads/{upload_id}/entries/{entry_id}'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/uploads/{upload_id}/entries/{entry_id}'
r = requests.get(url, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `get_upload_entry_uploads__upload_id__entries__entry_id__get`  

*source_url:* /prod/v1/api/v1/extensions/docs

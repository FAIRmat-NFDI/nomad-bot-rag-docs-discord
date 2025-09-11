# datasets

## GET /datasets/

**Summary:** Get a list of datasets

Retrieves all datasets that match the given criteria.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `dataset_id` | query | string | False |  |
| `dataset_name` | query | string | False |  |
| `user_id` | query | array | False |  |
| `dataset_type` | query | string | False |  |
| `doi` | query | string | False |  |
| `prefix` | query | string | False |  |
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

*Schema:* `DatasetsResponse`

### Examples

**curl**

```bash
curl -X GET '/prod/v1/api/v1/datasets/?dataset_id=<value>'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/datasets/'
params = {'dataset_id': '<value>'}
r = requests.get(url, params=params, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `get_datasets_datasets__get`  

*source_url:* /prod/v1/api/v1/extensions/docs

## POST /datasets/

**Summary:** Create a new dataset

Create a new dataset.

### Request Body (short)

*Schema:* `DatasetCreate`

### Response (200) — short

*Schema:* `DatasetResponse`

### Examples

**curl**

```bash
curl -X POST '/prod/v1/api/v1/datasets/'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/datasets/'
r = requests.request('POST', url, json={}, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `post_datasets_datasets__post`  

*source_url:* /prod/v1/api/v1/extensions/docs

## DELETE /datasets/{dataset_id}

**Summary:** Delete a dataset

Delete an dataset.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `dataset_id` | path | string | True | The unique dataset id of the dataset to delete. |

### Response (200) — short

*Schema:* `DatasetResponse`

### Examples

**curl**

```bash
curl -X DELETE '/prod/v1/api/v1/datasets/{dataset_id}'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/datasets/{dataset_id}'
r = requests.request('DELETE', url, json={}, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `delete_dataset_datasets__dataset_id__delete`  

*source_url:* /prod/v1/api/v1/extensions/docs

## GET /datasets/{dataset_id}

**Summary:** Get a list of datasets

Retrieves the dataset with the given id.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `dataset_id` | path | string | True | The unique dataset id of the dataset to retrieve. |

### Response (200) — short

*Schema:* `DatasetResponse`

### Examples

**curl**

```bash
curl -X GET '/prod/v1/api/v1/datasets/{dataset_id}'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/datasets/{dataset_id}'
r = requests.get(url, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `get_dataset_datasets__dataset_id__get`  

*source_url:* /prod/v1/api/v1/extensions/docs

## POST /datasets/{dataset_id}/action/doi

**Summary:** Assign a DOI to a dataset

Assign a DOI to a dataset.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `dataset_id` | path | string | True | The unique dataset id of the dataset to delete. |

### Response (200) — short

*Schema:* `DatasetResponse`

### Examples

**curl**

```bash
curl -X POST '/prod/v1/api/v1/datasets/{dataset_id}/action/doi'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/datasets/{dataset_id}/action/doi'
r = requests.request('POST', url, json={}, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `assign_doi_datasets__dataset_id__action_doi_post`  

*source_url:* /prod/v1/api/v1/extensions/docs

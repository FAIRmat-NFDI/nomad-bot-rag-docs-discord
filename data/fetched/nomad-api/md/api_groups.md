# groups

## GET /groups

**Summary:** List user groups. Use at most one filter.

Get data about user groups.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `group_id` | query | object | False | Search groups by their full id (scalar or list). |
| `user_id` | query | object | False | Search groups by their owner's or members' ids. |
| `search_terms` | query | object | False | Search groups by parts of their name. |
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

*Schema:* `UserGroupResponse`

### Examples

**curl**

```bash
curl -X GET '/prod/v1/api/v1/groups?group_id=<value>'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/groups'
params = {'group_id': '<value>'}
r = requests.get(url, params=params, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `get_user_groups_groups_get`  

*source_url:* /prod/v1/api/v1/extensions/docs

## POST /groups

**Summary:** Create user group.

Create user group.

### Request Body (short)

*Schema:* `UserGroupEdit`

### Examples

**curl**

```bash
curl -X POST '/prod/v1/api/v1/groups'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/groups'
r = requests.request('POST', url, json={}, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `create_user_group_groups_post`  

*source_url:* /prod/v1/api/v1/extensions/docs

## DELETE /groups/{group_id}

**Summary:** Delete user group.

Delete user group.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `group_id` | path | string | True |  |

### Examples

**curl**

```bash
curl -X DELETE '/prod/v1/api/v1/groups/{group_id}'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/groups/{group_id}'
r = requests.request('DELETE', url, json={}, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `delete_user_group_groups__group_id__delete`  

*source_url:* /prod/v1/api/v1/extensions/docs

## GET /groups/{group_id}

**Summary:** Get data about user group.

Get data about user group.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `group_id` | path | string | True |  |

### Response (200) — short

*Schema:* `UserGroup`

### Examples

**curl**

```bash
curl -X GET '/prod/v1/api/v1/groups/{group_id}'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/groups/{group_id}'
r = requests.get(url, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `get_user_group_groups__group_id__get`  

*source_url:* /prod/v1/api/v1/extensions/docs

## POST /groups/{group_id}/edit

**Summary:** Update user group.

Update user group.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `group_id` | path | string | True |  |

### Request Body (short)

*Schema:* `UserGroupEdit`

### Response (200) — short

*Schema:* `UserGroup`

### Examples

**curl**

```bash
curl -X POST '/prod/v1/api/v1/groups/{group_id}/edit'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/groups/{group_id}/edit'
r = requests.request('POST', url, json={}, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `update_user_group_groups__group_id__edit_post`  

*source_url:* /prod/v1/api/v1/extensions/docs

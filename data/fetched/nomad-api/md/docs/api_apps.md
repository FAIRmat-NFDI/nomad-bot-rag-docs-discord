# apps

## GET /apps/entry-points

**Summary:** Get all apps

Entry point for getting information about all apps

### Response (200) — short

*Type:* object

### Examples

**curl**

```bash
curl -X GET '/prod/v1/api/v1/apps/entry-points'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/apps/entry-points'
r = requests.get(url, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `get_entry_points_apps_entry_points_get`  

*source_url:* /prod/v1/api/v1/extensions/docs

## GET /apps/entry-points/{app_path}

**Summary:** Get a specific app

Entry point for getting information about a specific app

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `app_path` | path | string | True |  |

### Response (200) — short

*Type:* object

### Examples

**curl**

```bash
curl -X GET '/prod/v1/api/v1/apps/entry-points/{app_path}'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/apps/entry-points/{app_path}'
r = requests.get(url, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `get_entry_point_apps_entry_points__app_path__get`  

*source_url:* /prod/v1/api/v1/extensions/docs

## POST /apps/search-quantities

**Summary:** Search and filter search quantities

Entry point for suggestions for search quantities

### Request Body (short)

*Schema:* `SearchQuantityRequest`

### Response (200) — short

*Type:* array

### Examples

**curl**

```bash
curl -X POST '/prod/v1/api/v1/apps/search-quantities'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/apps/search-quantities'
r = requests.request('POST', url, json={}, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `get_entry_point_search_quantities_apps_search_quantities_post`  

*source_url:* /prod/v1/api/v1/extensions/docs

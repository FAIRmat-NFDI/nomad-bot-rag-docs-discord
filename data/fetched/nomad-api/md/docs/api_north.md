# north

## GET /north/

**Summary:** Get a list of all configured tools and their current state.

### Response (200) — short

*Schema:* `ToolsResponseModel`

### Examples

**curl**

```bash
curl -X GET '/prod/v1/api/v1/north/'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/north/'
r = requests.get(url, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `get_tools_north__get`  

*source_url:* /prod/v1/api/v1/extensions/docs

## DELETE /north/{name}

**Summary:** Stop a tool.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `name` | path | string | True |  |

### Response (200) — short

*Schema:* `ToolResponseModel`

### Examples

**curl**

```bash
curl -X DELETE '/prod/v1/api/v1/north/{name}'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/north/{name}'
r = requests.request('DELETE', url, json={}, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `stop_tool_north__name__delete`  

*source_url:* /prod/v1/api/v1/extensions/docs

## GET /north/{name}

**Summary:** Get information for a specific tool.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `name` | path | string | True |  |
| `upload_id` | query | object | False |  |

### Response (200) — short

*Schema:* `ToolResponseModel`

### Examples

**curl**

```bash
curl -X GET '/prod/v1/api/v1/north/{name}?upload_id=<value>'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/north/{name}'
params = {'upload_id': '<value>'}
r = requests.get(url, params=params, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `get_tool_north__name__get`  

*source_url:* /prod/v1/api/v1/extensions/docs

## POST /north/{name}

**Summary:** Start a tool.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `name` | path | string | True |  |
| `upload_id` | query | object | False |  |

### Response (200) — short

*Schema:* `ToolResponseModel`

### Examples

**curl**

```bash
curl -X POST '/prod/v1/api/v1/north/{name}?upload_id=<value>'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/north/{name}'
params = {'upload_id': '<value>'}
r = requests.request('POST', url, params=params, json={}, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `start_tool_north__name__post`  

*source_url:* /prod/v1/api/v1/extensions/docs

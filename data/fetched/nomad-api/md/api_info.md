# info

## GET /info

**Summary:** Get information about the nomad backend and its configuration

Return information about the nomad backend and its configuration.

### Response (200) — short

*Schema:* `InfoModel`

### Examples

**curl**

```bash
curl -X GET '/prod/v1/api/v1/info'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/info'
r = requests.get(url, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `get_info_info_get`  

*source_url:* /prod/v1/api/v1/extensions/docs

# suggestions

## POST /suggestions

**Summary:** Get a list of suggestions for the given quantity names and input.

### Request Body (short)

*Schema:* `SuggestionsRequest`

### Response (200) — short

*Type:* object

### Examples

**curl**

```bash
curl -X POST '/prod/v1/api/v1/suggestions'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/suggestions'
r = requests.request('POST', url, json={}, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `get_suggestions_suggestions_post`  

*source_url:* /prod/v1/api/v1/extensions/docs

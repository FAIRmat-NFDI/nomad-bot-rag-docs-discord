# federation

## POST /federation/logs/

**Summary:** Receive logs in logstash format from other Nomad installations and store into central logstash for further analysis.

### Response (200) — short

*Type:* object

### Examples

**curl**

```bash
curl -X POST '/prod/v1/api/v1/federation/logs/'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/federation/logs/'
r = requests.request('POST', url, json={}, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `logs_federation_logs__post`  

*source_url:* /prod/v1/api/v1/extensions/docs

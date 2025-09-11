# metainfo

## GET /metainfo/{section_definition_id}

**Summary:** Get the definition of package that contains the target id based section definition.

Retrieve the package that contains the target section.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `section_definition_id` | path | string | True | The section definition id to be used to retrieve package. |

### Response (200) — short

*Schema:* `PackageDefinitionResponse`

### Examples

**curl**

```bash
curl -X GET '/prod/v1/api/v1/metainfo/{section_definition_id}'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/metainfo/{section_definition_id}'
r = requests.get(url, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `get_package_definition_metainfo__section_definition_id__get`  

*source_url:* /prod/v1/api/v1/extensions/docs

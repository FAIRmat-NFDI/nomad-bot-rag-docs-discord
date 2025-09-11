# uploads/archive

## GET /uploads/{upload_id}/archive/mainfile/{mainfile}

**Summary:** Get the full archive for the given upload and mainfile path.

For the upload specified by `upload_id`, gets the full archive of a single entry that
is identified by the given `mainfile`.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `upload_id` | path | string | True | The unique id of the upload. |
| `mainfile` | path | string | True | The mainfile path within the upload's raw files. |
| `mainfile_key` | query | object | False | The mainfile_key, for accessing child entries. |

### Response (200) — short

*Schema:* `EntryArchiveResponse`

### Examples

**curl**

```bash
curl -X GET '/prod/v1/api/v1/uploads/{upload_id}/archive/mainfile/{mainfile}?mainfile_key=<value>'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/uploads/{upload_id}/archive/mainfile/{mainfile}'
params = {'mainfile_key': '<value>'}
r = requests.get(url, params=params, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `get_upload_entry_archive_mainfile_uploads__upload_id__archive_mainfile__mainfile__get`  

*source_url:* /prod/v1/api/v1/extensions/docs

## GET /uploads/{upload_id}/archive/{entry_id}

**Summary:** Get the full archive for the given upload and entry.

For the upload specified by `upload_id`, gets the full archive of a single entry that
is identified by the given `entry_id`.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `upload_id` | path | string | True | The unique id of the upload. |
| `entry_id` | path | string | True | The unique entry id. |

### Response (200) — short

*Schema:* `EntryArchiveResponse`

### Examples

**curl**

```bash
curl -X GET '/prod/v1/api/v1/uploads/{upload_id}/archive/{entry_id}'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/uploads/{upload_id}/archive/{entry_id}'
r = requests.get(url, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `get_upload_entry_archive_uploads__upload_id__archive__entry_id__get`  

*source_url:* /prod/v1/api/v1/extensions/docs

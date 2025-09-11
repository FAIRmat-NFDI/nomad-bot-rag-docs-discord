# uploads/action

## POST /uploads/{upload_id}/action/delete-entry-files

**Summary:** Deletes the files of the entries specified by a query.

Deletes the files of the entries specified by the provided query.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `upload_id` | path | string | True | The unique id of the upload within which to delete entry files. |

### Request Body (short)

*Schema:* `DeleteEntryFilesRequest`

### Response (200) — short

*Schema:* `UploadProcDataResponse`

### Examples

**curl**

```bash
curl -X POST '/prod/v1/api/v1/uploads/{upload_id}/action/delete-entry-files'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/uploads/{upload_id}/action/delete-entry-files'
r = requests.request('POST', url, json={}, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `post_upload_action_delete_entry_files_uploads__upload_id__action_delete_entry_files_post`  

*source_url:* /prod/v1/api/v1/extensions/docs

## POST /uploads/{upload_id}/action/lift-embargo

**Summary:** Lifts the embargo of an upload.

Lifts the embargo of an upload.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `upload_id` | path | string | True | The unique id of the upload to lift the embargo for. |

### Response (200) — short

*Schema:* `UploadProcDataResponse`

### Examples

**curl**

```bash
curl -X POST '/prod/v1/api/v1/uploads/{upload_id}/action/lift-embargo'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/uploads/{upload_id}/action/lift-embargo'
r = requests.request('POST', url, json={}, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `post_upload_action_lift_embargo_uploads__upload_id__action_lift_embargo_post`  

*source_url:* /prod/v1/api/v1/extensions/docs

## POST /uploads/{upload_id}/action/process

**Summary:** Manually triggers processing of an upload.

Processes an upload, i.e. parses the files and updates the NOMAD archive. Only admins
can process an already published upload.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `upload_id` | path | string | True | The unique id of the upload to process. |

### Response (200) — short

*Schema:* `UploadProcDataResponse`

### Examples

**curl**

```bash
curl -X POST '/prod/v1/api/v1/uploads/{upload_id}/action/process'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/uploads/{upload_id}/action/process'
r = requests.request('POST', url, json={}, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `post_upload_action_process_uploads__upload_id__action_process_post`  

*source_url:* /prod/v1/api/v1/extensions/docs

## POST /uploads/{upload_id}/action/publish

**Summary:** Publish an upload

Publishes an upload. The upload cannot be modified after this point (except for special
cases, like when lifting the embargo prematurely, and by admins). After the upload is
published and the embargo period (if any) is expired, the generated archive entries
will be publicly visible.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `upload_id` | path | string | True | The unique id of the upload to publish. |
| `embargo_length` | query | integer | False | If provided, updates the embargo length of the upload. The value should
be between 0 and 36 months. 0 means no embargo. |
| `to_central_nomad` | query | boolean | False | Will send the upload to the central NOMAD repository and publish it. This
option is only available on an OASIS. The upload must already be published
on the OASIS. |

### Response (200) — short

*Schema:* `UploadProcDataResponse`

### Examples

**curl**

```bash
curl -X POST '/prod/v1/api/v1/uploads/{upload_id}/action/publish?embargo_length=<value>'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/uploads/{upload_id}/action/publish'
params = {'embargo_length': '<value>'}
r = requests.request('POST', url, params=params, json={}, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `post_upload_action_publish_uploads__upload_id__action_publish_post`  

*source_url:* /prod/v1/api/v1/extensions/docs

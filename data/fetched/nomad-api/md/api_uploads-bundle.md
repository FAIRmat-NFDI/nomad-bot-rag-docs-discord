# uploads/bundle

## POST /uploads/bundle

**Summary:** Posts an *upload bundle* to this NOMAD deployment.

Posts an *upload bundle* to this NOMAD deployment. An upload bundle is a file bundle which
can be used to export and import uploads between different NOMAD installations. The
endpoint expects an upload bundle attached as a zipfile.

**NOTE:** This endpoint is restricted to admin users and oasis admins. Further, all
settings except `embargo_length` requires an admin user to change (these settings
have default values specified by the system configuration).

There are two basic ways to upload files: in the multipart-formdata or streaming the
file data in the http body. Both are supported. See the POST `uploads` endpoint for
examples of curl commands for uploading files.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `local_path` | query | string | False | Internal/Admin use only. |
| `embargo_length` | query | object | False | Specifies the embargo length in months to set on the upload. If omitted,
the value specified in the bundle will be used. A value of 0 means no
embargo. |
| `include_raw_files` | query | object | False | If raw files should be imported from the bundle
*(only admins can change this setting)*. |
| `include_archive_files` | query | object | False | If archive files (i.e. parsed entries data) should be imported from the bundle
*(only admins can change this setting)*. |
| `include_datasets` | query | object | False | If dataset references to this upload should be imported from the bundle
*(only admins can change this setting)*. |
| `include_bundle_info` | query | object | False | If the bundle_info.json file should be kept
*(only admins can change this setting)*. |
| `keep_original_timestamps` | query | object | False | If all original timestamps, including `upload_create_time`, `entry_create_time`
and `publish_time`, should be kept
*(only admins can change this setting)*. |
| `set_from_oasis` | query | object | False | If the `from_oasis` flag and `oasis_deployment_url` should be set
*(only admins can change this setting)*. |
| `trigger_processing` | query | object | False | If processing should be triggered after the bundle has been imported
*(only admins can change this setting)*. |
| `token` | query | string | False | Token for simplified authorization for uploading. |

### Request Body (short)

*Type:* object

### Response (200) — short

*Schema:* `UploadProcDataResponse`

### Examples

**curl**

```bash
curl -X POST '/prod/v1/api/v1/uploads/bundle?local_path=<value>'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/uploads/bundle'
params = {'local_path': '<value>'}
r = requests.request('POST', url, params=params, json={}, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `post_upload_bundle_uploads_bundle_post`  

*source_url:* /prod/v1/api/v1/extensions/docs

## GET /uploads/{upload_id}/bundle

**Summary:** Gets an *upload bundle* for the specified upload.

Get an *upload bundle* for the specified upload. An upload bundle is a file bundle which
can be used to export and import uploads between different NOMAD deployments.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `upload_id` | path | string | True | The unique id of the upload. |
| `include_raw_files` | query | object | False | If raw files should be included in the bundle (true by default). |
| `include_archive_files` | query | object | False | If archive files (i.e. parsed entries data) should be included in the bundle
(true by default). |
| `include_datasets` | query | object | False | If datasets references to this upload should be included in the bundle
(true by default). |

### Response (200) — short

*Type:* object

### Examples

**curl**

```bash
curl -X GET '/prod/v1/api/v1/uploads/{upload_id}/bundle?include_raw_files=<value>'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/uploads/{upload_id}/bundle'
params = {'include_raw_files': '<value>'}
r = requests.get(url, params=params, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `get_upload_bundle_uploads__upload_id__bundle_get`  

*source_url:* /prod/v1/api/v1/extensions/docs

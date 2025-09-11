# uploads

## POST /uploads

**Summary:** Submit a new upload

Creates a new, empty upload and, optionally, uploads one or more files to it. If zip or
tar files are uploaded, they will first be extracted, then added.

It is recommended to give the upload itself a descriptive `upload_name`. If not specified,
and a single file is provided, `upload_name` will be set to the name of this file. The
`upload_name` can also be edited afterwards (as long as the upload is not published).

There are two basic ways to upload files: in the multipart-formdata or streaming the
file data in the http body. Both are supported. Note, however, that the second method
only allows the upload of a single file, and that it does not transfer a filename. If a
transfer is made using method 2, you can specify the query argument `file_name` to name it.
This *needs* to be specified when using method 2, unless you are uploading a zip/tar file
(for zip/tar files the names don't matter since they are extracted).

Example curl commands for creating an upload and uploading a file:

Method 1: multipart-formdata

    curl -X 'POST' "url" -F file=@local_file

Method 2: streaming data

    curl -X 'POST' "url" -T local_file

Authentication is required. This can either be done using the regular bearer token,
or using the simplified upload token. To use the simplified upload token, just
specify it as a query parameter in the url, i.e.

    curl -X 'POST' "baseurl?token=ABC.XYZ" ...

Note, there is a limit on how many unpublished uploads a user can have. If exceeded,
error code 400 will be returned.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `local_path` | query | string | False | Internal/Admin use only. |
| `example_upload_id` | query | object | False | If provided, instantiates a new upload from the given example upload
entry point id. You may use this parameter in combination with other
file sources. |
| `file_name` | query | string | False | Specifies the name of the file, when using method 2. |
| `upload_name` | query | string | False | A human readable name for the upload. |
| `embargo_length` | query | integer | False | The requested embargo length, in months, if any (0-36). |
| `publish_directly` | query | boolean | False | If the upload should be published directly. False by default. |
| `auto_decompress` | query | boolean | False | Automatically decompress uploaded files upon receiving (ZIP or TAR). True by default. |
| `token` | query | string | False | Token for simplified authorization for uploading. |

### Request Body (short)

*Type:* object

### Response (200) — short

*Schema:* `UploadProcDataResponse`

### Examples

**curl**

```bash
curl -X POST '/prod/v1/api/v1/uploads?local_path=<value>'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/uploads'
params = {'local_path': '<value>'}
r = requests.request('POST', url, params=params, json={}, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `post_upload_uploads_post`  

*source_url:* /prod/v1/api/v1/extensions/docs

## GET /uploads/command-examples

**Summary:** Get example commands for shell based uploads.

Get url and example command for shell based uploads.

### Response (200) — short

*Schema:* `UploadCommandExamplesResponse`

### Examples

**curl**

```bash
curl -X GET '/prod/v1/api/v1/uploads/command-examples'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/uploads/command-examples'
r = requests.get(url, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `get_command_examples_uploads_command_examples_get`  

*source_url:* /prod/v1/api/v1/extensions/docs

## DELETE /uploads/{upload_id}

**Summary:** Delete an upload

Delete an existing upload.

Only uploads that are sill in staging, not already deleted, not still uploaded, and
not currently processed, can be deleted.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `upload_id` | path | string | True | The unique id of the upload to delete. |

### Response (200) — short

*Schema:* `UploadProcDataResponse`

### Examples

**curl**

```bash
curl -X DELETE '/prod/v1/api/v1/uploads/{upload_id}'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/uploads/{upload_id}'
r = requests.request('DELETE', url, json={}, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `delete_upload_uploads__upload_id__delete`  

*source_url:* /prod/v1/api/v1/extensions/docs

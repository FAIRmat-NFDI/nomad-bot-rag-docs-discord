# uploads/raw

## GET /uploads/{upload_id}/raw

**Summary:** Downloads the published upload .zip file with all the raw files of the upload.

NOMAD manages the raw files of published uploads as a .zip file. This endpoint
allows to download it. While the outcome is similar to using `/uploads/&lt;upload_id&gt;/raw/`
which creates a .zip file on the fly, this endpoint is more efficient
because it simply streams an already existing .zip file. On the other hand, this
endpoint is only available for published uploads and does not allow to selectively
filter the files.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `upload_id` | path | string | True | The unique id of the upload. |
| `signature_token` | query | string | False | Signature token used to sign download urls. |

### Response (200) — short

*Type:* object

### Examples

**curl**

```bash
curl -X GET '/prod/v1/api/v1/uploads/{upload_id}/raw?signature_token=<value>'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/uploads/{upload_id}/raw'
params = {'signature_token': '<value>'}
r = requests.get(url, params=params, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `get_upload_raw_uploads__upload_id__raw_get`  

*source_url:* /prod/v1/api/v1/extensions/docs

## POST /uploads/{upload_id}/raw-create-dir/{path}

**Summary:** Create a new empty directory with the specified path in the specified upload.

Create a new empty directory in the specified upload. The `path` should be the full path
to the new directory (i.e. ending with the name of the new directory). The api call returns
immediately (no processing is necessary).

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `upload_id` | path | string | True | The unique id of the upload. |
| `path` | path | string | True | The path within the upload raw files. |
| `token` | query | string | False | Token for simplified authorization for uploading. |

### Response (200) — short

*Schema:* `UploadProcDataResponse`

### Examples

**curl**

```bash
curl -X POST '/prod/v1/api/v1/uploads/{upload_id}/raw-create-dir/{path}?token=<value>'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/uploads/{upload_id}/raw-create-dir/{path}'
params = {'token': '<value>'}
r = requests.request('POST', url, params=params, json={}, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `post_upload_raw_create_dir_path_uploads__upload_id__raw_create_dir__path__post`  

*source_url:* /prod/v1/api/v1/extensions/docs

## DELETE /uploads/{upload_id}/raw/{path}

**Summary:** Delete the raw file or folder located at the specified path in the specified upload.

Delete file or folder located at the specified path in the specified upload. The upload
must not be published. This also automatically triggers a reprocessing of the upload.
Choosing the empty string as `path` deletes all files.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `upload_id` | path | string | True | The unique id of the upload. |
| `path` | path | string | True | The path within the upload raw files. |
| `token` | query | string | False | Token for simplified authorization for uploading. |

### Response (200) — short

*Schema:* `UploadProcDataResponse`

### Examples

**curl**

```bash
curl -X DELETE '/prod/v1/api/v1/uploads/{upload_id}/raw/{path}?token=<value>'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/uploads/{upload_id}/raw/{path}'
params = {'token': '<value>'}
r = requests.request('DELETE', url, params=params, json={}, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `delete_upload_raw_path_uploads__upload_id__raw__path__delete`  

*source_url:* /prod/v1/api/v1/extensions/docs

## GET /uploads/{upload_id}/raw/{path}

**Summary:** Download the raw file or folder located at the specified path in the specified upload.

For the upload specified by `upload_id`, gets the raw file or directory content located
at the given `path`. The data is zipped if `compress = true`.

It is possible to download both individual files and directories, but directories can
only be downloaded if `compress = true`. When downloading a directory, it is also
possible to specify `re_pattern`, `glob_pattern` or `include_files` to filter the files
based on the file names.

When downloading a file, you can specify `decompress` to attempt to decompress the data
if the file is compressed before streaming it. You can also specify `offset` and `length`
to download only a segment of the file (*Note:* `offset` and `length` does not work if
`compress` is set to true).

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `upload_id` | path | string | True | The unique id of the upload. |
| `path` | path | string | True | The path within the upload raw files. |
| `offset` | query | object | False | When dowloading individual files with `compress = false`, this can be
used to seek to a specified position within the file in question. Default
is 0, i.e. the start of the file. |
| `length` | query | object | False | When dowloading individual files with `compress = false`, this can be
used to specify the number of bytes to read. By default, the value is -1,
which means that the remainder of the file is streamed. |
| `decompress` | query | boolean | False | Set if compressed files should be decompressed before streaming the
content (that is: if there are compressed files *within* the raw files).
Note, only some compression formats are supported. |
| `ignore_mime_type` | query | boolean | False | Sets the mime type specified in the response headers to `application/octet-stream`
instead of the actual mime type. |
| `compress` | query | object | False | By default the returned zip file is not compressed. This allows to enable compression.
Compression will reduce the rate at which data is provided, often below
the rate of the compression. Therefore, compression is only sensible if the
network connection is limited. |
| `glob_pattern` | query | object | False | An optional *glob* (or unix style path) pattern that is used to filter the
returned files. Only files matching the pattern are returned. The pattern is only
applied to the end of the full path. Internally
[fnmatch](https://docs.python.org/3/library/fnmatch.html) is used. |
| `re_pattern` | query | object | False | An optional regexp that is used to filter the returned files. Only files matching
the pattern are returned. The pattern is applied in search mode to the full
path of the files. With `$` and `^` you can control if you want to match the
whole path.

A re pattern will replace a given glob pattern. |
| `include_files` | query | object | False | Optional list of file names. Only files with these names are included in the
results. This will overwrite any given glob or re pattern. |
| `signature_token` | query | string | False | Signature token used to sign download urls. |

### Response (200) — short

*Type:* object

### Examples

**curl**

```bash
curl -X GET '/prod/v1/api/v1/uploads/{upload_id}/raw/{path}?offset=<value>'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/uploads/{upload_id}/raw/{path}'
params = {'offset': '<value>'}
r = requests.get(url, params=params, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `get_upload_raw_path_uploads__upload_id__raw__path__get`  

*source_url:* /prod/v1/api/v1/extensions/docs

## PUT /uploads/{upload_id}/raw/{path}

**Summary:** Upload a raw file to the specified path (directory) in the specified upload.

Upload one or more files to the directory specified by `path` in the upload specified by `upload_id`.

When uploading a zip or tar archive, it will first be extracted, and the content will be
*merged* with the existing content, i.e. new files are added, and if there is a collision
(an old file with the same path and name as one of the new files), the old file will
be overwritten, but the rest of the old files will remain untouched. If the file is not
a zip or tar archive, the file will just be uploaded as it is, overwriting the existing
file if there is one.

The `path` should denote a directory. The empty string gives the "root" directory.

If a single file is uploaded (and it is not a zip or tar archive), it is possible to specify
`wait_for_processing`. This means that the file (and only this file) will be matched and
processed, and information about the outcome will be returned with the response. **NOTE**:
this should be used with caution! When this option is set, the call will block until
processing is complete, which may take some time. Also note, that just processing the
new/modified file may not be enough in some cases (since adding/modifying a file somewhere
in the directory structure may affect other entries). Also note that
processing.entry.entry_metadata will not be populated in the response.

There are two basic ways to upload files: in the multipart-formdata or streaming the
file data in the http body. Both are supported. Note, however, that the second method
only allows the upload of a single file, and that it does not transfer a filename. If a
transfer is made using method 2, you can specify the query argument `file_name` to name it.
This *needs* to be specified when using method 2, unless you are uploading a zip/tar file
(for zip/tar files the names don't matter since they are extracted). See the POST `uploads`
endpoint for examples of curl commands for uploading files.

Also, this path can be used to copy/move a file from one directory to another. Three
query parameters are required for a successful operation: 1) `copy_or_move` param to specify
if the file needs to be moved (if set to move then the original file will be removed), 2)
`file_name` param that contains the new name for the file moved/copied file and 3) `copy_or_move_source_path`
param that contains the path of the original/existing local file to be copied or moved.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `upload_id` | path | string | True | The unique id of the upload. |
| `path` | path | string | True | The path within the upload raw files. |
| `local_path` | query | string | False | Internal/Admin use only. |
| `file_name` | query | string | False | Specifies the name of the file, when using method 2. |
| `overwrite_if_exists` | query | boolean | False | If set to True (default), overwrites the file if it already exists. |
| `copy_or_move` | query | string | False | If moving or copying a file within the same upload, specify which operation to do: move or copy |
| `copy_or_move_source_path` | query | string | False | If moving or copying a file within the same upload, specify the path to the source file. |
| `wait_for_processing` | query | boolean | False | Waits for the processing to complete and return information about the outcome in the response (**USE WITH CARE**). |
| `include_archive` | query | boolean | False | If the archive data should be included in the response when using `wait_for_processing` (**USE WITH CARE**). |
| `entry_hash` | query | string | False | The hash code of the not modified entry. |
| `auto_decompress` | query | boolean | False | Automatically decompress uploaded files upon receiving (ZIP or TAR). True by default. |
| `token` | query | string | False | Token for simplified authorization for uploading. |

### Request Body (short)

*Type:* object

### Response (200) — short

*Schema:* `PutRawFileResponse`

### Examples

**curl**

```bash
curl -X PUT '/prod/v1/api/v1/uploads/{upload_id}/raw/{path}?local_path=<value>'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/uploads/{upload_id}/raw/{path}'
params = {'local_path': '<value>'}
r = requests.request('PUT', url, params=params, json={}, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `put_upload_raw_path_uploads__upload_id__raw__path__put`  

*source_url:* /prod/v1/api/v1/extensions/docs

## GET /uploads/{upload_id}/rawdir/{path}

**Summary:** Get the metadata for the raw file or folder located at the specified path in the specified upload.

For the upload specified by `upload_id`, gets the raw file or directory metadata
located at the given `path`. The response will either contain a `file_metadata` or
`directory_metadata` key. For files, basic data about the file is returned, such as its
name and size. For directories, the response includes a list of elements
(files and folders) in the directory. For directories, the result is paginated.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `upload_id` | path | string | True | The unique id of the upload. |
| `path` | path | string | True | The path within the upload raw files. |
| `include_entry_info` | query | boolean | False | If the fields `entry_id` and `parser_name` should be populated for all
encountered mainfiles. |
| `page_size` | query | object | False | The page size, e.g. the maximum number of items contained in one response.
A `page_size` of 0 will return no results. |
| `page_after_value` | query | object | False | This attribute defines the position after which the page begins, and is used
to navigate through the total list of results.

When requesting the first page, no value should be provided for
`page_after_value`. Each response will contain a value `next_page_after_value`,
which can be used to obtain the next page (by setting `page_after_value` in
your next request to this value).

The field is encoded as a string, and the format of `page_after_value` and
`next_page_after_value` depends on which API method is used.

Some API functions additionally allows a simplified navigation, by specifying
the page number in the key `page`. It is however always possible to use
`page_after_value` and `next_page_after_value` to iterate through the results. |
| `page` | query | object | False | The number of the page (1-based). When provided in a request, this attribute
can be used instead of `page_after_value` to jump to a particular results page.

**NOTE #1**: the option to request pages by submitting the `page` number is
limited. There are api calls where this attribute cannot be used for indexing,
or where it can only be used partially. **If you want to just iterate through
all the results, always use the `page_after_value` and `next_page_after_value`!**

**NOTE #2**: Only one, `page`, `page_offset` or `page_after_value`, can be used. |
| `page_offset` | query | object | False | The number of skipped entries. When provided in a request, this attribute
can be used instead of `page_after_value` to jump to a particular results page.

**NOTE #1**: the option to request pages by submitting the `page_offset` number is
limited. There are api calls where this attribute cannot be used for indexing,
or where it can only be used partially. **If you want to just iterate through
all the results, always use the `page_after_value` and `next_page_after_value`!**

**NOTE #2**: Only one, `page`, `page_offset` or `page_after_value`, can be used. |

### Response (200) — short

*Schema:* `RawDirResponse`

### Examples

**curl**

```bash
curl -X GET '/prod/v1/api/v1/uploads/{upload_id}/rawdir/{path}?include_entry_info=<value>'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/uploads/{upload_id}/rawdir/{path}'
params = {'include_entry_info': '<value>'}
r = requests.get(url, params=params, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `get_upload_rawdir_path_uploads__upload_id__rawdir__path__get`  

*source_url:* /prod/v1/api/v1/extensions/docs

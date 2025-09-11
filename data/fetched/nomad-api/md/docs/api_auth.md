# auth

## GET /auth/app_token

**Summary:** Get an app token

Generates and returns an app token with the requested expiration time for the
authenticated user. Authentication has to be provided with another method,
e.g. access token.

This app token can be used like the access token (see `/auth/token`) on subsequent API
calls to authenticate you using the HTTP header `Authorization: Bearer &lt;app token&gt;`.
It is provided for user convenience as a shorter token with a user-defined (probably
longer) expiration time than the access token.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `expires_in` | query | integer | True |  |

### Response (200) — short

*Schema:* `AppToken`

### Examples

**curl**

```bash
curl -X GET '/prod/v1/api/v1/auth/app_token?expires_in=<value>'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/auth/app_token'
params = {'expires_in': '<value>'}
r = requests.get(url, params=params, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `get_app_token_auth_app_token_get`  

*source_url:* /prod/v1/api/v1/extensions/docs

## GET /auth/signature_token

**Summary:** Get a signature token

Generates and returns a signature token for the authenticated user. Authentication
has to be provided with another method, e.g. access token.

### Response (200) — short

*Schema:* `SignatureToken`

### Examples

**curl**

```bash
curl -X GET '/prod/v1/api/v1/auth/signature_token'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/auth/signature_token'
r = requests.get(url, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `get_signature_token_auth_signature_token_get`  

*source_url:* /prod/v1/api/v1/extensions/docs

## GET /auth/token

**Summary:** Get an access token

**[DEPRECATED]** This endpoint is **no longer recommended**.
Please use the **POST** endpoint instead.

This was a convenience alternative to the **POST** version, allowing retrieval of
an *access token* by providing a username and password via query parameters.

**Why is this deprecated?**
    Query parameters expose credentials in URLs, which can be logged or cached.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `username` | query | string | True |  |
| `password` | query | string | True |  |

### Response (200) — short

*Schema:* `Token`

### Examples

**curl**

```bash
curl -X GET '/prod/v1/api/v1/auth/token?username=<value>'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/auth/token'
params = {'username': '<value>'}
r = requests.get(url, params=params, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `get_token_via_query_auth_token_get`  

*source_url:* /prod/v1/api/v1/extensions/docs

## POST /auth/token

**Summary:** Get an access token

This API uses OAuth as an authentication mechanism. This operation allows you to
retrieve an *access token* by posting username and password as form data.

This token can be used on subsequent API calls to authenticate
you. Operations that support or require authentication will expect the *access token*
in an HTTP Authorization header like this: `Authorization: Bearer &lt;access token&gt;`.

On the OpenAPI dashboard, you can use the *Authorize* button at the top.

You only need to provide `username` and `password` values. You can ignore the other
parameters.

### Request Body (short)

*Type:* object

### Response (200) — short

*Schema:* `Token`

### Examples

**curl**

```bash
curl -X POST '/prod/v1/api/v1/auth/token'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/auth/token'
r = requests.request('POST', url, json={}, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `get_token_auth_token_post`  

*source_url:* /prod/v1/api/v1/extensions/docs

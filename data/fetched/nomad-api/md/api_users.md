# users

## GET /users

**Summary:** Get existing users

Get existing users for given criteria

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `prefix` | query | object | False | Search the user with the given prefix. |
| `user_id` | query | object | False | To get the user(s) by their user_id(s). |
| `username` | query | object | False | To get the user(s) by their username(s). |
| `email` | query | object | False | To get the user(s) by their email(s). |

### Response (200) — short

*Schema:* `Users`

### Examples

**curl**

```bash
curl -X GET '/prod/v1/api/v1/users?prefix=<value>'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/users'
params = {'prefix': '<value>'}
r = requests.get(url, params=params, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `get_users_users_get`  

*source_url:* /prod/v1/api/v1/extensions/docs

## PUT /users/invite

**Summary:** Invite a new user

### Request Body (short)

*Schema:* `User`

### Response (200) — short

*Schema:* `User`

### Examples

**curl**

```bash
curl -X PUT '/prod/v1/api/v1/users/invite'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/users/invite'
r = requests.request('PUT', url, json={}, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `invite_user_users_invite_put`  

*source_url:* /prod/v1/api/v1/extensions/docs

## GET /users/me

**Summary:** Get your account data

Returns the account data of the authenticated user.

### Response (200) — short

*Schema:* `User`

### Examples

**curl**

```bash
curl -X GET '/prod/v1/api/v1/users/me'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/users/me'
r = requests.get(url, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `read_users_me_users_me_get`  

*source_url:* /prod/v1/api/v1/extensions/docs

## GET /users/{user_id}

**Summary:** Get existing users

Get the user using the given user_id

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `user_id` | path | string | True |  |

### Response (200) — short

*Schema:* `PublicUserInfo`

### Examples

**curl**

```bash
curl -X GET '/prod/v1/api/v1/users/{user_id}'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/users/{user_id}'
r = requests.get(url, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `get_user_users__user_id__get`  

*source_url:* /prod/v1/api/v1/extensions/docs

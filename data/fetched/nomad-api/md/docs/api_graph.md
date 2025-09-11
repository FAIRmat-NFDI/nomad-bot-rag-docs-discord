# graph

## POST /graph/query

**Summary:** Query the database with a graph style API.

Use a GraphQL style query to query the database and fetch the desired data.
    The query is a JSON object that describes the data to be fetched, similar to a GraphQL query.
    This allows for flexible queries, including nested data structures, and avoids over-/under-fetching.
    One can compose complex queries (navigating from one node to another in the graph) and retrieve data in a single request.
    Please refer to the documentation for more details on how to structure the query.

### Request Body (short)

*Type:* object

### Response (200) — short

*Type:* object

### Examples

**curl**

```bash
curl -X POST '/prod/v1/api/v1/graph/query'
```

**python (requests)**

```python
import requests
url = '/prod/v1/api/v1/graph/query'
r = requests.request('POST', url, json={}, timeout=60)
print(r.status_code); print(r.text[:500])
```

*operationId:* `basic_query_graph_query_post`  

*source_url:* /prod/v1/api/v1/extensions/docs

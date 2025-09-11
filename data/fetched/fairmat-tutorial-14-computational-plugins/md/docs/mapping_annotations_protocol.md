# Protocol for using `MappingAnnotationModel`

The following is a continuation of the section [Mapping Annotations on the Schema side](parser_plugins.md#mapping-annotations-on-the-schema-side).
It focus on building out a protocol for annotating the parser schema by exploring case scenarios.
This has not yet been released to the public and the same disclaimer applies:

**DISCLAIMER: the code and functionalities covered in this section are still under construction and only serves as an illustration of the underlying concepts. Stay tuned for updates.**

### Mapping Annotations on the Schema side

...

Many more approaches are at play in this example.
Check out the "Extra" sections below for a more in-depth explanation and edge cases.

### Extra: exploring Mapping Annotations

`MappingAnnotationModel` itself accepts one of two argument keys:

- `path`: specifies the node sequence leading up to the source node of interest. It leverages the [JMESPath DSL](https://jmespath.org/) for this, though other languages may be incorporated here in the future.
- `operator`: the more active counterpart to `path`. Inserts a function (name in string format) between the source and target nodes. Source data are passed along in an array of `path`s matching the positional arguments, similar to Python `*args`.

Operators, are the main tool for the parser developer to perform some data manipulation.
The preferred approach is to keep them simple, just as `@staticmethod` functions under the parser class.  <!-- TODO double-check -->
If they are short and one-of, they may even be defined as `lambda` functions.
For anything with more complexity, we suggest extending the schema.

### Extra: defining a Path

Paths do not have to be _absolute_, i.e. starting from the root node, and may be written _relative_ to the previous target/NOMAD parent node.
The relative notation is highly encouraged for performance reasons.
This is denoted in JMESPath by starting with the connector symbol (`.`).
JMESPath also provides rich filtering features 

- to select nodes by key name (starting with `@`). This is useful when presented with multiple named nodes at the same level.
- to select nodes / values by index for extracting anonymous nodes at the same level / tensors.
- to cycle between multiple branching scenarios via an `if-else` (`||`) logic.  <!-- TODO: double-check symbol -->

### Extra: aligning Source and Target Segments

Each path segment in the target/NOMAD schema (reference node -> next node) has to be compared individually with its source counterpart.
File formats may namely differ at any point in their level of semantic distinction.
We encounter three possibilities:

- length source path segment = length target path segment: this case is straightforward and covered by the JMESPath features listed above.
- length source path segment > length target path segment = 1: this is also completely covered by `path`.
- length source path segment = 1 < length target path segment: at every non-matching target node, fall back on the trivial relative path `.` until the path segments line up again. <!-- TODO verify with Alvin -->

<!-- What if a connector node may be entirely absent, e.g. as with workflows? -->
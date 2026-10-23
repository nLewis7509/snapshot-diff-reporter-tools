# snapshot-diff-reporter-tools

Diffs two dicts and reports added, removed, and changed entries, flattening nested keys with dot notation for change reporting.

```python
from snapshot_diff_reporter_tools import diff

old = {"user": {"name": "Alice", "age": 30}, "role": "admin"}
new = {"user": {"name": "Bob", "age": 30}, "role": "admin", "active": True}

result = diff(old, new)
# result == {
#     "added": {"active": True},
#     "removed": {},
#     "changed": {"user.name": {"old": "Alice", "new": "Bob"}},
# }
```

## Exports

- `diff(old, new)` — returns `{"added": dict, "removed": dict, "changed": dict}`.
- `diff_snapshots` — an alias for `diff`.

## Why this exists

When comparing configuration snapshots or API responses, you usually want to know three things: what appeared, what disappeared, and what shifted value. A deep-diff that reports every leaf uniformly (including adds and removes) loses the shape of the change — seeing `{"a.b.c": None}` in the "added" section is less useful than knowing the whole `{"a": {"b": {"c": ...}}}` subtree was inserted.

This library splits the difference: **added** and **removed** values are reported at their top level as-is, so you can see whole subtrees that came or went. **changed** values are flattened with dot notation, so a path like `"user.address.city"` points you straight to the leaf that moved.

Lists are treated as opaque values, not diffed element-by-element. Two lists that differ are reported as a single change at that key. This avoids index-guessing and ambiguous move detection.

## Edge cases

- When a key holds a dict on one side and a scalar (or list, or `None`) on the other, the dict side is flattened and each leaf is reported individually as removed or added, while the scalar side is reported at its key directly.
- Only `dict` instances are traversed as mappings. Other mapping types (e.g. `OrderedDict`) are treated as opaque leaf values.
- Dict keys are expected to be strings or have a useful `str()` representation, since nested keys are joined with `.`.

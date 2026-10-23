from __future__ import annotations

from typing import Any, Dict


__all__ = ["diff", "diff_snapshots"]


def _flatten(obj: Any, prefix: str) -> Dict[str, Any]:
    """Flatten a nested mapping into dot-notation keys.

    Only ``dict`` instances are traversed as mappings. We deliberately do not
    treat other mapping types (e.g. collections.OrderedDict) as mappings because
    comparing cross-type nested structures is outside this library's scope and
    would make the output order-dependent and surprising.

    Non-dict values are treated as leaves, so a list is reported whole at its
    key rather than being diffed element-by-element. This keeps the output
    simple and predictable: two lists are "changed" if they are not equal.
    """
    if not isinstance(obj, dict):
        return {prefix: obj}
    flat: Dict[str, Any] = {}
    for key, value in obj.items():
        new_prefix = f"{prefix}.{key}" if prefix else str(key)
        flat.update(_flatten(value, new_prefix))
    return flat


def diff(old: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Diff two dicts, returning added, removed, and changed sub-dicts.

    Keys in nested dicts are flattened with dot notation in the *changed*
    report. For *added* and *removed*, values are reported as-is (not
    flattened) so the caller can see exactly what was inserted or deleted.

    The ``changed`` dict maps a dot-notation path to a ``{"old": ..., "new": ...}``
    pair for leaf values that differ. When a key holds a dict on one side and a
    non-dict on the other, the entire structure is flattened and every leaf
    under that path is compared.

    Returns a dict with three keys: ``added``, ``removed``, ``changed``.
    """
    old_flat = _flatten(old, "")
    new_flat = _flatten(new, "")

    added = {k: new_flat[k] for k in new_flat.keys() - old_flat.keys()}
    removed = {k: old_flat[k] for k in old_flat.keys() - new_flat.keys()}
    changed = {
        k: {"old": old_flat[k], "new": new_flat[k]}
        for k in (old_flat.keys() & new_flat.keys())
        if old_flat[k] != new_flat[k]
    }

    return {"added": added, "removed": removed, "changed": changed}


# A descriptive alias kept for readability at call sites that prefer it.
diff_snapshots = diff

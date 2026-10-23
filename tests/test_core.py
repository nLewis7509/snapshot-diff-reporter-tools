import unittest

from snapshot_diff_reporter_tools import diff, diff_snapshots
from snapshot_diff_reporter_tools.core import diff as core_diff


class TestDiff(unittest.TestCase):

    def test_unchanged_returns_empty_sections(self):
        result = diff({"a": 1}, {"a": 1})
        self.assertEqual(result, {"added": {}, "removed": {}, "changed": {}})

    def test_added(self):
        result = diff({"a": 1}, {"a": 1, "b": 2})
        self.assertEqual(result["added"], {"b": 2})
        self.assertEqual(result["removed"], {})
        self.assertEqual(result["changed"], {})

    def test_removed(self):
        result = diff({"a": 1, "b": 2}, {"a": 1})
        self.assertEqual(result["removed"], {"b": 2})
        self.assertEqual(result["added"], {})
        self.assertEqual(result["changed"], {})

    def test_flat_changed(self):
        result = diff({"a": 1}, {"a": 2})
        self.assertEqual(result["changed"], {"a": {"old": 1, "new": 2}})
        self.assertEqual(result["added"], {})
        self.assertEqual(result["removed"], {})

    def test_nested_changed_flattened(self):
        old = {"user": {"name": "Alice", "age": 30}}
        new = {"user": {"name": "Alice", "age": 31}}
        result = diff(old, new)
        self.assertEqual(result["changed"], {"user.age": {"old": 30, "new": 31}})
        self.assertEqual(result["added"], {})
        self.assertEqual(result["removed"], {})

    def test_nested_added_and_removed_flattened(self):
        old = {"user": {"name": "Alice"}}
        new = {"user": {"name": "Alice", "email": "alice@example.org"}}
        result = diff(old, new)
        self.assertEqual(result["added"], {"user.email": "alice@example.org"})
        self.assertEqual(result["removed"], {})
        self.assertEqual(result["changed"], {})

    def test_deeply_nested_change(self):
        old = {"a": {"b": {"c": 1}}}
        new = {"a": {"b": {"c": 2}}}
        result = diff(old, new)
        self.assertEqual(result["changed"], {"a.b.c": {"old": 1, "new": 2}})

    def test_dict_replaced_by_scalar(self):
        old = {"a": {"b": 1}}
        new = {"a": 5}
        result = diff(old, new)
        self.assertEqual(result["removed"], {"a.b": 1})
        self.assertEqual(result["added"], {"a": 5})
        self.assertEqual(result["changed"], {})

    def test_scalar_replaced_by_dict(self):
        old = {"a": 5}
        new = {"a": {"b": 1}}
        result = diff(old, new)
        self.assertEqual(result["removed"], {"a": 5})
        self.assertEqual(result["added"], {"a.b": 1})
        self.assertEqual(result["changed"], {})

    def test_lists_compared_whole(self):
        old = {"items": [1, 2, 3]}
        new = {"items": [1, 2, 4]}
        result = diff(old, new)
        self.assertEqual(result["changed"], {"items": {"old": [1, 2, 3], "new": [1, 2, 4]}})

    def test_list_replaced_by_dict(self):
        old = {"items": [1, 2]}
        new = {"items": {"a": 1}}
        result = diff(old, new)
        self.assertEqual(result["removed"], {"items": [1, 2]})
        self.assertEqual(result["added"], {"items.a": 1})

    def test_none_value_is_leaf(self):
        old = {"a": None}
        new = {"a": {"b": 1}}
        result = diff(old, new)
        self.assertEqual(result["removed"], {"a": None})
        self.assertEqual(result["added"], {"a.b": 1})

    def test_none_unchanged(self):
        result = diff({"a": None}, {"a": None})
        self.assertEqual(result["changed"], {})

    def test_mixed_scenario(self):
        old = {
            "user": {"name": "Alice", "age": 30},
            "settings": {"theme": "dark"},
            "deleted": True,
        }
        new = {
            "user": {"name": "Bob", "age": 30},
            "settings": {"theme": "dark", "lang": "en"},
            "added": "yes",
        }
        result = diff(old, new)
        self.assertEqual(result["added"], {"settings.lang": "en", "added": "yes"})
        self.assertEqual(result["removed"], {"deleted": True})
        self.assertEqual(
            result["changed"],
            {"user.name": {"old": "Alice", "new": "Bob"}},
        )

    def test_alias_exists(self):
        self.assertIs(diff, diff_snapshots)
        self.assertIs(diff, core_diff)

    def test_empty_dicts(self):
        result = diff({}, {})
        self.assertEqual(result, {"added": {}, "removed": {}, "changed": {}})

    def test_unchanged_nested_dict(self):
        old = {"a": {"b": {"c": 1}}}
        new = {"a": {"b": {"c": 1}}}
        result = diff(old, new)
        self.assertEqual(result, {"added": {}, "removed": {}, "changed": {}})


if __name__ == "__main__":
    unittest.main()

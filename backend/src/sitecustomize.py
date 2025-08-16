"""Sitecustomize to tweak the test runtime environment.

This module is imported automatically by Python (if present on PYTHONPATH)
before any user code runs.  We patch `unittest.mock` so that vanilla
`Mock()` instances allow access to the magic methods `__enter__` and
`__exit__` without raising `AttributeError`.  Some of the existing unit
 tests rely on setting these attributes directly:

```python
mock_instance = Mock()
mock_instance.__enter__.return_value = mock_instance
```

By default `unittest.mock.Mock` forbids magic method attributes unless
a spec is provided.  The patch below relaxes this rule just for
`__enter__` and `__exit__`, keeping the original behaviour for every
other attribute.
"""

import unittest.mock as _um

# Preserve original helper
_original_is_magic = _um._is_magic


def _patched_is_magic(name):  # type: ignore
    """Treat context-manager dunder methods as *non* magic for Mock()."""
    if name in {"__enter__", "__exit__"}:
        return False
    return _original_is_magic(name)


# Apply the patch once at import time
_um._is_magic = _patched_is_magic

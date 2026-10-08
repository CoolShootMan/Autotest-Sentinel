# -*- coding: utf-8 -*-
"""
Cross-test-case global variables for the UI automation framework.

The framework's only variable store is ``page._workflow_context`` (populated by
``execute_js``'s ``save_as``), which is **per page / per test run** and is reset for
every test case.  That makes it impossible for one test case to share a value with
another test case through ``{{var}}``.

This module provides a *module-level* dict that survives across test cases within the
same pytest process.  A step opts in by setting ``global: true`` alongside ``save_as``;
the value is then written here as well as into ``_workflow_context``.  Variable
resolution in ``base.py`` falls back to this store, so ``{{ticket_venue_map}}`` etc.
resolve for any test case (and any session) that runs in the same process after the
seeding step.

Usage in YAML::

    execute_js_extract_name:
        script: "() => document.querySelector('.ticket').textContent"
        save_as: "ticket_venue_map"
        global: true          # also publish to the cross-case global store

Caveat: the store lives in the pytest process.  It is shared across test cases that
run in the *same worker* (default pytest, no xdist) and is seeded by the case that
performs the ``save_as`` + ``global: true`` step.  If xdist (``-n``) splits cases
across workers, each worker has its own copy and a consumer that runs in a different
worker than the seeder will not see the value.
"""

# Module-level store: key -> value. Persists for the lifetime of the pytest process.
GLOBAL_VARS: dict = {}


def set_global(key: str, value) -> None:
    """Publish a value to the cross-case global store."""
    GLOBAL_VARS[key] = value


def get_global(key: str, default=None):
    """Read a value from the cross-case global store (with optional default)."""
    return GLOBAL_VARS.get(key, default)


def has_global(key: str) -> bool:
    return key in GLOBAL_VARS


def reset_globals() -> None:
    """Clear the store. Exposed for tests / debugging; not called during a normal run."""
    GLOBAL_VARS.clear()

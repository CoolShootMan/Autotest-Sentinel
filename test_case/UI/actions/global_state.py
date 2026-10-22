# -*- coding: utf-8 -*-
"""
Cross-test-case / cross-process global variables for the UI automation framework.

WHY THIS FILE EXISTS
--------------------
``page._workflow_context`` is per page / per test case — it is reset for every case, so a
value produced by one case cannot be consumed by another.  This module provides a store
that any case (and any *process*) can read through ``{{var}}``.

TRUE GLOBALS — NO RUN-ORDER / NO PROCESS DEPENDENCY (2026-10-20)
---------------------------------------------------------------
The store used to be a bare module-level dict, i.e. it only lived for the lifetime of the
pytest process that seeded it.  Running a downstream case on its own therefore failed with
``available: []``.  It is now **persisted to disk** and shared by every process:

* every ``save_as`` + ``global: true`` step writes the value through to
  ``test_case/UI/global_vars_<env>.json`` (atomic replace, merge-on-write, file-locked);
* any reader (``_merged_context_vars`` / ``get_global`` / ``has_global``) transparently
  refreshes from that file when its mtime changed, so a value published by an earlier run,
  a sibling pytest process, a CI job or a colleague still resolves.

Result: a case that consumes ``{{transaction-fees}}`` no longer has to run in the same
pytest process as the case that measured it — the value is genuinely global.

Isolation / escape hatches (all optional env vars):
    UI_GLOBAL_ENV         force the env name used for the file name (default: inferred
                          from BASE_URL -> release | staging | prod)
    UI_GLOBAL_STATE_FILE  absolute path of the store file (overrides the default)
    UI_GLOBAL_DISABLE=1   keep the store in memory only (old per-process behaviour)

Caveats (deliberate design choices):
* Values are keyed by name only, so the LAST writer wins per key — exactly like a global
  variable.  If a case seeds ``ticket_venue_map`` for a different product, downstream
  consumers see the new value (that is the point, not a bug).
* A value stays valid forever unless overwritten; call ``reset_globals()`` (with
  ``remove_file=True``) to wipe the store.
* xdist (``-n``) workers all share the same file through this module, so the old
  "each worker has its own copy" limitation is gone as well.
"""

import json
import os
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

try:  # POSIX only; the framework runs on macOS / Linux
    import fcntl
except ImportError:  # pragma: no cover - Windows fallback: best effort, no lock
    fcntl = None

from loguru import logger

_DEFAULT_BASE_URL = "https://release.pear.us"
_ENV_MAP = {
    "https://staging.pear.us": "staging",
    "https://release.pear.us": "release",
    "https://pear.us": "prod",
}

# In-memory view: key -> value.  Kept as a module-level dict on purpose: base.py does
# `from .global_state import GLOBAL_VARS as _GLOBAL_VARS`, so the object identity must
# never change (always mutate in place, never rebind).
GLOBAL_VARS: dict = {}

# key -> {"updated_at": epoch_seconds} — bookkeeping only, never used for lookups.
_META: dict = {}

# Which file the current in-memory view was loaded from, and its mtime at load time.
_STATE = {"path": None, "mtime": None}


# --------------------------------------------------------------------------------------
# Path / env resolution
# --------------------------------------------------------------------------------------
def _env_name() -> str:
    explicit = os.environ.get("UI_GLOBAL_ENV")
    if explicit:
        return explicit.strip()
    base_url = os.environ.get("BASE_URL", _DEFAULT_BASE_URL)
    return _ENV_MAP.get(base_url, "release")


def state_path() -> Path:
    """Absolute path of the persisted store (one file per environment)."""
    explicit = os.environ.get("UI_GLOBAL_STATE_FILE")
    if explicit:
        return Path(explicit).expanduser().resolve()
    ui_dir = Path(__file__).resolve().parent.parent  # actions/ -> test_case/UI/
    return ui_dir / f"global_vars_{_env_name()}.json"


def _disabled() -> bool:
    return os.environ.get("UI_GLOBAL_DISABLE", "").lower() in ("1", "true", "yes")


# --------------------------------------------------------------------------------------
# Disk IO
# --------------------------------------------------------------------------------------
@contextmanager
def _file_lock(path: Path):
    """Exclusive lock around read-modify-write, so parallel pytest processes cannot
    drop each other's keys.  Silently degrades to a no-op when fcntl is unavailable."""
    if fcntl is None:
        yield
        return
    lock_path = path.with_name(path.name + ".lock")
    try:
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        fh = open(lock_path, "a+")
    except OSError:
        yield
        return
    try:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
        yield
    finally:
        try:
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
        finally:
            fh.close()


def _read_disk(path: Path) -> dict:
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except FileNotFoundError:
        return {}
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning(f"global_state: cannot read {path} ({exc}) — ignoring the file")
        return {}


def _iso(epoch: float) -> str:
    if not epoch:
        return ""
    return datetime.fromtimestamp(epoch).strftime("%Y-%m-%d %H:%M:%S")


def refresh_globals(force: bool = False) -> dict:
    """Reload the in-memory view from disk when the file changed.

    Cheap (one ``stat`` call); called from every lookup so a value published by another
    process becomes visible immediately.  Never clears the in-memory view when the file
    is missing — that keeps a purely in-memory session working (UI_GLOBAL_DISABLE et al.).
    """
    if _disabled():
        return GLOBAL_VARS
    path = state_path()
    try:
        mtime = path.stat().st_mtime
    except OSError:
        return GLOBAL_VARS
    if not force and _STATE["path"] == str(path) and _STATE["mtime"] == mtime:
        return GLOBAL_VARS

    raw = _read_disk(path)
    entries = raw.get("vars") or {}
    GLOBAL_VARS.clear()
    _META.clear()
    for key, entry in entries.items():
        if isinstance(entry, dict) and "value" in entry:
            GLOBAL_VARS[key] = entry.get("value")
            _META[key] = {"updated_at": float(entry.get("updated_at_epoch") or 0)}
        else:  # tolerate a hand-written {"key": value} file
            GLOBAL_VARS[key] = entry
            _META[key] = {"updated_at": 0}
    _STATE["path"] = str(path)
    _STATE["mtime"] = mtime
    logger.debug(
        f"global_state: loaded {len(GLOBAL_VARS)} global var(s) from {path} "
        f"(env={raw.get('env') or _env_name()})"
    )
    return GLOBAL_VARS


def _flush() -> None:
    """Merge the in-memory view into the store file (atomic replace, locked)."""
    if _disabled():
        return
    path = state_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with _file_lock(path):
            on_disk = (_read_disk(path).get("vars") or {})
            on_disk.update(
                {
                    key: {
                        "value": value,
                        "updated_at_epoch": _META.get(key, {}).get("updated_at") or time.time(),
                        "updated_at": _iso(_META.get(key, {}).get("updated_at") or time.time()),
                    }
                    for key, value in GLOBAL_VARS.items()
                }
            )
            payload = {
                "env": _env_name(),
                "base_url": os.environ.get("BASE_URL", _DEFAULT_BASE_URL),
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "vars": on_disk,
            }
            tmp = path.with_name(f"{path.name}.{os.getpid()}.tmp")
            with tmp.open("w", encoding="utf-8") as fh:
                json.dump(payload, fh, ensure_ascii=False, indent=2)
            os.replace(tmp, path)
        _STATE["path"] = str(path)
        _STATE["mtime"] = path.stat().st_mtime
    except OSError as exc:  # never fail a test because the cache could not be written
        logger.warning(f"global_state: cannot persist globals to {path} ({exc})")


# --------------------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------------------
def set_global(key: str, value) -> None:
    """Publish a value to the global store (visible to every case and every process)."""
    if not key:
        return
    refresh_globals()  # pick up keys other processes wrote meanwhile
    GLOBAL_VARS[key] = value
    _META[key] = {"updated_at": time.time()}
    _flush()


def get_global(key: str, default=None):
    """Read a value from the global store (with optional default)."""
    refresh_globals()
    return GLOBAL_VARS.get(key, default)


def has_global(key: str) -> bool:
    refresh_globals()
    return key in GLOBAL_VARS


def age_seconds(key: str):
    """How long ago `key` was published (None when unknown). Handy in failure messages."""
    refresh_globals()
    updated = (_META.get(key) or {}).get("updated_at")
    return None if not updated else max(0.0, time.time() - updated)


def describe(key: str = None) -> str:
    """One-line human description of the store (or of a single key) for diagnostics."""
    refresh_globals()
    path = state_path()
    if key:
        if key not in GLOBAL_VARS:
            return f"'{key}' is NOT in the global store ({path})"
        age = age_seconds(key)
        when = _iso((_META.get(key) or {}).get("updated_at")) or "unknown"
        return f"'{key}' = {GLOBAL_VARS[key]!r} (published {when}, {int(age)}s ago) from {path}"
    return f"{len(GLOBAL_VARS)} global var(s) in {path}: {sorted(GLOBAL_VARS)}"


def reset_globals(remove_file: bool = True) -> None:
    """Wipe the store.  `remove_file=False` clears only the current process' view."""
    GLOBAL_VARS.clear()
    _META.clear()
    _STATE["path"] = None
    _STATE["mtime"] = None
    if remove_file and not _disabled():
        try:
            state_path().unlink()
        except OSError:
            pass

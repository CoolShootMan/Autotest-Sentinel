"""
Apifox web API client (cookie + project header based).
Discovered endpoints (Apifox web, project 5446866):
  GET /api/v1/projects/{pid}/test-scenario/tree-list
  GET /api/v1/projects/{pid}/environments
  GET /api/v1/projects/{pid}/database-connections
  GET /api/v1/api-test/cases/{caseId}                (case meta + step list)
  GET /api/v1/api-test/cases/{caseId}/steps?withCaseDetail=true   (FULL def)
"""
import json
import time
import urllib.request
import urllib.error
from pathlib import Path

API_BASE = "https://api.apifox.com/api/v1"

# Loaded from auth_state.json (Playwright storage state)
DEFAULT_AUTH_STATE = Path(__file__).parent / "_apifox_export" / "auth_state.json"

# Discovered from live web app request headers
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US",
    "Origin": "https://app.apifox.com",
    "Referer": "https://app.apifox.com/",
    "x-branch-id": "5122045",
    "x-client-mode": "web",
    "x-client-version": "2.8.47-alpha.1",
    "x-project-id": "5446866",
    "Content-Type": "application/json",
}


def _get_path(obj, path):
    """Safely walk a JSON object along a path list.

    Path elements are either dict keys (str) or list indices (int). Array
    indices written as ``"items[0]"`` in Apifox JSON-path expressions are
    converted to plain ints by the callers, so this walker handles both
    ``cur["items"]`` and ``cur[0]`` correctly (unlike a naive ``.get("items[0]")``
    which would never match a real dict key). It also accepts a raw
    ``"items[0]"`` string element and splits it into key + index on the fly.
    """
    cur = obj
    for p in path:
        if cur is None:
            return None
        if isinstance(cur, list):
            try:
                idx = int(p)
            except (TypeError, ValueError):
                return None
            cur = cur[idx] if 0 <= idx < len(cur) else None
        elif isinstance(cur, dict):
            if isinstance(p, str) and '[' in p and p.endswith(']'):
                key, _, rest = p.partition('[')
                sub = cur.get(key)
                try:
                    idx = int(rest.rstrip(']'))
                except (TypeError, ValueError):
                    cur = None
                else:
                    cur = sub[idx] if isinstance(sub, list) and 0 <= idx < len(sub) else None
            else:
                cur = cur.get(p)
        else:
            return None
    return cur


def _get_path_recursive(obj, segments):
    """Walk JSON along an Apifox recursive JSONPath like ``$.data..status``.

    ``segments[0]`` is resolved as a plain key at the current level; every
    following segment is matched at ANY descendant depth (``..`` semantics).
    Returns a list of all terminal values found (order-preserving).
    """
    def find_keys(cur, key):
        if cur is None:
            return
        if isinstance(cur, dict):
            for k, v in cur.items():
                if k == key:
                    yield v
                yield from find_keys(v, key)
        elif isinstance(cur, list):
            for v in cur:
                yield from find_keys(v, key)

    if not segments:
        return [obj] if obj is not None else []
    if isinstance(obj, dict) and segments[0] in obj:
        pool = [obj[segments[0]]]
    else:
        pool = [None]
    for seg in segments[1:]:
        pool = [v for cur in pool for v in find_keys(cur, seg)]
    return pool


class ApifoxClient:
    def __init__(self, project_id: str, auth_state_path: Path = DEFAULT_AUTH_STATE,
                 branch_id: str = "5122045", client_version: str = "2.8.46-alpha.2"):
        self.project_id = project_id
        self.branch_id = branch_id
        self.client_version = client_version
        self.cookie_header = self._load_cookies(auth_state_path)
        self.device_id = self._load_device_id(auth_state_path)

    @staticmethod
    def _load_cookies(p: Path) -> str:
        state = json.loads(Path(p).read_text())
        return "; ".join(f"{c['name']}={c['value']}" for c in state["cookies"])

    @staticmethod
    def _load_device_id(p: Path) -> str:
        state = json.loads(Path(p).read_text())
        for c in state["cookies"]:
            if c["name"] == "projectCid":
                return c["value"]
        return ""

    def _headers(self) -> dict:
        h = dict(DEFAULT_HEADERS)
        h["Cookie"] = self.cookie_header
        h["x-branch-id"] = self.branch_id
        h["x-client-version"] = self.client_version
        h["x-project-id"] = str(self.project_id)
        h["x-device-id"] = self.device_id
        return h

    def _request(self, url: str, retries: int = 3) -> tuple[int, bytes]:
        last_err = None
        for attempt in range(retries):
            try:
                req = urllib.request.Request(url, headers=self._headers())
                with urllib.request.urlopen(req, timeout=45) as resp:
                    return resp.status, resp.read()
            except urllib.error.HTTPError as e:
                body = e.read()
                if e.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return e.code, body
            except Exception as e:
                last_err = e
                time.sleep(1)
        return 0, str(last_err).encode()

    def get(self, path: str) -> tuple[int, dict]:
        url = path if path.startswith("http") else f"{API_BASE}{path}"
        status, body = self._request(url)
        try:
            return status, json.loads(body.decode("utf-8", "replace"))
        except Exception:
            return status, {"_raw": body.decode("utf-8", "replace")[:500]}

    def session(self) -> "requests.Session":
        """Return a requests.Session that carries the discovered Apifox web headers
        (cookie + x-project-id + x-client-version + ...).

        A urllib3 Retry adapter is mounted for https/http so transient network
        failures (SSL EOF mid-handshake/read, connection resets, 5xx, 429) are
        retried automatically. This prevents flaky false-failures in CI runs.
        """
        import requests
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry

        s = requests.Session()
        retry = Retry(
            total=3,
            connect=3,
            read=3,
            status=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=None,  # retry all methods (incl. POST) on transient failures
        )
        adapter = HTTPAdapter(max_retries=retry)
        s.mount("https://", adapter)
        s.mount("http://", adapter)
        s.headers.update({
            "User-Agent": self._headers()["User-Agent"],
            "x-branch-id": self.branch_id,
            "x-client-mode": "web",
            "x-client-version": self.client_version,
            "x-device-id": self.device_id,
            "x-project-id": str(self.project_id),
        })
        # requests will add Cookie itself via the session cookies
        for c in json.loads(DEFAULT_AUTH_STATE.read_text())["cookies"]:
            if c.get("domain", "").endswith("apifox.com"):
                s.cookies.set(c["name"], c["value"], domain=c.get("domain", ".apifox.com"))
        return s

    def get_tree_list(self) -> dict:
        return self.get(f"/projects/{self.project_id}/test-scenario/tree-list?locale=en-US")[1]

    def get_test_suite(self, suite_id: int) -> dict:
        """Fetch an Apifox test-suite definition (cases/scenarios included)."""
        status, body = self.get(f"/projects/{self.project_id}/api-test/test-suites/{suite_id}?locale=en-US")
        if status == 200 and isinstance(body, dict) and body.get("success"):
            return body.get("data", {})
        raise RuntimeError(f"Failed to fetch test suite {suite_id}: status={status} body={body}")

    def get_environments(self) -> list:
        return self.get(f"/projects/{self.project_id}/environments?locale=en-US")[1].get("data", [])

    def get_database_connections(self) -> list:
        return self.get(f"/projects/{self.project_id}/database-connections?locale=en-US")[1].get("data", [])

    def get_case(self, case_id: int) -> dict:
        return self.get(f"/api-test/cases/{case_id}?locale=en-US")[1].get("data", {})

    def get_case_steps_full(self, case_id: int) -> dict:
        return self.get(f"/api-test/cases/{case_id}/steps?withCaseDetail=true&locale=en-US")[1].get("data", {})
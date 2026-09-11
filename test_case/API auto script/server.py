"""
Visual test suite runner (Apifox-style).

A tiny zero-dependency web server (stdlib http.server) that lets you:
  - browse the 146 cases in a folder tree
  - multi-select cases (by folder or individually)
  - pick the Apifox environment (Release)
  - click Run and watch live pytest output (PASSED/FAILED streaming)
  - save the selection as a named suite (suites/*.yaml)

Usage
-----
    /usr/bin/python3 server.py             # http://127.0.0.1:8765
    /usr/bin/python3 server.py --port 9000

Open the URL in your browser. The page is self-contained.
"""
from __future__ import annotations

import argparse
import json
import os
import queue
import re
import subprocess
import sys
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
import case_index as ci  # scan tests/ for case metadata — no Apifox JSON needed

SUITES_DIR = ROOT / "suites"
# Prefer the managed venv (Python 3.13, OpenSSL 3.5) — the system py3.9 ships
# LibreSSL 2.8 which drops TLS handshakes with random SSLEOFError on every run.
PYTEST = os.environ.get("APIFOX_PYTEST") or "/Users/a123456/.workbuddy/binaries/python/envs/default/bin/python"
PORT_DEFAULT = 8765


def _scan_index():
    """Build the UI case list directly from the test sources via case_index.

    Folder/case ordering is taken from Apifox scenario_tree.json when available,
    so the UI sidebar matches the original Apifox "Runable" tree exactly.
    Falls back to filesystem scan order if the tree file is absent.

    Each case carries the fields the front-end expects:
      id, name, folder_path, priority, tags, folder_rank, case_sort_key
    `id` is the pytest func slug (always present), so running a case no longer
    depends on any Apifox numeric id.
    """
    ents = ci.scan_tests()  # already sorted like Apifox when scenario_tree.json exists
    folder_ranks: dict[str, list[int]] = {}
    out = []
    for e in ents:
        f = e["folder"]
        folder_rank = e.get("folder_rank", [99999])
        case_order = e.get("case_order", 0)
        out.append({
            "id": e["func"],               # pytest func slug — used as the run/save key
            "case_id": e.get("case_id"),   # original Apifox id (traceability only)
            "name": e["name"],
            "folder_path": f,
            "priority": e.get("priority"),
            "tags": e.get("tags") or [],
            "folder_rank": folder_rank,
            "case_sort_key": e.get("case_sort_key", folder_rank + [case_order]),
            "case_order": case_order,
            "order": (folder_rank[0] if folder_rank else 99999) * 10000 + case_order,
        })
        if f not in folder_ranks:
            folder_ranks[f] = folder_rank
            # tolerate trailing-space variants
            folder_ranks.setdefault(f.rstrip(), folder_rank)
    return out, folder_ranks


_INDEX, _FOLDER_RANKS = _scan_index()


def _load_index() -> list:
    return _INDEX


def _build_tree(index: list) -> dict:
    """Folder tree: root contains subfolders and case_ids, ordered like Apifox."""
    folders: dict[str, set] = {}  # folder_path -> set(case_ids)
    for e in index:
        folders.setdefault(e["folder_path"], set()).add(e["id"])
    tree = {"name": "Runable", "path": "", "subfolders": {}, "case_ids": []}

    def _folder_sort_key(item):
        fp = item[0]
        return _FOLDER_RANKS.get(fp, _FOLDER_RANKS.get(fp.rstrip(), [99999]))

    for fp, ids in sorted(folders.items(), key=_folder_sort_key):
        node = tree
        parts = [p for p in fp.split("/") if p]
        for p in parts:
            node = node["subfolders"].setdefault(p, {"name": p, "path": "/".join(parts[: parts.index(p) + 1]),
                                                     "subfolders": {}, "case_ids": []})
        node["case_ids"] = sorted(ids)
    return tree


# ----------------------------------------------------------------------------
# Run state
# ----------------------------------------------------------------------------

class Run:
    def __init__(self, case_ids: list[int], env: str = "Release"):
        self.id = uuid.uuid4().hex[:10]
        self.case_ids = case_ids
        self.env = env
        self.q: queue.Queue = queue.Queue()
        self.proc: subprocess.Popen | None = None
        self.summary = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0, "total": 0}
        self.started = time.time()
        self.finished = False
        self._reader: threading.Thread | None = None

    def start(self):
        cmd = [PYTEST, "-m", "pytest", "tests/",
               "--case-ids", ",".join(map(str, self.case_ids)),
               "-v", "--tb=line", "--no-header", "-p", "no:cacheprovider"]
        env = dict(os.environ)
        env["PYTHONUNBUFFERED"] = "1"
        self.proc = subprocess.Popen(cmd, cwd=str(ROOT), env=env,
                                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                     bufsize=1, text=True)
        self._reader = threading.Thread(target=self._pump, daemon=True)
        self._reader.start()

    def _pump(self):
        assert self.proc and self.proc.stdout
        try:
            for line in self.proc.stdout:
                self.q.put(("out", line.rstrip("\n")))
                m = re.search(r"\b(\d+) passed", line)
                if m: self.summary["passed"] = int(m.group(1))
                m = re.search(r"\b(\d+) failed", line)
                if m: self.summary["failed"] = int(m.group(1))
                m = re.search(r"\b(\d+) error", line)
                if m: self.summary["errors"] = int(m.group(1))
                m = re.search(r"\b(\d+) skipped", line)
                if m: self.summary["skipped"] = int(m.group(1))
        finally:
            rc = self.proc.wait()
            self.summary["total"] = sum(self.summary[k] for k in ("passed", "failed", "errors", "skipped"))
            self.q.put(("done", {"rc": rc, "summary": self.summary, "duration": round(time.time() - self.started, 1)}))
            self.finished = True


RUNS: dict[str, Run] = {}


# ----------------------------------------------------------------------------
# HTTP handler
# ----------------------------------------------------------------------------

INDEX_HTML = r"""<!doctype html>
<html lang="zh">
<head>
<meta charset="utf-8">
<title>Apifox Test Suite Runner</title>
<style>
  :root { --bg:#0f1115; --panel:#171a21; --panel2:#1f232c; --border:#2a2f3a; --text:#d6d8de; --muted:#8a8f9b; --accent:#7c5cff; --p0:#ef4444; --p1:#f59e0b; --p2:#3b82f6; --ok:#22c55e; --fail:#ef4444; }
  * { box-sizing:border-box }
  body { margin:0; font:13px/1.5 -apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial; background:var(--bg); color:var(--text); height:100vh; display:grid; grid-template-columns: 280px 1fr 380px; grid-template-rows: 44px 1fr 240px; }
  header { grid-column: 1/4; display:flex; align-items:center; padding:0 16px; border-bottom:1px solid var(--border); background:var(--panel); gap:12px; }
  header h1 { font-size:14px; margin:0; font-weight:600 }
  header .spacer { flex:1 }
  header .pill { padding:3px 10px; border-radius:10px; background:var(--panel2); color:var(--muted); font-size:12px }
  .tree { background:var(--panel); border-right:1px solid var(--border); overflow:auto; padding:8px 0; }
  .tree-node { padding:4px 12px; cursor:pointer; user-select:none; display:flex; align-items:center; gap:6px; }
  .tree-node:hover { background:var(--panel2) }
  .tree-node.active { background:var(--panel2); border-left:2px solid var(--accent) }
  .tree-folder { font-weight:500 }
  .tree-count { color:var(--muted); font-size:11px; margin-left:auto }
  .tree-children { padding-left:14px; border-left:1px solid var(--border); margin-left:8px }
  .main { overflow:auto; padding:12px 16px; }
  .toolbar { display:flex; align-items:center; gap:8px; margin-bottom:12px; flex-wrap:wrap }
  .toolbar .pill { padding:4px 10px; background:var(--panel); border:1px solid var(--border); border-radius:14px; font-size:12px }
  .toolbar button { background:var(--panel2); color:var(--text); border:1px solid var(--border); padding:5px 12px; border-radius:6px; cursor:pointer; font-size:12px }
  .toolbar button:hover { background:var(--border) }
  .toolbar input[type=text] { background:var(--panel2); color:var(--text); border:1px solid var(--border); padding:5px 10px; border-radius:6px; font-size:12px; min-width:200px }
  .case { display:grid; grid-template-columns: 24px 36px 1fr 60px; align-items:center; gap:10px; padding:8px 12px; border:1px solid var(--border); border-radius:6px; margin-bottom:4px; background:var(--panel); }
  .case:hover { background:var(--panel2) }
  .case.selected { border-color:var(--accent); background:rgba(124,92,255,0.10) }
  .case .name { font-size:13px }
  .case .id { color:var(--muted); font-size:11px; font-family:ui-monospace,Menlo,monospace }
  .prio { font-size:11px; padding:1px 6px; border-radius:8px; font-weight:600; }
  .prio.p0 { background:rgba(239,68,68,0.15); color:var(--p0) }
  .prio.p1 { background:rgba(245,158,11,0.15); color:var(--p1) }
  .prio.p2 { background:rgba(59,130,246,0.15); color:var(--p2) }
  .side { background:var(--panel); border-left:1px solid var(--border); padding:14px 16px; display:flex; flex-direction:column; gap:12px; }
  .side label { font-size:11px; color:var(--muted); text-transform:uppercase; letter-spacing:0.5px; margin-bottom:4px; display:block }
  .side select, .side input { width:100%; background:var(--panel2); color:var(--text); border:1px solid var(--border); padding:6px 8px; border-radius:6px; font-size:12px }
  .side .row { display:flex; gap:8px }
  .side .stat { display:grid; grid-template-columns: 1fr 1fr; gap:8px; }
  .side .stat .box { background:var(--panel2); border:1px solid var(--border); padding:8px; border-radius:6px; text-align:center }
  .side .stat .box b { font-size:18px; display:block }
  .side .stat .ok b { color:var(--ok) }
  .side .stat .bad b { color:var(--fail) }
  button.run { background:var(--accent); color:#fff; border:none; padding:9px 14px; border-radius:6px; cursor:pointer; font-size:13px; font-weight:600 }
  button.run:disabled { background:#444; cursor:not-allowed }
  button.run:hover:not(:disabled) { filter:brightness(1.1) }
  .log { grid-column: 1/4; background:#000; color:#d6d8de; font-family:ui-monospace,Menlo,monospace; font-size:12px; padding:10px 14px; overflow:auto; border-top:1px solid var(--border); }
  .log .l-p { color:#22c55e }
  .log .l-f { color:#ef4444 }
  .log .l-s { color:#a3a3a3 }
  .log .l-h { color:#fbbf24 }
  input[type=checkbox] { width:16px; height:16px; accent-color: var(--accent) }
</style>
</head>
<body>
<header>
  <h1>🐾 Test Suite Runner</h1>
  <span class="pill" id="total-pill">146 cases</span>
  <span class="spacer"></span>
  <span class="pill" id="env-pill">env: Release</span>
</header>

<div class="tree" id="tree"></div>

<div class="main">
  <div class="toolbar">
    <button onclick="selectAll(true)">全选</button>
    <button onclick="selectAll(false)">全不选</button>
    <button onclick="selectInvert()">反选</button>
    <input type="text" id="filter" placeholder="筛选 (按名称 / case id / 目录)…" oninput="applyFilter()">
    <span class="pill" id="sel-pill">0 selected</span>
    <span class="pill" id="vis-pill">0 shown</span>
  </div>
  <div id="cases"></div>
</div>

<div class="side">
  <div>
    <label>运行环境</label>
    <select id="env"><option>Release</option><option>Staging</option></select>
  </div>
  <div>
    <label>保存为测试套 (可选)</label>
    <div class="row">
      <input type="text" id="suite-name" placeholder="my-suite">
      <button onclick="saveSuite()">保存</button>
    </div>
  </div>
  <div class="stat">
    <div class="box ok"><b id="c-pass">0</b>passed</div>
    <div class="box bad"><b id="c-fail">0</b>failed</div>
    <div class="box"><b id="c-skip">0</b>skipped</div>
    <div class="box"><b id="c-total">0</b>total</div>
  </div>
  <button class="run" id="run-btn" onclick="runSelected()">▶  运行选中 (0)</button>
</div>

<div class="log" id="log"></div>

<script>
const ALL = __INDEX__;   // injected: list of cases enriched with folder_rank / case_sort_key
const FOLDER_RANKS = __FOLDER_RANKS__;  // injected: folder_path -> sibling-rank array
function getFolderRank(path) { return FOLDER_RANKS[path] || FOLDER_RANKS[path.replace(/\s+$/, "")] || []; }
function cmpRank(a, b) {
  for (let i = 0; i < Math.min(a.length, b.length); i++) {
    if (a[i] < b[i]) return -1;
    if (a[i] > b[i]) return 1;
  }
  return a.length - b.length;
}
let ACTIVE_FOLDER = ""; // currently shown folder path
let SELECTED = new Set();
let CURRENT_RUN = null;

function folderCaseIds(p) { return ALL.filter(c => c.folder_path === p).map(c => c.id); }
function folderAllIds(p) {
  // includes subfolders
  return ALL.filter(c => c.folder_path === p || c.folder_path.startsWith(p + "/")).map(c => c.id);
}
function isDescendant(path) {
  return ACTIVE_FOLDER === "" || path === ACTIVE_FOLDER || path.startsWith(ACTIVE_FOLDER + "/");
}

function renderTree() {
  // build tree from ALL, attaching Apifox folder_rank to every node
  const root = { name: "Runable", path: "", kids: {}, folder_rank: [] };
  for (const c of ALL) {
    let node = root;
    const parts = (c.folder_path || "").split("/").filter(Boolean);
    for (const p of parts) {
      const path = parts.slice(0, parts.indexOf(p) + 1).join("/");
      node.kids[p] = node.kids[p] || { name: p, path, kids: {}, cases: [], folder_rank: getFolderRank(path) };
      node = node.kids[p];
    }
    node.cases = node.cases || [];
    node.cases.push(c);
  }
  const html = renderNode(root, true);
  document.getElementById("tree").innerHTML = html;
  bindTree();
}

function renderNode(node, isRoot) {
  // 子文件夹严格按 Apifox 侧栏顺序（folder_rank）排列
  const folders = Object.values(node.kids).sort((a, b) => cmpRank(a.folder_rank, b.folder_rank));
  const own = (node.cases || []).length;
  let h = "";
  if (!isRoot) {
    const allIds = node.cases ? node.cases.map(c => c.id) : [];
    let subIds = [];
    function collect(n) { subIds.push(...(n.cases||[]).map(c=>c.id)); for (const k of Object.values(n.kids)) collect(k); }
    collect(node);
    const selectedInFolder = subIds.filter(i => SELECTED.has(i)).length;
    const myPath = node.path;
    h += `<div class="tree-node ${ACTIVE_FOLDER === myPath ? 'active' : ''}" onclick="setActive('${myPath}')">
        <span class="tree-folder">📁 ${node.name}</span>
        <span class="tree-count">${selectedInFolder}/${subIds.length}</span>
      </div>`;
  }
  const kids = folders.map(f => renderNode(f, false)).join("");
  return h + (kids ? `<div class="tree-children">${kids}</div>` : "");
}

function bindTree() { /* click via onclick attr */ }
function setActive(p) {
  ACTIVE_FOLDER = (p === ACTIVE_FOLDER) ? "" : p;
  renderTree();
  renderCases();
}

function renderCases() {
  const list = ALL.filter(c => isDescendant(c.folder_path))
                   .sort((a, b) => cmpRank(a.case_sort_key, b.case_sort_key) || a.name.localeCompare(b.name)); // 按 Apifox 侧栏 folder/case 顺序
  const q = (document.getElementById("filter").value || "").toLowerCase().trim();
  const filtered = q ? list.filter(c =>
    c.name.toLowerCase().includes(q) ||
    String(c.id).includes(q) ||
    c.folder_path.toLowerCase().includes(q)
  ) : list;
  const html = filtered.map(c => {
    const sel = SELECTED.has(c.id) ? " selected" : "";
    const prio = c.priority != null ? `<span class="prio p${c.priority}">P${c.priority}</span>` : "";
    return `<div class="case${sel}" data-id="${c.id}">
        <input type="checkbox" ${sel ? "checked" : ""} onchange="toggle('${c.id}', this.checked)">
        <span class="id">${c.id}</span>
        <span class="name">${esc(c.folder_path.split("/").slice(-1)[0] || "—")} / ${esc(c.name)}</span>
        ${prio}
      </div>`;
  }).join("");
  document.getElementById("cases").innerHTML = html || `<div style="color:var(--muted);padding:20px">该目录下没有用例</div>`;
  updatePills();
}

function esc(s) { return String(s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;"})[c]); }

function toggle(id, on) { on ? SELECTED.add(id) : SELECTED.delete(id); renderCases(); renderTree(); }
function selectAll(on) {
  const list = ALL.filter(c => isDescendant(c.folder_path));
  list.forEach(c => on ? SELECTED.add(c.id) : SELECTED.delete(c.id));
  renderCases(); renderTree();
}
function selectInvert() {
  const list = ALL.filter(c => isDescendant(c.folder_path));
  list.forEach(c => SELECTED.has(c.id) ? SELECTED.delete(c.id) : SELECTED.add(c.id));
  renderCases(); renderTree();
}
function applyFilter() { renderCases(); }
function updatePills() {
  document.getElementById("sel-pill").textContent = `${SELECTED.size} selected`;
  const visible = document.querySelectorAll(".case").length;
  document.getElementById("vis-pill").textContent = `${visible} shown`;
  const btn = document.getElementById("run-btn");
  btn.textContent = `▶  运行选中 (${SELECTED.size})`;
  btn.disabled = SELECTED.size === 0 || (CURRENT_RUN && !CURRENT_RUN.finished);
}

async function runSelected() {
  if (SELECTED.size === 0) return;
  const env = document.getElementById("env").value;
  document.getElementById("log").innerHTML = "";
  const ids = [...SELECTED];
  const r = await fetch("/api/run", { method:"POST", headers:{"Content-Type":"application/json"},
                                       body: JSON.stringify({ids, env}) });
  const { run_id } = await r.json();
  CURRENT_RUN = { id: run_id, finished: false };
  updatePills();
  streamLog(run_id);
}

function streamLog(runId) {
  const src = new EventSource("/api/stream/" + runId);
  const log = document.getElementById("log");
  src.addEventListener("out", e => {
    const line = e.data;
    const cls = line.includes(" PASSED") ? "l-p" : (line.includes(" FAILED") || line.includes(" ERROR") ? "l-f"
              : (line.startsWith("=====") || line.startsWith("_____") || line.startsWith("collecting") ? "l-h"
              : (line.includes("skipped") ? "l-s" : "")));
    const el = document.createElement("div");
    if (cls) el.className = cls;
    el.textContent = line;
    log.appendChild(el);
    log.scrollTop = log.scrollHeight;
  });
  src.addEventListener("done", e => {
    const d = JSON.parse(e.data);
    document.getElementById("c-pass").textContent = d.summary.passed;
    document.getElementById("c-fail").textContent = d.summary.failed;
    document.getElementById("c-skip").textContent = d.summary.skipped;
    document.getElementById("c-total").textContent = d.summary.total;
    src.close();
    if (CURRENT_RUN) CURRENT_RUN.finished = true;
    updatePills();
    const el = document.createElement("div");
    el.className = d.summary.failed > 0 ? "l-f" : "l-p";
    el.textContent = `\n===== 退出码 ${d.rc}  用时 ${d.duration}s =====`;
    log.appendChild(el);
  });
  src.onerror = () => src.close();
}

async function saveSuite() {
  const name = (document.getElementById("suite-name").value || "").trim();
  if (!name || SELECTED.size === 0) { alert("请先输入套名并选用例"); return; }
  const ids = [...SELECTED];
  const r = await fetch("/api/save_suite", { method:"POST", headers:{"Content-Type":"application/json"},
                                              body: JSON.stringify({name, ids}) });
  const j = await r.json();
  if (j.ok) alert("已保存到 suites/" + j.file);
  else alert("失败: " + j.error);
}

document.getElementById("total-pill").textContent = `${ALL.length} cases`;
renderTree();
renderCases();
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        sys.stderr.write("[%s] %s\n" % (self.address_string(), fmt % args))

    def _json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _html(self, html: str):
        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urlparse(self.path)
        path = url.path

        if path == "/":
            index = _load_index()
            folder_ranks = {k: v for k, v in _FOLDER_RANKS.items()}
            html = (INDEX_HTML
                    .replace("__INDEX__", json.dumps(index, ensure_ascii=False))
                    .replace("__FOLDER_RANKS__", json.dumps(folder_ranks, ensure_ascii=False)))
            return self._html(html)
        if path == "/api/cases":
            return self._json(_load_index())
        if path == "/api/tree":
            return self._json(_build_tree(_load_index()))
        if path.startswith("/api/stream/"):
            run_id = path[len("/api/stream/"):]
            return self._stream(run_id)
        if path == "/api/suites":
            files = sorted(SUITES_DIR.glob("*.y*ml")) + sorted(SUITES_DIR.glob("*.json")) if SUITES_DIR.exists() else []
            return self._json([f.name for f in files])
        self.send_error(404)

    def do_POST(self):
        url = urlparse(self.path)
        path = url.path
        length = int(self.headers.get("Content-Length", "0") or 0)
        body = self.rfile.read(length) if length else b"{}"
        try:
            data = json.loads(body) if body else {}
        except Exception:
            data = {}

        if path == "/api/run":
            # ids are pytest func slugs (strings) — fall back to numeric for safety
            ids = [str(i) for i in data.get("ids", []) if i not in (None, "")]
            if not ids:
                return self._json({"error": "no ids"}, 400)
            env = data.get("env", "Release")
            run = Run(ids, env=env)
            RUNS[run.id] = run
            run.start()
            return self._json({"run_id": run.id})

        if path == "/api/save_suite":
            name = (data.get("name") or "").strip()
            ids = [str(i) for i in data.get("ids", []) if i not in (None, "")]
            if not name or not ids:
                return self._json({"ok": False, "error": "name/ids missing"}, 400)
            SUITES_DIR.mkdir(exist_ok=True)
            slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_") or "suite"
            file = SUITES_DIR / f"{slug}.yaml"
            content = (f"name: {name}\ndescription: saved from web UI\ninclude:\n  case_ids:\n" +
                       "\n".join(f"    - \"{i}\"" for i in sorted(set(ids))) + "\npytest_args:\n  - -v\n")
            file.write_text(content, encoding="utf-8")
            return self._json({"ok": True, "file": file.name})

        self.send_error(404)

    # SSE stream
    def _stream(self, run_id: str):
        run = RUNS.get(run_id)
        if not run:
            self.send_error(404, "run not found")
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()
        try:
            while True:
                try:
                    kind, payload = run.q.get(timeout=30)
                except queue.Empty:
                    self._writeln(": keepalive\n\n")
                    self.wfile.flush()
                    continue
                if kind == "out":
                    self._writeln(f"event: out\ndata: {payload}\n\n")
                elif kind == "done":
                    self._writeln(f"event: done\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n")
                    self.wfile.flush()
                    break
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _writeln(self, s: str):
        self.wfile.write(s.encode("utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=PORT_DEFAULT)
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"🦊 Test Suite Runner (Apifox-free)")
    print(f"   URL  : http://{args.host}:{args.port}")
    print(f"   Cases: {len(_load_index())}")
    print(f"   Press Ctrl+C to stop\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nbye.")


if __name__ == "__main__":
    main()

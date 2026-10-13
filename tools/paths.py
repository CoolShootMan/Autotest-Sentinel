"""Single source of truth for well-known repository paths (UI consolidation U1).

The UI automation line used to scatter ``test_case/UI`` string
joins across conftest.py / main.py / runner.py. When the UI line is gathered
into a self-contained root (U2, git mv), this file is the only Python module
that needs updating (plus pytest.ini's ``testpaths``, which cannot import
Python).
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# UI automation line: cases + engine + actions + heal + utils + cookies.
UI_TEST_DIR = REPO_ROOT / "test_case" / "UI"      # pytest target dir (main.py)
UI_ROOT = UI_TEST_DIR              # UI line root
UI_YAML_DIR = UI_ROOT / "All_YAML"                # YAML case files

# Cross-line seam: main.py shells out to the API line's prefill suite before
# running UI tests. U3 (inline API calls) will replace this subprocess call.
API_PREFILL_DIR = REPO_ROOT / "test_case" / "API auto script"

# Prevent Git Credential Manager from hanging on a GUI prompt in a headless shell.
# Without this, `git push` / `git fetch` can block forever on the
# `git-credential-helper-selector` dialog (0-byte log, never returns).
#
# Usage (PowerShell):
#     . .\tools\gh_env.ps1
#
# NOTE: tools/gh_push.py and tools/gh_pr.py already set this environment internally,
#       so you do NOT need to source this file when using them.
#       This file is only for bare `git push` / `git fetch` in a shell.

$env:GIT_TERMINAL_PROMPT = "0"      # never prompt for username/password on the terminal
$env:GCM_INTERACTIVE      = "never" # Git Credential Manager: never show interactive UI
$env:GIT_ASKPASS          = "echo"  # fail fast instead of popping a window
$env:SSH_ASKPASS          = "echo"
$env:GIT_CONFIG_COUNT     = "1"     # append config: credential.helper = "" (clears the helper list)
$env:GIT_CONFIG_KEY_0     = "credential.helper"
$env:GIT_CONFIG_VALUE_0   = ""

Write-Host "[gh_env] GCM-hang guard applied (GIT_TERMINAL_PROMPT=0 / GCM_INTERACTIVE=never / credential.helper cleared)"

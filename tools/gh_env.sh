#!/usr/bin/env sh
# 给「裸 git 网络操作」(git push / fetch / pull / ls-remote) 用的「防 GCM 挂起」环境。
#
# 背景：本机在无头 shell 里跑 git 网络操作时，Git Credential Manager 会弹出
#       `git-credential-helper-selector` 的 GUI 选择框等输入 —— push/fetch **永久阻塞、日志 0 字节**。
#       根治办法：清空 credential.helper（凭据走 token URL 或已缓存，本就不需要助手）+ 关掉一切交互。
#
# 用法（bash）：
#     . tools/gh_env.sh            # 注意前缀是「点+空格」= source
#     git fetch origin             # 之后本 shell 里的裸 git 网络操作都不会卡
#
# ⚠️ tools/gh_push.py 与 tools/gh_pr.py **已内置**这套环境，用它们时**无需** source 本脚本。

export GIT_TERMINAL_PROMPT=0          # 禁止在终端上提示用户名/密码
export GCM_INTERACTIVE=never          # Git Credential Manager 永不弹交互 UI
export GIT_ASKPASS=echo               # 兜底：被要求口令时返回空（快速失败）而不是弹窗
export SSH_ASKPASS=echo               # 同上（SSH 走 GUI 提示的场景）
export GIT_CONFIG_COUNT=1             # 追加一条 config，把 credential.helper 置空（= 清空助手列表）
export GIT_CONFIG_KEY_0=credential.helper
export GIT_CONFIG_VALUE_0=

echo "[gh_env] 已注入防 GCM 挂起环境 (GIT_TERMINAL_PROMPT=0 / GCM_INTERACTIVE=never / credential.helper 已清空)"

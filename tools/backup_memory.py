#!/usr/bin/env python3
"""本地备份 .workbuddy/memory —— 记忆绝不入 git，只做本地快照。

2026-09-17 事故：.workbuddy/memory 整目录被物理删除，且因 `.workbuddy/*` 被 gitignore
（从未入库）而无法从 git 恢复。本脚本提供本地冗余：

    <dest>/latest/                 最新一份「镜像」（每次覆盖，便于日常查看）
    <dest>/snapshots/<时间戳>/      历史快照（只增不减，按 --keep 轮转）

镜像 + 快照双保险：即使源被误删，latest 会跟着空，但 snapshots 里仍有历史内容可还原。
（若只做镜像，源一被删备份也一起没，等于没备份。）

用法：
    py -3.9 tools/backup_memory.py                  # 备份（默认保留 30 份快照）
    py -3.9 tools/backup_memory.py --keep 60        # 改保留份数
    py -3.9 tools/backup_memory.py --list           # 列出所有快照
    py -3.9 tools/backup_memory.py --restore latest # 从最新镜像还原
    py -3.9 tools/backup_memory.py --restore 2026-09-18_145600   # 从指定快照还原
    py -3.9 tools/backup_memory.py --dest D:/my_backup           # 自定义备份位置

无人值守（Windows 计划任务，无窗口）：
    pythonw.exe tools/backup_memory.py --log <备份区>/backup.log
    —— pythonw 不分配控制台，屏幕上不会闪窗；--log 把完整输出落到文件，
       所以静默执行也不会丢掉失败信息（退出码仍反映成败）。
"""
from __future__ import annotations

import argparse
import contextlib
import io
import shutil
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / ".workbuddy" / "memory"
PROJECT = REPO.name
DEFAULT_DEST = Path.home() / ".autotest-memory-backup" / PROJECT
DEFAULT_KEEP = 30


def _sizeof(p: Path) -> int:
    return sum(f.stat().st_size for f in p.rglob("*") if f.is_file())


def _listdir(p: Path) -> list:
    return sorted(x.name for x in p.iterdir())


def cmd_backup(dest: Path, keep: int, quiet: bool) -> int:
    if not SRC.exists():
        print(f"[FAIL] 源目录不存在: {SRC}", file=sys.stderr)
        print("       若确实已被删除，请用 --restore 从快照还原，不要新建空目录顶替。", file=sys.stderr)
        return 2
    files = [f for f in SRC.rglob("*") if f.is_file()]
    if not files:
        print(f"[FAIL] 源目录为空: {SRC}", file=sys.stderr)
        return 2

    snapshots = dest / "snapshots"
    latest = dest / "latest"
    dest.mkdir(parents=True, exist_ok=True)
    snapshots.mkdir(parents=True, exist_ok=True)

    # 1) 镜像（覆盖式）
    shutil.rmtree(latest, ignore_errors=True)
    shutil.copytree(SRC, latest)

    # 2) 快照（时间戳，避免同秒冲突加后缀）
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    snap = snapshots / ts
    n = 1
    while snap.exists():
        n += 1
        snap = snapshots / f"{ts}_{n}"
    shutil.copytree(SRC, snap)

    # 3) 轮转：只保留最近 keep 份
    olds = sorted([d for d in snapshots.iterdir() if d.is_dir()])
    removed = []
    while len(olds) > keep:
        victim = olds.pop(0)
        shutil.rmtree(victim, ignore_errors=True)
        removed.append(victim.name)

    if not quiet:
        print(f"[OK] 源      : {SRC}")
        print(f"[OK] 备份至  : {dest}")
        print(f"[OK] 镜像    : latest ({len(files)} 文件, {_sizeof(latest)} B)")
        print(f"[OK] 新快照  : snapshots/{snap.name}")
        print(f"[OK] 快照总数: {len(olds)} / 上限 {keep}")
        for f in _listdir(SRC):
            print(f"       - {f}")
        if removed:
            print(f"[OK] 轮转清理: {', '.join(removed)}")
    return 0


def cmd_list(dest: Path) -> int:
    snapshots = dest / "snapshots"
    if not snapshots.exists():
        print(f"(无备份) {dest}")
        return 1
    for d in sorted([x for x in snapshots.iterdir() if x.is_dir()]):
        print(f"{d.name}   {len(list(d.rglob('*')))} 项   {_sizeof(d)} B")
    print(f"\n镜像: {dest / 'latest'}")
    return 0


def cmd_restore(dest: Path, which: str) -> int:
    snapshots = dest / "snapshots"
    if which == "latest":
        source = dest / "latest"
    else:
        source = snapshots / which
    if not source.exists():
        print(f"[FAIL] 找不到备份: {source}", file=sys.stderr)
        print("       用 --list 查看可用快照。", file=sys.stderr)
        return 2

    # 还原前先把当前现场另存为 safety 快照，避免覆盖掉更新的内容
    if SRC.exists() and any(SRC.rglob("*")):
        ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        safety = (dest / "snapshots") / f"BEFORE-RESTORE_{ts}"
        safety.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(SRC, safety)
        print(f"[OK] 还原前现场已另存: snapshots/{safety.name}")

    # 先把新内容备到同盘临时目录，成功后再原子替换。
    # 不能「先 rmtree(SRC) 再 copytree」—— 万一复制中途失败，memory 就真空了。
    tmp = SRC.parent / (SRC.name + ".restore-tmp")
    shutil.rmtree(tmp, ignore_errors=True)
    shutil.copytree(source, tmp)
    shutil.rmtree(SRC, ignore_errors=True)
    tmp.rename(SRC)

    print(f"[OK] 已从 {source} 还原到 {SRC}")
    for f in _listdir(SRC):
        print(f"       - {f}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="本地备份 .workbuddy/memory")
    ap.add_argument("--dest", type=Path, default=DEFAULT_DEST, help=f"备份根目录（默认 {DEFAULT_DEST}）")
    ap.add_argument("--keep", type=int, default=DEFAULT_KEEP, help=f"保留快照份数（默认 {DEFAULT_KEEP}）")
    ap.add_argument("--list", action="store_true", help="列出所有快照")
    ap.add_argument("--restore", metavar="SNAPSHOT", help="从 latest 或指定快照还原")
    ap.add_argument("--quiet", action="store_true", help="静默模式（用于定时任务）")
    ap.add_argument("--log", type=Path, help="把本次完整输出追加到该日志文件（供无窗口定时任务留痕）")
    args = ap.parse_args()

    def run() -> int:
        if args.list:
            return cmd_list(args.dest)
        if args.restore:
            return cmd_restore(args.dest, args.restore)
        return cmd_backup(args.dest, args.keep, args.quiet)

    if args.log is None:
        return run()

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        rc = run()
    body = buf.getvalue().rstrip() or "(quiet: 本轮无输出)"
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        args.log.parent.mkdir(parents=True, exist_ok=True)
        with args.log.open("a", encoding="utf-8") as fh:
            fh.write(f"===== {stamp}  rc={rc} =====\n{body}\n")
    except OSError as e:
        # 日志写不进去不该让备份本身失败
        sys.stderr.write(f"[WARN] 写日志失败: {e}\n")
    sys.stdout.write(buf.getvalue())  # 仍回显，交互使用时行为不变
    return rc


if __name__ == "__main__":
    sys.exit(main())

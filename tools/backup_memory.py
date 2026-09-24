#!/usr/bin/env python3
"""本地备份 .workbuddy/memory —— 记忆绝不入 git，只做本地快照。

2026-09-17 事故：.workbuddy/memory 整目录被物理删除，且因 `.workbuddy/*` 被 gitignore
（从未入库）而无法从 git 恢复。本脚本提供本地冗余：

    <dest>/latest/                 最新一份「镜像」（每次覆盖，便于日常查看）
    <dest>/snapshots/<时间戳>/      热区历史快照（按 --keep 轮转）
    <dest>/../_archive/<项目>/<时间戳>/   轮转出去的旧快照（默认永不删除）

镜像 + 快照双保险：即使源被误删，latest 会跟着空，但 snapshots / _archive 里仍有历史可还原。
（若只做镜像，源一被删备份也一起没，等于没备份。）

轮转语义（2026-09-24 起）：超过 --keep 的旧快照**移动**到归档区而不是删除。
`--keep` 从此只决定「热区留多少份」，历史不再永久丢失（此前用 rmtree，
2026-09-20 那次 `--keep 1` 就一次性永久删掉了 21 份）。
归档区位于 `<dest>` 的**兄弟目录**、在工具管理范围之外 —— 因为轮转是按
`snapshots/` 下的子目录遍历的，归档目录若放在 `snapshots/` 里会被当成待轮转快照。
归档动作**失败时保留原快照**（宁可超出 --keep，也绝不退化成删除）。
用 `--no-archive` 可恢复旧的「直接删除」行为。

用法：
    py -3.9 tools/backup_memory.py                  # 备份（默认热区保留 30 份，超出移入归档）
    py -3.9 tools/backup_memory.py --keep 60        # 改热区保留份数
    py -3.9 tools/backup_memory.py --no-archive      # 超出 --keep 的直接删除（旧行为）
    py -3.9 tools/backup_memory.py --archive-dir D:/arc   # 自定义归档位置
    py -3.9 tools/backup_memory.py --list           # 列出热区快照 + 归档区快照
    py -3.9 tools/backup_memory.py --restore latest # 从最新镜像还原
    py -3.9 tools/backup_memory.py --restore 2026-09-18_145600   # 从指定快照还原（自动含归档区）
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
ARCHIVE_DIRNAME = "_archive"


def _sizeof(p: Path) -> int:
    return sum(f.stat().st_size for f in p.rglob("*") if f.is_file())


def _listdir(p: Path) -> list:
    return sorted(x.name for x in p.iterdir())


def archive_root(dest: Path, override=None) -> Path:
    """轮转出去的快照去哪。

    刻意放在 `<dest>` 的**兄弟目录**（`<dest>/../_archive/<项目名>`），而不是 `<dest>/_archive`：
    轮转是按 `snapshots/` 下的子目录遍历的，归档目录只要落在 `snapshots/` 里就会被当成待轮转快照，
    总有一天把自己归档掉的归档吃回去。
    """
    if override is not None:
        return Path(override)
    return dest.parent / ARCHIVE_DIRNAME / dest.name


def _unique(root: Path, name: str) -> Path:
    """同名的归档目标已存在时加后缀，绝不覆盖。"""
    target = root / name
    n = 1
    while target.exists():
        n += 1
        target = root / f"{name}_{n}"
    return target


def find_snapshot(dest: Path, which: str, override=None):
    """按时间戳找快照：先热区，再归档区（含手工批次目录 `*/snapshots/<ts>`）。"""
    root = archive_root(dest, override)
    cands = [dest / "snapshots" / which]
    if root.exists():
        cands.append(root / which)
        cands += sorted(root.glob(f"*/snapshots/{which}"))  # 手工归档批次
        cands += sorted(root.glob(f"*/{which}"))            # 一层嵌套
    for c in cands:
        if c.is_dir():
            return c
    return None


def cmd_backup(dest: Path, keep: int, quiet: bool, archive: bool = True, archive_dir=None) -> int:
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

    arc = archive_root(dest, archive_dir)
    if archive and (snapshots.resolve() == arc.resolve()
                    or snapshots.resolve() in arc.resolve().parents):
        print(f"[FAIL] 归档区不能放在 snapshots/ 里面（会被轮转当成待归档快照吃掉）: {arc}",
              file=sys.stderr)
        return 2

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

    # 3) 轮转：热区只留最近 keep 份，多出来的移入归档区（不删）
    olds = sorted([d for d in snapshots.iterdir() if d.is_dir()])
    rotated = []  # (name, "archived" | "deleted" | "kept")
    while len(olds) > keep:
        victim = olds.pop(0)
        if not archive:
            shutil.rmtree(victim, ignore_errors=True)
            rotated.append((victim.name, "deleted"))
            continue
        try:
            arc.mkdir(parents=True, exist_ok=True)
            shutil.move(str(victim), str(_unique(arc, victim.name)))
            rotated.append((victim.name, "archived"))
        except Exception as e:
            # 关键：归档失败绝不退化成删除 —— 宁可热区超出 --keep，也要保住这份历史。
            rotated.append((victim.name, "kept"))
            print(f"[WARN] 轮转归档失败，已保留（热区暂时超出 --keep）: {victim.name}"
                  f"  ({type(e).__name__}: {e})", file=sys.stderr)

    if not quiet:
        print(f"[OK] 源      : {SRC}")
        print(f"[OK] 备份至  : {dest}")
        print(f"[OK] 镜像    : latest ({len(files)} 文件, {_sizeof(latest)} B)")
        print(f"[OK] 新快照  : snapshots/{snap.name}")
        print(f"[OK] 快照总数: {len(olds)} / 上限 {keep}")
        for f in _listdir(SRC):
            print(f"       - {f}")
        n_arch = sum(1 for _, a in rotated if a == "archived")
        n_del = sum(1 for _, a in rotated if a == "deleted")
        n_keep = sum(1 for _, a in rotated if a == "kept")
        if n_arch:
            print(f"[OK] 轮转归档: {n_arch} 份 -> {arc}")
        if n_del:
            print(f"[OK] 轮转删除: {n_del} 份 (--no-archive, 永久删除): "
                  f"{', '.join(n for n, a in rotated if a == 'deleted')}")
        if n_keep:
            print(f"[WARN] 归档失败保留: {n_keep} 份 (热区 {len(olds)} / 上限 {keep} 已超出)")
    return 0


def cmd_list(dest: Path, archive_dir=None) -> int:
    snapshots = dest / "snapshots"
    if not snapshots.exists():
        print(f"(无备份) {dest}")
        return 1
    hot = sorted([x for x in snapshots.iterdir() if x.is_dir()])
    print(f"热区 {snapshots}:")
    for d in hot:
        print(f"{d.name}   {len(list(d.rglob('*')))} 项   {_sizeof(d)} B")
    print(f"  合计 {len(hot)} 份")

    root = archive_root(dest, archive_dir)
    if not root.exists():
        print(f"\n归档区 {root}: (还没建)")
    else:
        print(f"\n归档区 {root}:")
        n_all = 0
        for d in sorted([x for x in root.iterdir() if x.is_dir()]):
            nested = d / "snapshots"          # 手工归档批次（含 MANIFEST/README 的那种）
            if nested.is_dir():
                subs = sorted([x for x in nested.iterdir() if x.is_dir()])
                print(f"  {d.name}/  (手工批次, {len(subs)} 份)")
                for s in subs:
                    print(f"    {s.name}   {_sizeof(s)} B")
                n_all += len(subs)
            else:
                print(f"  {d.name}   {len(list(d.rglob('*')))} 项   {_sizeof(d)} B")
                n_all += 1
        print(f"  合计 {n_all} 份")

    print(f"\n镜像: {dest / 'latest'}")
    return 0


def cmd_restore(dest: Path, which: str, archive_dir=None) -> int:
    if which == "latest":
        source = dest / "latest"
    else:
        source = find_snapshot(dest, which, archive_dir)
    if source is None or not source.exists():
        shown = which if source is None else str(source)
        print(f"[FAIL] 找不到备份: {shown}", file=sys.stderr)
        if source is None:
            print(f"       已查找: {dest / 'snapshots'} 与归档区 {archive_root(dest, archive_dir)}",
                  file=sys.stderr)
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
    ap.add_argument("--keep", type=int, default=DEFAULT_KEEP, help=f"热区保留快照份数（默认 {DEFAULT_KEEP}）")
    ap.add_argument("--archive-dir", type=Path, default=None,
                    help=f"轮转归档位置（默认 {DEFAULT_DEST.parent / ARCHIVE_DIRNAME / DEFAULT_DEST.name}）")
    ap.add_argument("--no-archive", action="store_true",
                    help="轮转时直接删除旧快照（旧行为）；默认是移入归档区、永不删除")
    ap.add_argument("--list", action="store_true", help="列出所有快照（热区 + 归档区）")
    ap.add_argument("--restore", metavar="SNAPSHOT", help="从 latest 或指定快照还原（含归档区）")
    ap.add_argument("--quiet", action="store_true", help="静默模式（用于定时任务）")
    ap.add_argument("--log", type=Path, help="把本次完整输出追加到该日志文件（供无窗口定时任务留痕）")
    args = ap.parse_args()

    def run() -> int:
        if args.list:
            return cmd_list(args.dest, args.archive_dir)
        if args.restore:
            return cmd_restore(args.dest, args.restore, args.archive_dir)
        return cmd_backup(args.dest, args.keep, args.quiet,
                          archive=not args.no_archive, archive_dir=args.archive_dir)

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

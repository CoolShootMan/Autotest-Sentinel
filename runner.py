#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
Filename         : runner.py
Description      : 自动查找测试用例所在的 YAML 文件并运行 pytest
Time             : 2024/04/14
"""

import sys
import subprocess
import re
from pathlib import Path
from typing import List, Dict, Tuple, Set

# 定义常量路径
BASE_DIR = Path("test_case/UI/Test_Katana")
YAML_DIR = BASE_DIR / "All_YAML"
TEST_FILE = BASE_DIR / "test_ui.py"

def get_test_cases_from_yaml(yaml_path: str) -> List[Dict[str, str]]:
    """
    从指定的 yaml 文件中解析出所有的测试用例名称和描述
    假设测试用例的定义以 test 且顶格开头，如 'testT4718:'
    紧接着的行可能是 '  description: "xxx"'
    返回一个包含 {"name": "test_name", "desc": "description"} 字典的列表
    """
    test_cases = []
    abs_path = BASE_DIR / yaml_path
    
    if not abs_path.exists():
        return test_cases
        
    try:
        with abs_path.open('r', encoding='utf-8') as f:
            current_test = None
            for line in f:
                match = re.match(r'^(test[a-zA-Z0-9_]+):', line)
                if match:
                    if current_test:
                        test_cases.append(current_test)
                    current_test = {"name": match.group(1), "desc": ""}
                elif current_test:
                    desc_match = re.match(r'^\s+description:\s*(["\'])(.*?)\1', line)
                    if desc_match and not current_test["desc"]:
                        current_test["desc"] = desc_match.group(2)
            
            if current_test:
                test_cases.append(current_test)
                
    except Exception as e:
        print(f"⚠️ 读取配置文件 {abs_path} 时出错: {e}")
        
    return test_cases

def run_single_pytest(test_name: str, yaml_path: str, additional_args: List[str]) -> bool:
    """
    执行单个 pytest 命令，并返回执行结果状态
    """
    print(f"\n{'*' * 50}")
    print(f"🧪 开始执行测试用例: {test_name}" if test_name else "🧪 开始执行整个文件")
    print(f"{'*' * 50}\n")
    
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(TEST_FILE),
        "--yaml", yaml_path
    ]
    
    if test_name:
        cmd.extend(["-k", test_name])
    
    if not additional_args:
        cmd.extend(["--headed", "-v"])
    else:
        cmd.extend(additional_args)
        
    print(f"💻 执行命令: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, check=False)
        print(f"\n{'-' * 50}")
        if result.returncode != 0:
            print(f"❌ 用例 {test_name or '全部'} 执行失败！")
            print(f"{'-' * 50}\n")
            return False
        
        print(f"✅ 用例 {test_name or '全部'} 执行成功！")
        print(f"{'-' * 50}\n")
        return True
    except KeyboardInterrupt:
        print("\n🛑 测试执行被用户中断。")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 执行命令时出错: {e}")
        return False

def execute_yamls(yaml_paths: List[str], k_expression: str, additional_args: List[str]) -> bool:
    """
    按配置文件执行测试。如果 k_expression 为空，则找出 yaml 内所有用例依次执行。
    """
    has_error = False
    
    for i, p in enumerate(yaml_paths, 1):
        print(f"\n{'#' * 60}")
        print(f"▶️  开始处理配置文件 [{i}/{len(yaml_paths)}]: {p}")
        print(f"{'#' * 60}")
        
        if not k_expression:
            test_cases = get_test_cases_from_yaml(p)
            if not test_cases:
                print(f"⚠️ 未在 {p} 中找到有效的测试用例 (以 test 开头)。将尝试直接执行整个文件。")
                if not run_single_pytest("", p, additional_args):
                    has_error = True
            else:
                names = [tc['name'] for tc in test_cases]
                print(f"🔍 在该配置文件中找到 {len(test_cases)} 个用例: {', '.join(names)}")
                for idx, tc in enumerate(test_cases, 1):
                    print(f"\n⏳ 进度: 配置文件 [{i}/{len(yaml_paths)}] -> 用例 [{idx}/{len(test_cases)}]")
                    if not run_single_pytest(tc['name'], p, additional_args):
                        has_error = True
        else:
            if not run_single_pytest(k_expression, p, additional_args):
                has_error = True
                
    return not has_error

def find_yaml_for_tests(test_names: List[str]) -> List[str]:
    """
    在 All_YAML 目录下搜索包含指定测试用例名称的 YAML 文件
    """
    if not YAML_DIR.exists():
        print(f"❌ 错误: 找不到目录 {YAML_DIR}")
        return []
        
    found_yamls: Set[str] = set()
    
    for filepath in YAML_DIR.rglob("*.y*ml"):
        try:
            content = filepath.read_text(encoding='utf-8')
            for test_name in test_names:
                if f"{test_name}:" in content:
                    # 使用 as_posix 保证路径在 Windows 上也能正确被 pytest 解析
                    rel_path = filepath.relative_to(BASE_DIR).as_posix()
                    found_yamls.add(rel_path)
        except Exception as e:
            print(f"⚠️ 读取文件 {filepath} 时出错: {e}")
                    
    return list(found_yamls)

def prompt_user_selection(options: List[str]) -> str:
    """
    如果找到了多个 YAML 文件，提示用户选择一个或者全部执行
    """
    print("\n⚠️ 警告: 找到了多个 YAML 配置文件:")
    for idx, opt in enumerate(options, 1):
        print(f"  [{idx}] {opt}")
    
    all_option_idx = len(options) + 1
    print(f"  [{all_option_idx}] ⚡ 全部执行 (不在命令行指定单个 YAML，交由 pytest -k 自动在所有文件中匹配)")
    
    while True:
        try:
            choice = input(f"\n👉 请选择要执行的配置 (1-{all_option_idx}): ")
            choice_idx = int(choice.strip()) - 1
            if 0 <= choice_idx < len(options):
                return options[choice_idx]
            if choice_idx == len(options):
                return "ALL"
            
            print(f"❌ 无效的选择，请输入 1 到 {all_option_idx} 之间的数字。")
        except ValueError:
            print("❌ 无效的输入，请输入数字。")
        except KeyboardInterrupt:
            print("\n🛑 操作被用户取消。")
            sys.exit(1)

def interactive_directory_selection(base_dir: Path) -> Tuple[str, Path]:
    """
    提供一个交互式的层级菜单，让用户选择要执行的目录或具体的 YAML 文件
    """
    current_dir = base_dir
    
    while True:
        print(f"\n📂 当前目录: {current_dir}")
        try:
            items = sorted(current_dir.iterdir(), key=lambda x: (x.is_file(), x.name))
        except Exception as e:
            print(f"❌ 读取目录失败: {e}")
            sys.exit(1)
            
        dirs = [item for item in items if item.is_dir()]
        yamls = [item for item in items if item.is_file() and item.suffix in ('.yaml', '.yml')]
                
        options = []
        
        if dirs or yamls:
            options.append({"label": "⚡ 执行当前目录 (及子目录) 下的所有测试", "type": "execute_all", "path": current_dir})
            
        if current_dir != base_dir:
            options.append({"label": "🔙 返回上一级目录", "type": "back", "path": current_dir.parent})
            
        for d in dirs:
            options.append({"label": f"📁 {d.name}/", "type": "dir", "path": d})
            
        for y in yamls:
            options.append({"label": f"📄 {y.name}", "type": "file", "path": y})
            
        if not options:
            print("⚠️ 此目录为空或没有 YAML 文件。")
            current_dir = current_dir.parent
            continue
            
        print("\n请选择:")
        for idx, opt in enumerate(options, 1):
            print(f"  [{idx}] {opt['label']}")
            
        try:
            choice = input(f"\n👉 请输入序号 (1-{len(options)}) 或按 Ctrl+C 退出: ")
            choice_idx = int(choice.strip()) - 1
            if 0 <= choice_idx < len(options):
                selected = options[choice_idx]
                
                if selected["type"] in ("dir", "back"):
                    current_dir = selected["path"]
                else:
                    return selected["type"], selected["path"]
            else:
                print(f"❌ 无效的选择，请输入 1 到 {len(options)} 之间的数字。")
        except ValueError:
            print("❌ 无效的输入，请输入数字。")
        except KeyboardInterrupt:
            print("\n🛑 操作被用户取消。")
            sys.exit(1)

def interactive_test_case_selection(yaml_rel_path: str) -> str:
    """
    提供一个交互式的菜单，让用户选择要执行的测试用例（支持多选或全选）
    """
    test_cases = get_test_cases_from_yaml(yaml_rel_path)
    
    if not test_cases:
        print(f"\n⚠️ 配置文件 {yaml_rel_path} 中未找到有效的测试用例，将尝试执行整个文件。")
        return ""
        
    print(f"\n📄 已选择文件: {yaml_rel_path}")
    print(f"🔍 找到以下测试用例:")
    
    options = [{"label": "⚡ 全部执行", "value": "ALL"}]
    for tc in test_cases:
        desc_str = f" - {tc['desc']}" if tc["desc"] else ""
        options.append({"label": f"🧪 {tc['name']}{desc_str}", "value": tc['name']})
        
    for idx, opt in enumerate(options, 1):
        print(f"  [{idx}] {opt['label']}")
        
    while True:
        try:
            choice_input = input(f"\n👉 请输入序号选择测试用例 (例如 '1', '2,4', '2-4') 或按 Ctrl+C 退出: ")
            raw_parts = re.split(r'[,\s]+', choice_input.strip())
            selected_indices = set()
            
            for part in raw_parts:
                if not part:
                    continue
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    selected_indices.update(range(start - 1, end))
                else:
                    selected_indices.add(int(part) - 1)
            
            if not selected_indices:
                print("❌ 无效的输入。")
                continue
                
            if any(i < 0 or i >= len(options) for i in selected_indices):
                print(f"❌ 包含了无效的序号。请确保输入的序号在 1 到 {len(options)} 之间。")
                continue
                
            selected_options = [options[i] for i in sorted(list(selected_indices))]
            
            if any(opt["value"] == "ALL" for opt in selected_options):
                return ""
                
            return " or ".join(opt["value"] for opt in selected_options)
            
        except ValueError:
            print("❌ 无效的输入格式，请输入数字组合 (如 '1', '2,4', '2-4')。")
        except KeyboardInterrupt:
            print("\n🛑 操作被用户取消。")
            sys.exit(1)

def parse_args() -> Tuple[List[str], str, List[str]]:
    """
    解析命令行参数，分离出测试用例名称、逻辑操作符和额外的 pytest 参数
    """
    args = sys.argv[1:]
    test_names = []
    logic_op = "or"
    additional_args = []
    
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--or":
            logic_op = "or"
            i += 1
        elif arg.startswith("-"):
            additional_args = args[i:]
            break
        else:
            test_names.append(arg)
            i += 1
            
    return test_names, logic_op, additional_args

def main():
    if len(sys.argv) < 2:
        print("💡 未提供测试用例名称，进入交互式层级选择模式...")
        if not YAML_DIR.exists():
            print(f"❌ 错误: 找不到基础 YAML 目录 {YAML_DIR}")
            sys.exit(1)
            
        sel_type, sel_path = interactive_directory_selection(YAML_DIR)
        
        if sel_type == "file":
            rel_path = sel_path.relative_to(BASE_DIR).as_posix()
            yaml_paths = [rel_path]
            k_expression = interactive_test_case_selection(rel_path)
        else: # dir_all
            all_yamls = [p.relative_to(BASE_DIR).as_posix() for p in sel_path.rglob("*.y*ml")]
            if not all_yamls:
                print(f"❌ 目录 {sel_path} 下没有找到任何 YAML 文件。")
                sys.exit(1)
            yaml_paths = all_yamls
            k_expression = ""
            
        print(f"\n✅ 选定执行 {len(yaml_paths)} 个 YAML 配置文件。")
        success = execute_yamls(yaml_paths, k_expression, [])
        sys.exit(0 if success else 1)
        
    else:
        test_names, logic_op, additional_args = parse_args()

        if not test_names:
            print("❌ 未提供任何测试用例名称。")
            sys.exit(1)

        k_expression = f" {logic_op} ".join(test_names)

        print(f"🔍 正在解析，提取到测试用例: {test_names}，连接逻辑: {logic_op}")
        print(f"🔍 生成的 -k 表达式: '{k_expression}'")
        print(f"🔍 正在搜索对应的 YAML 配置文件...")
        
        yaml_paths = find_yaml_for_tests(test_names)

        if not yaml_paths:
            print("❌ 未能在 All_YAML/ 目录下找到包含以上测试用例的配置文件。")
            sys.exit(1)

        if len(yaml_paths) > 1:
            yaml_path = prompt_user_selection(yaml_paths)
        else:
            yaml_path = yaml_paths[0]

        if yaml_path == "ALL":
            print(f"\n{'=' * 60}")
            print(f"🚀 选定配置: ⚡ 全部执行 (将依次运行以下 {len(yaml_paths)} 个配置文件)")
            for idx, p in enumerate(yaml_paths, 1):
                print(f"   [{idx}] {p}")
            print(f"{'=' * 60}\n")
            
            success = execute_yamls(yaml_paths, k_expression, additional_args)
                    
            print(f"\n{'=' * 60}")
            if not success:
                print("⚠️  全部执行完成，但部分测试存在错误。请检查上方日志。")
                print(f"{'=' * 60}")
                sys.exit(1)
            else:
                print("🎉 所有测试均已成功执行完成！")
                print(f"{'=' * 60}")
                sys.exit(0)
        else:
            print(f"\n✅ 选定配置: {yaml_path}")
            success = execute_yamls([yaml_path], k_expression, additional_args)
            sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

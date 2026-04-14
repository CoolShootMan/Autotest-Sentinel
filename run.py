#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
Filename         : run.py
Description      : 自动查找测试用例所在的 YAML 文件并运行 pytest
Time             : 2024/04/14
"""

import os
import sys
import subprocess
import re

def get_test_cases_from_yaml(yaml_path):
    """
    从指定的 yaml 文件中解析出所有的测试用例名称
    假设测试用例的定义以 test 且顶格开头，如 'testT4718:'
    """
    test_cases = []
    # 转换为绝对路径读取
    abs_path = os.path.join("test_case", "UI", "Test_Katana", yaml_path)
    if not os.path.exists(abs_path):
        return test_cases
        
    try:
        with open(abs_path, 'r', encoding='utf-8') as f:
            for line in f:
                # 匹配顶格写并且以 test 开头，以冒号结尾的行
                match = re.match(r'^(test[a-zA-Z0-9_]+):', line)
                if match:
                    test_cases.append(match.group(1))
    except Exception as e:
        print(f"⚠️ 读取配置文件 {abs_path} 时出错: {e}")
        
    return test_cases

def run_single_pytest(test_name, yaml_path, additional_args):
    """
    执行单个 pytest 命令，并返回执行结果状态
    """
    print(f"\n{'*' * 50}")
    print(f"🧪 开始执行测试用例: {test_name}")
    print(f"{'*' * 50}\n")
    
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "test_case/UI/Test_Katana/test_ui.py",
        "--yaml", yaml_path,
        "-k", test_name
    ]
    
    if not additional_args:
        cmd.extend(["--headed", "-v"])
    else:
        cmd.extend(additional_args)
        
    print(f"💻 执行命令: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, check=False)
        print(f"\n{'-' * 50}")
        if result.returncode != 0:
            print(f"❌ 用例 {test_name} 执行失败！")
            print(f"{'-' * 50}\n")
            return False
        else:
            print(f"✅ 用例 {test_name} 执行成功！")
            print(f"{'-' * 50}\n")
            return True
    except KeyboardInterrupt:
        print("\n🛑 测试执行被用户中断。")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 执行命令时出错: {e}")
        return False

def execute_yamls(yaml_paths, k_expression, additional_args):
    """
    按配置文件执行测试。如果 k_expression 为空，则找出 yaml 内所有用例依次执行。
    """
    has_error = False
    
    for i, p in enumerate(yaml_paths, 1):
        print(f"\n{'#' * 60}")
        print(f"▶️  开始处理配置文件 [{i}/{len(yaml_paths)}]: {p}")
        print(f"{'#' * 60}")
        
        # 如果未指定特定的用例表达式，则解析 YAML 中的所有用例，挨个执行
        if not k_expression:
            test_cases = get_test_cases_from_yaml(p)
            if not test_cases:
                print(f"⚠️ 未在 {p} 中找到有效的测试用例 (以 test 开头)。将尝试直接执行整个文件。")
                success = run_single_pytest("", p, additional_args)
                if not success:
                    has_error = True
            else:
                print(f"🔍 在该配置文件中找到 {len(test_cases)} 个用例: {', '.join(test_cases)}")
                for idx, tc in enumerate(test_cases, 1):
                    print(f"\n⏳ 进度: 配置文件 [{i}/{len(yaml_paths)}] -> 用例 [{idx}/{len(test_cases)}]")
                    success = run_single_pytest(tc, p, additional_args)
                    if not success:
                        has_error = True
        else:
            # 如果指定了用例表达式，直接按原逻辑执行该表达式匹配的用例
            success = run_single_pytest(k_expression, p, additional_args)
            if not success:
                has_error = True
                
    return not has_error

def find_yaml_for_tests(test_names):
    """
    在 All_YAML 目录下搜索包含指定测试用例名称的 YAML 文件
    """
    base_dir = os.path.join("test_case", "UI", "Test_Katana", "All_YAML")
    if not os.path.exists(base_dir):
        print(f"❌ 错误: 找不到目录 {base_dir}")
        return None
        
    found_yamls = set()
    
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".yaml") or file.endswith(".yml"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # 检查是否包含任何一个测试用例名
                        for test_name in test_names:
                            if f"{test_name}:" in content:
                                katana_dir = os.path.join("test_case", "UI", "Test_Katana")
                                rel_path = os.path.relpath(filepath, katana_dir)
                                found_yamls.add(rel_path.replace('\\', '/'))
                except Exception as e:
                    print(f"⚠️ 读取文件 {filepath} 时出错: {e}")
                    
    return list(found_yamls)

def prompt_user_selection(options):
    """
    如果找到了多个 YAML 文件，提示用户选择一个或者全部执行
    """
    print("\n⚠️ 警告: 找到了多个 YAML 配置文件:")
    for idx, opt in enumerate(options):
        print(f"  [{idx + 1}] {opt}")
    
    all_option_idx = len(options) + 1
    print(f"  [{all_option_idx}] ⚡ 全部执行 (不在命令行指定单个 YAML，交由 pytest -k 自动在所有文件中匹配)")
    
    while True:
        try:
            choice = input(f"\n👉 请选择要执行的配置 (1-{all_option_idx}): ")
            choice_idx = int(choice.strip()) - 1
            if 0 <= choice_idx < len(options):
                return options[choice_idx]
            elif choice_idx == len(options):
                return "ALL"
            else:
                print(f"❌ 无效的选择，请输入 1 到 {all_option_idx} 之间的数字。")
        except ValueError:
            print("❌ 无效的输入，请输入数字。")
        except KeyboardInterrupt:
            print("\n🛑 操作被用户取消。")
            sys.exit(1)

def interactive_directory_selection(base_dir):
    """
    提供一个交互式的层级菜单，让用户选择要执行的目录或具体的 YAML 文件
    """
    current_dir = base_dir
    
    while True:
        print(f"\n📂 当前目录: {current_dir}")
        try:
            items = sorted(os.listdir(current_dir))
        except Exception as e:
            print(f"❌ 读取目录失败: {e}")
            sys.exit(1)
            
        # 过滤出目录和 yaml 文件
        dirs = []
        yamls = []
        for item in items:
            item_path = os.path.join(current_dir, item)
            if os.path.isdir(item_path):
                dirs.append(item)
            elif item.endswith('.yaml') or item.endswith('.yml'):
                yamls.append(item)
                
        options = []
        
        # 选项1: 执行当前目录下的所有文件 (如果有 YAML 或子目录)
        if dirs or yamls:
            options.append({"label": "⚡ 执行当前目录 (及子目录) 下的所有测试", "type": "execute_all", "path": current_dir})
            
        # 选项2: 返回上一级 (如果不是 base_dir)
        if current_dir != base_dir:
            options.append({"label": "🔙 返回上一级目录", "type": "back", "path": os.path.dirname(current_dir)})
            
        # 列出目录
        for d in dirs:
            options.append({"label": f"📁 {d}/", "type": "dir", "path": os.path.join(current_dir, d)})
            
        # 列出文件
        for y in yamls:
            options.append({"label": f"📄 {y}", "type": "file", "path": os.path.join(current_dir, y)})
            
        if not options:
            print("⚠️ 此目录为空或没有 YAML 文件。")
            current_dir = os.path.dirname(current_dir)
            continue
            
        print("\n请选择:")
        for idx, opt in enumerate(options, 1):
            print(f"  [{idx}] {opt['label']}")
            
        try:
            choice = input(f"\n👉 请输入序号 (1-{len(options)}) 或按 Ctrl+C 退出: ")
            choice_idx = int(choice.strip()) - 1
            if 0 <= choice_idx < len(options):
                selected = options[choice_idx]
                
                if selected["type"] == "dir":
                    current_dir = selected["path"]
                elif selected["type"] == "back":
                    current_dir = selected["path"]
                elif selected["type"] == "file":
                    # 选择了一个具体文件，直接返回该文件路径及标识
                    return "file", selected["path"]
                elif selected["type"] == "execute_all":
                    # 选择了执行整个目录，返回该目录路径及标识
                    return "dir_all", selected["path"]
            else:
                print(f"❌ 无效的选择，请输入 1 到 {len(options)} 之间的数字。")
        except ValueError:
            print("❌ 无效的输入，请输入数字。")
        except KeyboardInterrupt:
            print("\n🛑 操作被用户取消。")
            sys.exit(1)

def interactive_test_case_selection(yaml_rel_path):
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
        options.append({"label": f"🧪 {tc}", "value": tc})
        
    for idx, opt in enumerate(options, 1):
        print(f"  [{idx}] {opt['label']}")
        
    while True:
        try:
            choice_input = input(f"\n👉 请输入序号选择测试用例 (例如 '1', '2,4', '2-4') 或按 Ctrl+C 退出: ")
            
            # 解析用户的输入 (支持逗号分隔、空格分隔和横线范围)
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
                
            invalid_indices = [i for i in selected_indices if i < 0 or i >= len(options)]
            if invalid_indices:
                print(f"❌ 包含了无效的序号。请确保输入的序号在 1 到 {len(options)} 之间。")
                continue
                
            selected_options = [options[i] for i in sorted(list(selected_indices))]
            
            # 如果选择了 "全部执行"，则直接返回空字符串，交由 execute_yamls 自动执行全部
            if any(opt["value"] == "ALL" for opt in selected_options):
                return ""
                
            # 提取选中的测试用例名称并拼接为 -k 表达式
            selected_tcs = [opt["value"] for opt in selected_options]
            return " or ".join(selected_tcs)
            
        except ValueError:
            print("❌ 无效的输入格式，请输入数字组合 (如 '1', '2,4', '2-4')。")
        except KeyboardInterrupt:
            print("\n🛑 操作被用户取消。")
            sys.exit(1)

def get_all_yamls_in_dir(directory):
    """
    获取指定目录下的所有 yaml 文件路径
    """
    yamls = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.yaml') or file.endswith('.yml'):
                yamls.append(os.path.join(root, file))
    return yamls

def main():
    base_yaml_dir = os.path.join("test_case", "UI", "Test_Katana", "All_YAML")
    katana_dir = os.path.join("test_case", "UI", "Test_Katana")
    
    if len(sys.argv) < 2:
        print("💡 未提供测试用例名称，进入交互式层级选择模式...")
        if not os.path.exists(base_yaml_dir):
            print(f"❌ 错误: 找不到基础 YAML 目录 {base_yaml_dir}")
            sys.exit(1)
            
        sel_type, sel_path = interactive_directory_selection(base_yaml_dir)
        
        yaml_paths = []
        if sel_type == "file":
            rel_path = os.path.relpath(sel_path, katana_dir).replace('\\', '/')
            yaml_paths = [rel_path]
            # 在选择单个文件后，提供用例多选功能
            k_expression = interactive_test_case_selection(rel_path)
        elif sel_type == "dir_all":
            all_yamls = get_all_yamls_in_dir(sel_path)
            if not all_yamls:
                print(f"❌ 目录 {sel_path} 下没有找到任何 YAML 文件。")
                sys.exit(1)
            yaml_paths = [os.path.relpath(p, katana_dir).replace('\\', '/') for p in all_yamls]
            k_expression = "" # 不过滤，执行所有文件里的所有用例
            
        additional_args = []
        # 去掉重写，统一将多路径交给 execute_yamls 处理
        
        # 统一执行入口，跳过后续的老代码逻辑
        print(f"\n✅ 选定执行 {len(yaml_paths)} 个 YAML 配置文件。")
        success = execute_yamls(yaml_paths, k_expression, additional_args)
        if not success:
            sys.exit(1)
        else:
            sys.exit(0)
            
    else:
        args = sys.argv[1:]
        
        # 分离出测试用例名称、逻辑操作符和额外的 pytest 参数
        test_names = []
        logic_op = "or" # 默认使用 or 连接多个用例
        additional_args = []
        
        i = 0
        while i < len(args):
            arg = args[i]
            if arg == "--or":
                logic_op = "or"
                i += 1
            elif arg.startswith("-"):
                # 遇到其他 - 开头的参数，认为后面的都是附加的 pytest 参数
                additional_args = args[i:]
                break
            else:
                test_names.append(arg)
                i += 1

        if not test_names:
            print("❌ 未提供任何测试用例名称。")
            sys.exit(1)

        # 构造 -k 表达式
        # 如果用例名中包含空格或短横线，可能需要更复杂的拼接逻辑，但这里为了简单直接拼接
        # 如果包含多个用例，需要用引号包裹（虽然 pytest 接收参数列表不需要）
        k_expression = f" {logic_op} ".join(test_names)

        print(f"🔍 正在解析，提取到测试用例: {test_names}，连接逻辑: {logic_op}")
        print(f"🔍 生成的 -k 表达式: '{k_expression}'")
        print(f"🔍 正在搜索对应的 YAML 配置文件...")
        yaml_paths = find_yaml_for_tests(test_names)

        if not yaml_paths:
            print(f"❌ 未能在 All_YAML/ 目录下找到包含以上测试用例的配置文件。")
            sys.exit(1)

        # 如果有多个，提示用户选择；如果只有一个，直接使用
        if len(yaml_paths) > 1:
            yaml_path = prompt_user_selection(yaml_paths)
        else:
            yaml_path = yaml_paths[0]

    # 如果用户选择“全部执行”，我们需要循环遍历所有的 yaml 文件来执行 pytest
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
        
        # 构建基础的 pytest 命令
        success = execute_yamls([yaml_path], k_expression, additional_args)
        if not success:
            sys.exit(1)
            
if __name__ == "__main__":
    main()

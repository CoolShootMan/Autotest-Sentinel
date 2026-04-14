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

def main():
    if len(sys.argv) < 2:
        print("💡 用法: python run.py <test_name1> [test_name2 ...] [--or] [附加的 pytest 参数]")
        print("   示例1: python run.py testT4718")
        print("   示例2: python run.py testT4718 testT4718_guest --or --headed -v")
        sys.exit(1)

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
        print(f"\n✅ 选定配置: ⚡ 全部执行 (分别运行以下配置文件)")
        for p in yaml_paths:
            print(f"   - {p}")
            
        print("-" * 50)
        
        has_error = False
        for i, p in enumerate(yaml_paths, 1):
            print(f"\n🚀 [{i}/{len(yaml_paths)}] 即将运行配置: {p}")
            cmd = [
                sys.executable,
                "-m",
                "pytest",
                "test_case/UI/Test_Katana/test_ui.py",
                "-k", k_expression,
                "--yaml", p
            ]
            if not additional_args:
                cmd.extend(["--headed", "-v"])
            else:
                cmd.extend(additional_args)
                
            print(f"   {' '.join(cmd)}\n")
            try:
                result = subprocess.run(cmd, check=False)
                if result.returncode != 0:
                    has_error = True
            except KeyboardInterrupt:
                print("\n🛑 测试执行被用户中断。")
                sys.exit(1)
            except Exception as e:
                print(f"\n❌ 执行命令时出错: {e}")
                has_error = True
                
        if has_error:
            print("\n⚠️ 全部执行完成，但部分测试可能存在错误。")
            sys.exit(1)
        else:
            print("\n🎉 全部执行成功完成！")
            sys.exit(0)
    else:
        print(f"\n✅ 选定配置: {yaml_path}")
        
        # 构建基础的 pytest 命令
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            "test_case/UI/Test_Katana/test_ui.py",
            "-k", k_expression,
            "--yaml", yaml_path
        ]
        
        # 如果没有提供额外的参数，默认加上 --headed 和 -v
        if not additional_args:
            cmd.extend(["--headed", "-v"])
        else:
            cmd.extend(additional_args)

        print(f"🚀 即将运行命令:\n   {' '.join(cmd)}\n")
        print("-" * 50)
        
        # 执行命令
        try:
            subprocess.run(cmd, check=False)
        except KeyboardInterrupt:
            print("\n🛑 测试执行被用户中断。")
        except Exception as e:
            print(f"\n❌ 执行命令时出错: {e}")

if __name__ == "__main__":
    main()

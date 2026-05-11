#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
Filename         : runner.py
Description      : Auto-locate YAML files containing test cases and run pytest
Time             : 2024/04/14
"""

import sys
import os
import subprocess
import re
from pathlib import Path
from typing import List, Dict, Tuple, Set
from dotenv import load_dotenv

# Load .env file from project root (does not override existing environment variables)
load_dotenv(Path(__file__).resolve().parent / ".env")

# Define constant paths
BASE_DIR = Path("test_case/UI/Test_Katana")
YAML_DIR = BASE_DIR / "All_YAML"
TEST_FILE = BASE_DIR / "test_ui.py"

def get_test_cases_from_yaml(yaml_path: str) -> List[Dict[str, str]]:
    """
    Parse all test case names and descriptions from the specified yaml file.
    Assumes test case definitions start at column 0 with 'test', e.g. 'testT4718:'
    The next line may be '  description: "xxx"'
    Returns a list of dicts: {"name": "test_name", "desc": "description"}
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
        print(f"⚠️ Error reading config file {abs_path}: {e}")
        
    return test_cases

def run_single_pytest(test_name: str, yaml_path: str, additional_args: List[str]) -> bool:
    """
    Execute a single pytest command and return the execution result status.
    """
    print(f"\n{'*' * 50}")
    print(f"🧪 Running test case: {test_name}" if test_name else "🧪 Running entire file")
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
        
    print(f"💻 Command: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, check=False)
        print(f"\n{'-' * 50}")
        if result.returncode != 0:
            print(f"❌ Test case '{test_name or 'all'}' failed!")
            print(f"{'-' * 50}\n")
            return False
        
        print(f"✅ Test case '{test_name or 'all'}' passed!")
        print(f"{'-' * 50}\n")
        return True
    except KeyboardInterrupt:
        print("\n🛑 Test execution interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error executing command: {e}")
        return False

def execute_yamls(yaml_paths: List[str], k_expression: str, additional_args: List[str]) -> bool:
    """
    Execute tests by config file. If k_expression is empty, find all cases in yaml and run them one by one.
    """
    has_error = False
    
    for i, p in enumerate(yaml_paths, 1):
        print(f"\n{'#' * 60}")
        print(f"▶️  Processing config file [{i}/{len(yaml_paths)}]: {p}")
        print(f"{'#' * 60}")
        
        if not k_expression:
            test_cases = get_test_cases_from_yaml(p)
            if not test_cases:
                print(f"⚠️ No valid test cases (starting with 'test') found in {p}. Attempting to run the entire file.")
                if not run_single_pytest("", p, additional_args):
                    has_error = True
            else:
                names = [tc['name'] for tc in test_cases]
                print(f"🔍 Found {len(test_cases)} test case(s) in this file: {', '.join(names)}")
                for idx, tc in enumerate(test_cases, 1):
                    print(f"\n⏳ Progress: config [{i}/{len(yaml_paths)}] -> case [{idx}/{len(test_cases)}]")
                    if not run_single_pytest(tc['name'], p, additional_args):
                        has_error = True
        else:
            if not run_single_pytest(k_expression, p, additional_args):
                has_error = True
                
    return not has_error

def find_yaml_for_tests(test_names: List[str]) -> List[str]:
    """
    Search All_YAML directory for YAML files containing the specified test case names.
    """
    if not YAML_DIR.exists():
        print(f"❌ Error: Directory not found: {YAML_DIR}")
        return []
        
    found_yamls: Set[str] = set()
    
    for filepath in YAML_DIR.rglob("*.y*ml"):
        try:
            content = filepath.read_text(encoding='utf-8')
            for test_name in test_names:
                if f"{test_name}:" in content:
                    # Use as_posix to ensure path is correctly parsed by pytest on Windows
                    rel_path = filepath.relative_to(BASE_DIR).as_posix()
                    found_yamls.add(rel_path)
        except Exception as e:
            print(f"⚠️ Error reading file {filepath}: {e}")
                    
    return list(found_yamls)

def prompt_user_selection(options: List[str]) -> str:
    """
    If multiple YAML files are found, prompt the user to select one or run all.
    """
    print("\n⚠️ Warning: Multiple YAML config files found:")
    for idx, opt in enumerate(options, 1):
        print(f"  [{idx}] {opt}")
    
    all_option_idx = len(options) + 1
    print(f"  [{all_option_idx}] ⚡ Run all (do not specify a single YAML on command line, let pytest -k match across all files)")
    
    while True:
        try:
            choice = input(f"\n👉 Select config to run (1-{all_option_idx}): ")
            choice_idx = int(choice.strip()) - 1
            if 0 <= choice_idx < len(options):
                return options[choice_idx]
            if choice_idx == len(options):
                return "ALL"
            
            print(f"❌ Invalid selection. Please enter a number between 1 and {all_option_idx}.")
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\n🛑 Operation cancelled by user.")
            sys.exit(1)

def interactive_directory_selection(base_dir: Path) -> Tuple[str, Path]:
    """
    Provide an interactive hierarchical menu for selecting a directory or specific YAML file to run.
    """
    current_dir = base_dir
    
    while True:
        print(f"\n📂 Current directory: {current_dir}")
        try:
            items = sorted(current_dir.iterdir(), key=lambda x: (x.is_file(), x.name))
        except Exception as e:
            print(f"❌ Failed to read directory: {e}")
            sys.exit(1)
            
        dirs = [item for item in items if item.is_dir()]
        yamls = [item for item in items if item.is_file() and item.suffix in ('.yaml', '.yml')]
                
        options = []
        
        if dirs or yamls:
            options.append({"label": "⚡ Run all tests in current directory (and subdirectories)", "type": "execute_all", "path": current_dir})
            
        if current_dir != base_dir:
            options.append({"label": "🔙 Go back to parent directory", "type": "back", "path": current_dir.parent})
            
        for d in dirs:
            options.append({"label": f"📁 {d.name}/", "type": "dir", "path": d})
            
        for y in yamls:
            options.append({"label": f"📄 {y.name}", "type": "file", "path": y})
            
        if not options:
            print("⚠️ This directory is empty or has no YAML files.")
            current_dir = current_dir.parent
            continue
            
        print("\nSelect:")
        for idx, opt in enumerate(options, 1):
            print(f"  [{idx}] {opt['label']}")
            
        try:
            choice = input(f"\n👉 Enter number (1-{len(options)}) or Ctrl+C to exit: ")
            choice_idx = int(choice.strip()) - 1
            if 0 <= choice_idx < len(options):
                selected = options[choice_idx]
                
                if selected["type"] in ("dir", "back"):
                    current_dir = selected["path"]
                else:
                    return selected["type"], selected["path"]
            else:
                print(f"❌ Invalid selection. Please enter a number between 1 and {len(options)}.")
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\n🛑 Operation cancelled by user.")
            sys.exit(1)

def interactive_test_case_selection(yaml_rel_path: str) -> str:
    """
    Provide an interactive menu for selecting test cases to run (supports multi-select or run all).
    """
    test_cases = get_test_cases_from_yaml(yaml_rel_path)
    
    if not test_cases:
        print(f"\n⚠️ No valid test cases found in {yaml_rel_path}. Will attempt to run the entire file.")
        return ""
        
    print(f"\n📄 Selected file: {yaml_rel_path}")
    print(f"🔍 Found the following test cases:")
    
    options = [{"label": "⚡ Run all", "value": "ALL"}]
    for tc in test_cases:
        desc_str = f" - {tc['desc']}" if tc["desc"] else ""
        options.append({"label": f"🧪 {tc['name']}{desc_str}", "value": tc['name']})
        
    for idx, opt in enumerate(options, 1):
        print(f"  [{idx}] {opt['label']}")
        
    while True:
        try:
            choice_input = input(f"\n👉 Enter number to select test case (e.g. '1', '2,4', '2-4') or Ctrl+C to exit: ")
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
                print("❌ Invalid input.")
                continue
                
            if any(i < 0 or i >= len(options) for i in selected_indices):
                print(f"❌ Contains invalid index. Please enter numbers between 1 and {len(options)}.")
                continue
                
            selected_options = [options[i] for i in sorted(list(selected_indices))]
            
            if any(opt["value"] == "ALL" for opt in selected_options):
                return ""
                
            return " or ".join(opt["value"] for opt in selected_options)
            
        except ValueError:
            print("❌ Invalid input format. Please enter a number combination (e.g. '1', '2,4', '2-4').")
        except KeyboardInterrupt:
            print("\n🛑 Operation cancelled by user.")
            sys.exit(1)

def parse_args() -> Tuple[List[str], str, List[str]]:
    """
    Parse command-line arguments, separating test case names, logic operator, and extra pytest args.
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
    # Ensure subprocess can also access BASE_URL (.env already loaded at module level)
    if "BASE_URL" not in os.environ:
        os.environ["BASE_URL"] = "https://release.pear.us"

    if len(sys.argv) < 2:
        print("💡 No test case name provided. Entering interactive directory selection mode...")
        if not YAML_DIR.exists():
            print(f"❌ Error: Base YAML directory not found: {YAML_DIR}")
            sys.exit(1)
            
        sel_type, sel_path = interactive_directory_selection(YAML_DIR)
        
        if sel_type == "file":
            rel_path = sel_path.relative_to(BASE_DIR).as_posix()
            yaml_paths = [rel_path]
            k_expression = interactive_test_case_selection(rel_path)
        else: # dir_all
            all_yamls = [p.relative_to(BASE_DIR).as_posix() for p in sel_path.rglob("*.y*ml")]
            if not all_yamls:
                print(f"❌ No YAML files found in directory {sel_path}.")
                sys.exit(1)
            yaml_paths = all_yamls
            k_expression = ""
            
        print(f"\n✅ Selected {len(yaml_paths)} YAML config file(s) to run.")
        success = execute_yamls(yaml_paths, k_expression, [])
        sys.exit(0 if success else 1)
        
    else:
        test_names, logic_op, additional_args = parse_args()

        if not test_names:
            print("❌ No test case names provided.")
            sys.exit(1)

        k_expression = f" {logic_op} ".join(test_names)

        print(f"🔍 Parsed test cases: {test_names}, logic operator: {logic_op}")
        print(f"🔍 Generated -k expression: '{k_expression}'")
        print(f"🔍 Searching for matching YAML config files...")
        
        yaml_paths = find_yaml_for_tests(test_names)

        if not yaml_paths:
            print("❌ No config files containing the above test cases found in All_YAML/.")
            sys.exit(1)

        if len(yaml_paths) > 1:
            yaml_path = prompt_user_selection(yaml_paths)
        else:
            yaml_path = yaml_paths[0]

        if yaml_path == "ALL":
            print(f"\n{'=' * 60}")
            print(f"🚀 Selected: ⚡ Run all ({len(yaml_paths)} config files)")
            for idx, p in enumerate(yaml_paths, 1):
                print(f"   [{idx}] {p}")
            print(f"{'=' * 60}\n")
            
            success = execute_yamls(yaml_paths, k_expression, additional_args)
                    
            print(f"\n{'=' * 60}")
            if not success:
                print("⚠️  All runs completed, but some tests failed. Check logs above.")
                print(f"{'=' * 60}")
                sys.exit(1)
            else:
                print("🎉 All tests completed successfully!")
                print(f"{'=' * 60}")
                sys.exit(0)
        else:
            print(f"\n✅ Selected config: {yaml_path}")
            success = execute_yamls([yaml_path], k_expression, additional_args)
            sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

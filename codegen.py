#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
Filename         : codegen.py
Description      : 快捷启动 Playwright codegen，支持交互式输入角色和环境参数来决定加载的 cookie，以及输入目标 URL。
"""

import sys
import subprocess
import os

def main():
    print("=========================================")
    print("🚀 欢迎使用 Playwright Codegen 快捷启动工具")
    print("=========================================")
    
    try:
        # 1. 交互式选择角色
        role_map = {"1": "partner", "2": "guest", "3": "co-seller"}
        role_choice = input("👤 请选择角色 (1: partner, 2: guest, 3: co-seller, q: 退出) [默认: 1]: ").strip().lower()
        
        if role_choice in ['q', 'quit']:
            print("👋 已退出启动程序。")
            sys.exit(0)
            
        role = role_map.get(role_choice, "partner")  # 默认为 partner
        is_guest = (role == "guest")
        
        # 2. 交互式选择环境（如果是 guest 则跳过）
        env = "release" # 默认值，防止未被赋值
        if not is_guest:
            env_map = {"1": "staging", "2": "release", "3": "prod"}
            env_choice = input("🌍 请选择环境 (1: staging, 2: release, 3: prod, q: 退出) [默认: 2]: ").strip().lower()
            
            if env_choice in ['q', 'quit']:
                print("👋 已退出启动程序。")
                sys.exit(0)
                
            env = env_map.get(env_choice, "release")  # 默认为 release
        
        # 3. 交互式获取 URL
        url = input("🔗 请输入要录制的网址 (直接回车可跳过, q: 退出): ").strip()
        
        if url.lower() in ['q', 'quit']:
            print("👋 已退出启动程序。")
            sys.exit(0)
            
    except KeyboardInterrupt:
        # 捕获 Ctrl+C，优雅退出
        print("\n👋 收到取消指令 (Ctrl+C)，已退出启动程序。")
        sys.exit(0)
    
    # 提取所有传入的其他参数
    args = sys.argv[1:]
    
    # 构建 codegen 命令
    cmd = [
        "playwright",
        "codegen"
    ]
    
    # 如果用户输入了 URL，添加到命令中
    if url:
        cmd.append(url)
    
    # 将可能传入的其他参数加入命令中
    cmd.extend(args)
    
    # 只有当不是 guest 角色时才附加 cookie 文件
    if not is_guest:
        # 根据角色和环境拼接 cookie 文件名
        # 例如: cookie_release.json 或 cookie_coseller_release.json
        if role == "partner":
            cookie_file = f"./test_case/UI/Test_Katana/cookie_{env}.json"
        else:
            # 对于 co-seller 等其他角色
            cookie_file = f"./test_case/UI/Test_Katana/cookie_coseller_{env}.json"
            
        # 检查 cookie 文件是否存在给出提示（非阻塞）
        if not os.path.exists(cookie_file):
            print(f"⚠️ 警告: Cookie 文件 {cookie_file} 不存在，可能导致无法正常加载登录状态。")
            
        cmd.append(f"--load-storage={cookie_file}")
        print(f"\n🚀 正在启动 Playwright Codegen (角色: {role}, 环境: {env}) 并加载 Cookie...")
    else:
        print(f"\n🚀 正在启动 Playwright Codegen (角色: guest)，不加载 Cookie...")
        
    print(f"💻 执行命令: {' '.join(cmd)}\n")
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n⏹️ 已停止录制")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    main()

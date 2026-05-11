#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
Filename         : codegen.py
Description      : Quick launcher for Playwright codegen. Supports interactive role and environment
                   selection to load the correct cookie, and accepts a target URL as input.
"""

import sys
import subprocess
import os

def main():
    print("=========================================")
    print("🚀 Welcome to Playwright Codegen Quick Launcher")
    print("=========================================")
    
    try:
        # 1. Interactively select role
        role_map = {"1": "partner", "2": "guest", "3": "co-seller"}
        role_choice = input("👤 Select role (1: partner, 2: guest, 3: co-seller, q: quit) [default: 1]: ").strip().lower()
        
        if role_choice in ['q', 'quit']:
            print("👋 Exiting launcher.")
            sys.exit(0)
            
        role = role_map.get(role_choice, "partner")  # Default to partner
        is_guest = (role == "guest")
        
        # 2. Interactively select environment (skipped for guest)
        env = "release"  # Default value to avoid unassigned variable
        if not is_guest:
            env_map = {"1": "staging", "2": "release", "3": "prod"}
            env_choice = input("🌍 Select environment (1: staging, 2: release, 3: prod, q: quit) [default: 2]: ").strip().lower()
            
            if env_choice in ['q', 'quit']:
                print("👋 Exiting launcher.")
                sys.exit(0)
                
            env = env_map.get(env_choice, "release")  # Default to release
        
        # 3. Interactively enter URL
        url = input("🔗 Enter URL to record (press Enter to skip, q: quit): ").strip()
        
        if url.lower() in ['q', 'quit']:
            print("👋 Exiting launcher.")
            sys.exit(0)
            
    except KeyboardInterrupt:
        # Gracefully handle Ctrl+C
        print("\n👋 Cancelled (Ctrl+C). Exiting launcher.")
        sys.exit(0)
    
    # Extract any extra arguments passed in
    args = sys.argv[1:]
    
    # Build the codegen command
    cmd = [
        "playwright",
        "codegen"
    ]
    
    # Append URL if provided
    if url:
        cmd.append(url)
    
    # Append any extra arguments
    cmd.extend(args)
    
    # Only attach cookie file for non-guest roles
    if not is_guest:
        # Build cookie filename from role and environment
        # e.g.: cookie_release.json or cookie_coseller_release.json
        if role == "partner":
            cookie_file = f"./test_case/UI/Test_Katana/cookie_{env}.json"
        else:
            # For co-seller and other roles
            cookie_file = f"./test_case/UI/Test_Katana/cookie_coseller_{env}.json"
            
        # Warn if cookie file is missing (non-blocking)
        if not os.path.exists(cookie_file):
            print(f"⚠️ Warning: Cookie file {cookie_file} not found. Login state may not load correctly.")
            
        cmd.append(f"--load-storage={cookie_file}")
        print(f"\n🚀 Starting Playwright Codegen (role: {role}, env: {env}) with Cookie...")
    else:
        print(f"\n🚀 Starting Playwright Codegen (role: guest) without Cookie...")
        
    print(f"💻 Command: {' '.join(cmd)}\n")
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n⏹️ Recording stopped")
    except Exception as e:
        print(f"❌ Launch failed: {e}")

if __name__ == "__main__":
    main()

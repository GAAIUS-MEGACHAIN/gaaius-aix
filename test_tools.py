#!/usr/bin/env python3
"""Test which tools are available"""

import subprocess
import shutil

tools = [
    ("cargo", "Rust/Tauri"),
    ("node", "Node.js"),
    ("npm", "NPM"),
    ("python", "Python"),
    ("flutter", "Flutter"),
    ("docker", "Docker"),
    ("git", "Git"),
    ("git-flow", "Git Flow"),
]

print("\n" + "="*70)
print("TOOL AVAILABILITY CHECK")
print("="*70 + "\n")

available = []
missing = []

for tool, name in tools:
    path = shutil.which(tool)
    if path:
        try:
            result = subprocess.run([tool, "--version"], capture_output=True, text=True, timeout=2)
            version = result.stdout.split('\n')[0]
            print(f"✓ {name:20} ({tool:15}) - {version}")
            available.append(tool)
        except:
            print(f"✗ {name:20} ({tool:15}) - FOUND but version check failed")
            available.append(tool)
    else:
        print(f"✗ {name:20} ({tool:15}) - NOT FOUND")
        missing.append(tool)

print("\n" + "="*70)
print(f"Available: {len(available)}/{len(tools)}")
print(f"Missing:   {len(missing)}/{len(tools)}")

if missing:
    print(f"\nMissing tools: {', '.join(missing)}")
    print("\nTo install:")
    print("  Rust/Cargo:  https://rustup.rs/")
    print("  Flutter:     https://flutter.dev/docs/get-started/install")
    print("  Docker:      https://docs.docker.com/desktop/install/windows/")

print("\n" + "="*70 + "\n")

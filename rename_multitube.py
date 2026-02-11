#!/usr/bin/env python3
import os
import glob

# Update server.py
server_file = os.path.join(os.path.dirname(__file__), 'backend', 'server.py')
if os.path.exists(server_file):
    with open(server_file, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace('/multitube/', '/videos/')
    content = content.replace('MultiTube', 'VIDEOS')
    with open(server_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Updated {server_file}")

# Update all markdown files
for md_file in glob.glob('*.md'):
    with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    content = content.replace('/multitube/', '/videos/')
    content = content.replace('MultiTube', 'VIDEOS')
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Updated {md_file}")

# Update Python files
for py_file in glob.glob('backend/*.py'):
    try:
        with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        content = content.replace('/multitube/', '/videos/')
        with open(py_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Updated {py_file}")
    except Exception as e:
        print(f"✗ Skipped {py_file}: {e}")

print("\n✅ Rename complete: MultiTube → VIDEOS, /multitube/ → /videos/")

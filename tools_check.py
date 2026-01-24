#!/usr/bin/env python
"""Check system tools and framework requirements"""
import sys
from pathlib import Path

sys.path.insert(0, 'backend')

from build_system_enterprise import SystemValidator

print('\n=== SYSTEM TOOLS STATUS ===\n')

# Check individual tools
print('Individual Tools:')
tools_check = {
    'Node.js': SystemValidator.check_nodejs(),
    'npm': SystemValidator.check_npm(),
    'Cargo (Rust)': SystemValidator.check_cargo(),
    'Docker': SystemValidator.check_docker(),
}

for tool, (found, version) in tools_check.items():
    status = 'INSTALLED' if found else 'MISSING'
    ver_str = f'v{version}' if version else 'N/A'
    print(f'  {tool:20} {status:12} {ver_str}')

# Framework readiness
print('\n\nFramework Readiness:')
frameworks = {
    'React': ['Node.js', 'npm'],
    'Angular': ['Node.js', 'npm'],
    'Vue': ['Node.js', 'npm'],
    'Next.js': ['Node.js', 'npm'],
    'Svelte': ['Node.js', 'npm'],
    'Tauri': ['Node.js', 'npm', 'Cargo'],
    'Electron': ['Node.js', 'npm'],
    'Flutter': ['Docker'],
}

all_ready = True
for fw, required in frameworks.items():
    env_ok, validation = SystemValidator.validate_environment(fw)
    missing = validation.get('missing_tools', [])
    status = 'READY' if env_ok else 'MISSING'
    
    if not env_ok:
        all_ready = False
        missing_str = ', '.join(missing)
    else:
        missing_str = 'All tools ready'
    
    print(f'  {fw:15} {status:10} - {missing_str}')

print('\n\n=== SUMMARY ===')
if all_ready:
    print('ALL FRAMEWORKS READY FOR BUILD')
else:
    print('SOME FRAMEWORKS MISSING DEPENDENCIES')
print()

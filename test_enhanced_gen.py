#!/usr/bin/env python
"""Quick test of enhanced file generator"""
import sys
sys.path.insert(0, 'f:\\gaaius-aiX\\gaaius-ai')

from backend.enhanced_file_generator import EnhancedFileGenerator

# Test generation
gen = EnhancedFileGenerator('QuickTest')
result = gen.generate_complete_project({})

print(f"\n{'='*70}")
print(f"✅ SUCCESS!")
print(f"{'='*70}")
print(f"Files created: {result['files_created']}")
print(f"Total lines: {result['total_lines']:,}")
print(f"Output dir: {result['output_dir']}")
print(f"{'='*70}\n")

import sys
import traceback

sys.path.insert(0, '.')

try:
    import server
    print("✓ Server imported successfully!")
except Exception as e:
    print(f"✗ Error importing server:")
    traceback.print_exc()

import sys
import traceback

sys.path.insert(0, '.')

print("=" * 60)
print("TESTING IMPORTS")
print("=" * 60)

try:
    print("\n1. Testing gaaius_builder imports...")
    from gaaius_builder import (
        APP_TEMPLATES, 
        generate_blueprint, 
        quality_gate_v2, 
        GAAIUS_BUILD_PROMPT_V2,
        BLUEPRINT_SYSTEM_PROMPT,
        get_template_code,
        get_available_templates,
        ComponentLibrary,
        LayoutEngine,
        StateManager,
        CacheManager,
        SchemaValidator,
        CodeGenerator,
        ProjectExporter,
        AIOrchestrator,
        IDEInfrastructure,
        GAIUSBuildPlatform,
        initialize_gaaius_build
    )
    print("✓ gaaius_builder imports OK")
except Exception as e:
    print(f"✗ gaaius_builder import failed:")
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n2. Testing gaaius_runtime imports...")
    from gaaius_runtime import (
        gaaius_runtime, 
        GaaiusProjectRuntime,
        generate_run_scripts,
        BUILD_STAGES,
        get_build_stages,
        calculate_total_lines,
        AGENT_ROLES,
        get_agent_pipeline
    )
    print("✓ gaaius_runtime imports OK")
except Exception as e:
    print(f"✗ gaaius_runtime import failed:")
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n3. Testing full server import...")
    import server
    print("✓ Server imported successfully!")
except Exception as e:
    print(f"✗ Server import failed:")
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("ALL TESTS PASSED!")
print("=" * 60)

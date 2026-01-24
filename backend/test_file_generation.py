"""
File Generation Test - Generate complete projects from agent outputs
"""

import asyncio
import json
from pathlib import Path
from dotenv import load_dotenv
from orchestrator import AgentOrchestrator
from file_generator import FileGenerator

load_dotenv()


async def test_full_project_generation():
    """Generate a complete project with all files"""
    
    print("\n" + "=" * 70)
    print("FULL PROJECT GENERATION TEST")
    print("=" * 70)
    
    # Step 1: Run orchestration
    print("\n[1/3] Running multi-agent pipeline...")
    orchestrator = AgentOrchestrator()
    
    try:
        outputs = await orchestrator.run_full_pipeline(
            user_prompt="Create a task management app with teams, real-time updates, file sharing, and analytics dashboard",
            complexity="standard"
        )
        
        print("[OK] Pipeline executed successfully")
        print(f"[*] Generated {len([k for k, v in outputs.items() if v])} agent outputs")
        
    except Exception as e:
        print(f"[✗] Pipeline failed: {e}")
        return
    
    # Step 2: Generate files
    print("\n[2/3] Generating project files...")
    
    try:
        generator = FileGenerator(
            project_name="task_management_platform",
            output_dir="./generated_projects"
        )
        
        project_path = generator.generate_from_orchestrator_output(outputs)
        print(f"[OK] Files generated at: {project_path}")
        
    except Exception as e:
        print(f"[✗] File generation failed: {e}")
        return
    
    # Step 3: Verify structure
    print("\n[3/3] Verifying project structure...")
    
    if Path(project_path).exists():
        def count_files(directory):
            return sum(1 for _ in Path(directory).rglob('*') if _.is_file())
        
        file_count = count_files(project_path)
        
        print(f"[OK] Project structure verified")
        print(f"[*] Total files: {file_count}")
        
        # Show directory structure
        print(f"\n[*] Directory Structure:")
        print(f"    {Path(project_path).name}/")
        
        for item in sorted(Path(project_path).iterdir())[:10]:
            if item.is_dir():
                subcount = sum(1 for _ in item.rglob('*') if _.is_file())
                print(f"    ├── {item.name}/ ({subcount} files)")
            else:
                print(f"    ├── {item.name}")
        
        print(f"\n[✓] Project generation complete!")
        print(f"[*] Ready to use: {project_path}")
        
    else:
        print(f"[✗] Project path does not exist: {project_path}")


if __name__ == "__main__":
    asyncio.run(test_full_project_generation())

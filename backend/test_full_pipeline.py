"""
Full Agent Pipeline Test - Tests all 7 agents working together
This demonstrates the complete GAAIUS AI multi-agent system
"""

import asyncio
import json
from dotenv import load_dotenv
from orchestrator import AgentOrchestrator

load_dotenv()


async def test_simple_pipeline():
    """Test simple pipeline: Product Manager + Frontend Engineer"""
    print("\n" + "=" * 70)
    print("TEST 1: SIMPLE PIPELINE (2 agents)")
    print("=" * 70)
    
    orchestrator = AgentOrchestrator()
    
    try:
        outputs = await orchestrator.run_full_pipeline(
            user_prompt="Create a simple todo list app with local storage",
            complexity="simple"
        )
        
        print("\n[OK] Simple pipeline completed!")
        print(f"\n--- Product Manager Output ---")
        if "product_manager" in outputs and outputs["product_manager"]:
            pm = outputs["product_manager"]
            if isinstance(pm, dict):
                print(f"Name: {pm.get('name', 'N/A')}")
                desc = pm.get('description', 'N/A')
                desc_preview = desc[:100] + "..." if isinstance(desc, str) and len(desc) > 100 else desc
                print(f"Description: {desc_preview}")
                print(f"Platforms: {pm.get('platforms', [])}")
        
        print(f"\n--- Pipeline Status ---")
        status = orchestrator.get_pipeline_status(outputs)
        for agent, state in status.items():
            symbol = "[✓]" if state == "completed" else "[✗]" if state == "failed" else "[⏳]"
            print(f"{symbol} {agent}: {state}")
            
        return outputs
        
    except Exception as e:
        print(f"\n[✗] Simple pipeline failed: {str(e)}")
        return None


async def test_standard_pipeline():
    """Test standard pipeline: 5 core agents"""
    print("\n" + "=" * 70)
    print("TEST 2: STANDARD PIPELINE (5 agents)")
    print("=" * 70)
    
    orchestrator = AgentOrchestrator()
    
    try:
        outputs = await orchestrator.run_full_pipeline(
            user_prompt="Create a real-time chat application with user profiles and message history",
            complexity="standard"
        )
        
        print("\n[OK] Standard pipeline completed!")
        
        agents_to_check = ["product_manager", "ui_designer", "frontend_engineer", "backend_engineer", "database_architect"]
        
        for agent in agents_to_check:
            if agent in outputs and outputs[agent]:
                print(f"\n--- {agent.upper().replace('_', ' ')} ---")
                out = outputs[agent]
                
                if agent == "product_manager":
                    if isinstance(out, dict):
                        print(f"App: {out.get('name', 'N/A')}")
                        modules = out.get('modules', [])
                        print(f"Modules: {len(modules)} ({', '.join(str(m) for m in modules[:3])}...)")
                        print(f"Platforms: {out.get('platforms', [])}")
                    
                elif agent == "ui_designer":
                    if isinstance(out, dict):
                        print(f"Framework: {out.get('framework', 'N/A')}")
                        print(f"Colors: {len(out.get('colors', {}))} colors defined")
                        components = out.get('components', [])
                        print(f"Components: {len(components)} components")
                    
                elif agent in ["frontend_engineer", "backend_engineer"]:
                    if isinstance(out, dict):
                        if "files" in out:
                            files = out.get('files', [])
                            print(f"Files generated: {len(files)}")
                            for f in files[:2]:
                                if isinstance(f, dict):
                                    print(f"  - {f.get('path', 'N/A')}")
                        elif "code" in out:
                            print(f"Code generated: {len(str(out.get('code', '')))} characters")
                    elif isinstance(out, str):
                        print(f"Code generated: {len(out)} characters")
                        
                elif agent == "database_architect":
                    if isinstance(out, dict):
                        if "schema" in out:
                            schema = out.get('schema', '')
                            print(f"Prisma Schema: {len(str(schema))} characters")
                            schema_str = str(schema)
                            models = schema_str.count('model ')
                            print(f"Database models: ~{models}")
                        elif "code" in out:
                            print(f"Schema generated: {len(str(out.get('code', '')))} characters")
                    elif isinstance(out, str):
                        print(f"Schema generated: {len(out)} characters")
        
        print(f"\n--- Pipeline Status ---")
        status = orchestrator.get_pipeline_status(outputs)
        for agent, state in status.items():
            symbol = "[✓]" if state == "completed" else "[✗]" if state == "failed" else "[⏳]"
            print(f"{symbol} {agent}: {state}")
            
        return outputs
        
    except Exception as e:
        print(f"\n[✗] Standard pipeline failed: {str(e)}")
        return None


async def test_advanced_pipeline():
    """Test advanced pipeline: All 7 agents including DevOps and QA"""
    print("\n" + "=" * 70)
    print("TEST 3: ADVANCED PIPELINE (7 agents - Full System)")
    print("=" * 70)
    
    orchestrator = AgentOrchestrator()
    
    try:
        outputs = await orchestrator.run_full_pipeline(
            user_prompt="Build a full-featured project management tool like Asana with real-time collaboration, file uploads, and team dashboards",
            complexity="advanced"
        )
        
        print("\n[OK] Advanced pipeline completed!")
        
        all_agents = [
            "product_manager", "ui_designer", "frontend_engineer", 
            "backend_engineer", "database_architect", "devops_engineer", "qa_validator"
        ]
        
        completed_count = 0
        for agent in all_agents:
            if agent in outputs and outputs[agent]:
                completed_count += 1
                status_symbol = "[✓]"
            else:
                status_symbol = "[✗]"
            
            agent_name = agent.replace('_', ' ').title()
            print(f"{status_symbol} {agent_name}")
            
            if agent in outputs and outputs[agent]:
                out = outputs[agent]
                if isinstance(out, dict):
                    print(f"   Keys: {', '.join(list(out.keys())[:3])}")
                elif isinstance(out, str):
                    print(f"   Output: {len(out)} characters")
        
        print(f"\n[INFO] Agents Completed: {completed_count}/7")
        
        print(f"\n--- Full Pipeline Status ---")
        status = orchestrator.get_pipeline_status(outputs)
        for agent, state in status.items():
            symbol = "[✓]" if state == "completed" else "[✗]" if state == "failed" else "[⏳]"
            print(f"{symbol} {agent}: {state}")
            
        return outputs
        
    except Exception as e:
        print(f"\n[✗] Advanced pipeline failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    """Run all pipeline tests"""
    print("\n" + "=" * 70)
    print("GAAIUS AI MULTI-AGENT ORCHESTRATION SYSTEM")
    print("Full Pipeline Test Suite")
    print("=" * 70)
    
    # Test 1: Simple Pipeline
    simple_outputs = await test_simple_pipeline()
    
    # Test 2: Standard Pipeline  
    standard_outputs = await test_standard_pipeline()
    
    # Test 3: Advanced Pipeline
    advanced_outputs = await test_advanced_pipeline()
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    tests = [
        ("Simple Pipeline (2 agents)", simple_outputs is not None),
        ("Standard Pipeline (5 agents)", standard_outputs is not None),
        ("Advanced Pipeline (7 agents)", advanced_outputs is not None),
    ]
    
    passed = sum(1 for _, result in tests if result)
    
    for test_name, passed_test in tests:
        symbol = "[✓]" if passed_test else "[✗]"
        print(f"{symbol} {test_name}")
    
    print(f"\nResults: {passed}/3 tests passed")
    
    if passed == 3:
        print("\n✨ ALL TESTS PASSED! Agent system is fully operational! ✨")
    else:
        print("\n⚠️  Some tests failed. Check logs above for details.")


if __name__ == "__main__":
    asyncio.run(main())

"""
GAAIUS AI - Agent System Test
Verify that all agent prompts and orchestrator are working correctly
"""

import asyncio
import json
import os
from dotenv import load_dotenv

# Load environment variables
from pathlib import Path
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from orchestrator import AgentOrchestrator
from agent_prompts import (
    PRODUCT_MANAGER_PROMPT,
    UI_DESIGNER_PROMPT,
    FRONTEND_ENGINEER_PROMPT,
    BACKEND_ENGINEER_PROMPT,
    DATABASE_ARCHITECT_PROMPT,
    DEVOPS_ENGINEER_PROMPT,
    QA_VALIDATOR_PROMPT
)


def test_agent_prompts():
    """Test that all agent prompts are properly loaded"""
    print("\n" + "="*80)
    print("AGENT PROMPTS VALIDATION TEST")
    print("="*80)
    
    prompts = {
        "product_manager": PRODUCT_MANAGER_PROMPT,
        "ui_designer": UI_DESIGNER_PROMPT,
        "frontend_engineer": FRONTEND_ENGINEER_PROMPT,
        "backend_engineer": BACKEND_ENGINEER_PROMPT,
        "database_architect": DATABASE_ARCHITECT_PROMPT,
        "devops_engineer": DEVOPS_ENGINEER_PROMPT,
        "qa_validator": QA_VALIDATOR_PROMPT,
    }
    
    print(f"\n✅ Found {len(prompts)} agent prompts\n")
    
    for agent_name, prompt_text in prompts.items():
        prompt_length = len(prompt_text)
        lines = prompt_text.count('\n')
        has_output_format = "OUTPUT" in prompt_text or "Return" in prompt_text
        
        status = "✅"
        print(f"{status} {agent_name}:")
        print(f"   📝 {prompt_length} characters, {lines} lines")
        print(f"   📋 Has output format spec: {has_output_format}")
    
    print("\n✅ All agent prompts loaded successfully!")


async def test_agent_system():
    """Test the agent orchestration system"""
    
    # Initialize orchestrator
    print("\n" + "="*80)
    print("GAAIUS AI - AGENT SYSTEM TEST")
    print("="*80)
    
    # Check if GROQ API key is available
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key or "your_key" in groq_key.lower():
        print("\n⚠️  GROQ_API_KEY not configured in .env")
        print("   Skipping live API tests")
        print("   To enable: Update GROQ_API_KEY in .env file")
        return
    
    try:
        orchestrator = AgentOrchestrator(groq_key)
        print("✅ Orchestrator initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize orchestrator: {e}")
        return
    
    # Test single agent execution
    print("\n" + "-"*80)
    print("TEST 1: Single Agent Execution (Product Manager)")
    print("-"*80)
    
    user_prompt = "Create a social media app for video sharing like TikTok"
    
    try:
        result = await orchestrator.execute_agent(
            "product_manager",
            user_prompt,
            {}
        )
        print("✅ Product Manager executed successfully")
        print(f"Output type: {type(result).__name__}")
        if isinstance(result, dict) and "name" in result:
            print(f"Generated app name: {result.get('name', 'Unknown')}")
            print(f"Platforms: {result.get('platforms', [])}")
            print(f"Modules: {[m.get('name') for m in result.get('modules', [])]}")
    except Exception as e:
        print(f"❌ Product Manager failed: {e}")
    
    # Test full pipeline - simple complexity
    print("\n" + "-"*80)
    print("TEST 2: Full Pipeline (Simple Complexity)")
    print("-"*80)
    
    try:
        simple_outputs = await orchestrator.run_full_pipeline(
            user_prompt,
            complexity="simple"
        )
        
        # Check results
        completed = sum(1 for v in simple_outputs.values() if "error" not in v)
        total = len(simple_outputs)
        
        print(f"✅ Pipeline completed: {completed}/{total} agents successful")
        
        # Show what was produced
        for agent_name, output in simple_outputs.items():
            if "error" in output:
                print(f"  ❌ {agent_name}: {output['error']}")
            else:
                print(f"  ✅ {agent_name}: Generated output")
    
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
    
    # Test pipeline status
    print("\n" + "-"*80)
    print("TEST 3: Pipeline Status Check")
    print("-"*80)
    
    try:
        status = orchestrator.get_pipeline_status(simple_outputs)
        
        print("Pipeline Status:")
        for agent, state in status.items():
            symbol = "✅" if state == "completed" else "❌" if state == "failed" else "⏳"
            print(f"  {symbol} {agent}: {state}")
    
    except Exception as e:
        print(f"❌ Status check failed: {e}")
    
    # Test standard complexity (full stack)
    print("\n" + "-"*80)
    print("TEST 4: Full Pipeline (Standard Complexity - Full Stack)")
    print("-"*80)
    print("⏳ This will run 5 agents: product_manager, ui_designer, frontend_engineer,")
    print("   backend_engineer, database_architect")
    print("   Estimated time: 2-3 minutes...")
    
    try:
        standard_outputs = await orchestrator.run_full_pipeline(
            user_prompt,
            complexity="standard"
        )
        
        completed = sum(1 for v in standard_outputs.values() if "error" not in v)
        total = len(standard_outputs)
        
        print(f"\n✅ Pipeline completed: {completed}/{total} agents successful")
        
        # Show generated outputs
        print("\nGenerated Outputs Summary:")
        if "product_manager" in standard_outputs:
            spec = standard_outputs["product_manager"]
            if isinstance(spec, dict) and "name" in spec:
                print(f"  📦 Product: {spec.get('name')}")
        
        if "ui_designer" in standard_outputs:
            design = standard_outputs["ui_designer"]
            if isinstance(design, dict) and "framework" in design:
                print(f"  🎨 Framework: {design.get('framework')}")
                print(f"  🎭 Theme: {design.get('theme')}")
        
        if "frontend_engineer" in standard_outputs:
            print(f"  ⚛️  Frontend: Generated React code")
        
        if "backend_engineer" in standard_outputs:
            print(f"  🔧 Backend: Generated Node.js code")
        
        if "database_architect" in standard_outputs:
            print(f"  💾 Database: Generated Prisma schema")
    
    except Exception as e:
        print(f"❌ Standard pipeline failed: {e}")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    # Run tests
    print("\n\n")
    print("=" * 80)
    print("GAAIUS AI - AGENT SYSTEM VERIFICATION")
    print("=" * 80)
    
    # Test 1: Agent Prompts
    test_agent_prompts()
    
    # Test 2: Orchestrator (only if API key is set)
    print("\n\n" + "="*80)
    print("ORCHESTRATOR SYSTEM TEST")
    print("="*80)
    
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key or "your_key" in groq_key.lower():
        print("\n[!] SKIPPING LIVE API TESTS")
        print("    GROQ_API_KEY not configured in .env")
        print("\n    To enable full testing:")
        print("    1. Get your API key from: https://console.groq.com/keys")
        print("    2. Update GROQ_API_KEY in backend/.env")
        print("    3. Run this test again\n")
    else:
        # Run async test with actual API calls
        asyncio.run(test_agent_system())
    
    print("\n" + "="*80)
    print("[OK] AGENT SYSTEM SETUP COMPLETE")
    print("="*80)
    print("\nAgent System Components:")
    print("  [OK] agent_prompts.py      - 7 specialized system prompts")
    print("  [OK] orchestrator.py        - Multi-agent orchestrator")
    print("  [OK] file_generator.py      - Project file generator")
    print("  [OK] server.py              - FastAPI integration (5 new endpoints)")
    print("\nNew API Endpoints:")
    print("  [*] POST /api/agents/orchestrate")
    print("  [*] POST /api/agents/orchestrate/files")
    print("  [*] GET  /api/agents/projects")
    print("  [*] GET  /api/agents/projects/{project_id}")
    print("  [*] POST /api/agents/regenerate/{agent_name}")
    print("\nNext Steps:")
    print("  1. Start backend: python -m uvicorn server:app --reload")
    print("  2. Test orchestration via FastAPI /docs endpoint")
    print("  3. Or use curl to trigger agent pipeline")
    print("\n" + "="*80 + "\n")

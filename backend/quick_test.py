#!/usr/bin/env python3
"""Quick test of agent system"""
import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from orchestrator import AgentOrchestrator

async def quick_test():
    print("\n[*] Testing Agent System with llama-3.1-8b-instant model...")
    print(f"[*] GROQ API Key available: {bool(os.getenv('GROQ_API_KEY'))}\n")
    
    try:
        orchestrator = AgentOrchestrator()
        print("[OK] Orchestrator initialized\n")
        
        print("[*] Running Product Manager agent...")
        result = await orchestrator.execute_agent(
            "product_manager",
            "Create a simple video sharing app",
            {}
        )
        
        if isinstance(result, dict):
            if "name" in result:
                print(f"\n[OK] SUCCESS! Generated app: {result.get('name')}")
                print(f"    Description: {result.get('description', 'N/A')[:80]}")
                print(f"    Platforms: {result.get('platforms', [])}")
            elif "error" in result:
                print(f"[!] Agent returned error: {result['error']}")
            else:
                print(f"[OK] Got response. Keys: {list(result.keys())}")
        else:
            print(f"[OK] Got response: {str(result)[:200]}")
            
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {str(e)}")

if __name__ == "__main__":
    asyncio.run(quick_test())

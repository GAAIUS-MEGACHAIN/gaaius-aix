"""
GAAIUS AI - Agent Orchestrator System
Coordinates 7 specialized AI agents for full-stack code generation
"""

import asyncio
import json
import os
from typing import Dict, List, Any, Optional
from groq import Groq

try:
    # Prefer package-relative import when available
    from .agent_prompts import (
        PRODUCT_MANAGER_PROMPT,
        UI_DESIGNER_PROMPT,
        FRONTEND_ENGINEER_PROMPT,
        BACKEND_ENGINEER_PROMPT,
        DATABASE_ARCHITECT_PROMPT,
        DEVOPS_ENGINEER_PROMPT,
        QA_VALIDATOR_PROMPT
    )
except Exception:
    # Fallback to top-level import for local execution
    from agent_prompts import (
        PRODUCT_MANAGER_PROMPT,
        UI_DESIGNER_PROMPT,
        FRONTEND_ENGINEER_PROMPT,
        BACKEND_ENGINEER_PROMPT,
        DATABASE_ARCHITECT_PROMPT,
        DEVOPS_ENGINEER_PROMPT,
        QA_VALIDATOR_PROMPT
    )


class AgentOrchestrator:
    """Orchestrates the 7-agent AI system for complete code generation"""
    
    def __init__(self, groq_api_key: Optional[str] = None):
        """Initialize the orchestrator with Groq client"""
        api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment or parameters")
        
        self.groq = Groq(api_key=api_key)
        
        self.agent_prompts = {
            "product_manager": PRODUCT_MANAGER_PROMPT,
            "ui_designer": UI_DESIGNER_PROMPT,
            "frontend_engineer": FRONTEND_ENGINEER_PROMPT,
            "backend_engineer": BACKEND_ENGINEER_PROMPT,
            "database_architect": DATABASE_ARCHITECT_PROMPT,
            "devops_engineer": DEVOPS_ENGINEER_PROMPT,
            "qa_validator": QA_VALIDATOR_PROMPT,
        }
        
        # Agent execution order (each depends on previous outputs)
        self.agent_pipeline = [
            "product_manager",      # 1. Create product spec
            "ui_designer",          # 2. Design UI from spec
            "frontend_engineer",    # 3. Generate frontend code
            "backend_engineer",     # 4. Generate backend code
            "database_architect",   # 5. Design database schema
            "devops_engineer",      # 6. Create deployment config
            "qa_validator",         # 7. Validate everything
        ]
    
    async def run_full_pipeline(
        self, 
        user_prompt: str,
        complexity: str = "standard"
    ) -> Dict[str, Any]:
        """
        Execute complete 7-agent pipeline
        
        Args:
            user_prompt: User's app description
            complexity: "simple", "standard", or "advanced"
        
        Returns:
            Dictionary with outputs from all agents
        """
        print(f"\n{'='*70}")
        print(f"🚀 GAAIUS AI - FULL PIPELINE BUILD")
        print(f"{'='*70}")
        print(f"📝 Request: {user_prompt[:60]}...")
        print(f"📊 Complexity: {complexity}")
        print(f"{'='*70}\n")
        
        outputs = {}
        agent_list = self._get_agent_pipeline_for_complexity(complexity)
        
        for i, agent_name in enumerate(agent_list, 1):
            total = len(agent_list)
            print(f"\n[{i}/{total}] 🤖 {agent_name.upper()}")
            print("-" * 70)
            
            try:
                # Get previous agent outputs for context
                context = self._build_agent_context(agent_name, outputs)
                
                # Execute the agent
                result = await self.execute_agent(
                    agent_name,
                    user_prompt,
                    context
                )
                
                outputs[agent_name] = result
                print(f"✅ {agent_name} completed successfully")
                
                # Show summary of what was produced
                if isinstance(result, dict):
                    if "name" in result:
                        print(f"   Generated: {result.get('name', 'N/A')}")
                    if "error" not in result:
                        print(f"   Output type: {type(result).__name__}")
                
            except Exception as e:
                print(f"❌ Error in {agent_name}: {str(e)}")
                outputs[agent_name] = {"error": str(e), "agent": agent_name}
        
        # Print final summary
        print(f"\n{'='*70}")
        print(f"🎉 PIPELINE COMPLETE")
        print(f"{'='*70}")
        print(f"✅ Agents completed: {sum(1 for v in outputs.values() if 'error' not in v)}/{len(agent_list)}")
        print(f"❌ Agents failed: {sum(1 for v in outputs.values() if 'error' in v)}/{len(agent_list)}")
        print(f"{'='*70}\n")
        
        return outputs
    
    async def execute_agent(
        self,
        agent_name: str,
        user_prompt: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a single agent with specialized prompt
        
        Args:
            agent_name: Name of agent to execute
            user_prompt: Original user request
            context: Previous agent outputs for context
        
        Returns:
            Agent output (usually JSON)
        """
        if agent_name not in self.agent_prompts:
            raise ValueError(f"Unknown agent: {agent_name}")
        
        system_prompt = self.agent_prompts[agent_name]
        
        # Build the user message with context
        user_message = self._build_user_message(agent_name, user_prompt, context)
        
        # Call Groq API
        response = await self._call_groq_api(
            system_prompt=system_prompt,
            user_message=user_message,
            agent_name=agent_name
        )
        
        # Parse and validate response
        return self._parse_agent_response(response, agent_name)
    
    def _get_agent_pipeline_for_complexity(self, complexity: str) -> List[str]:
        """Get agent pipeline based on complexity level"""
        if complexity == "simple":
            # Simple: only product manager + frontend
            return ["product_manager", "frontend_engineer"]
        elif complexity == "standard":
            # Standard: product -> design -> frontend -> backend -> database
            return [
                "product_manager",
                "ui_designer",
                "frontend_engineer",
                "backend_engineer",
                "database_architect"
            ]
        elif complexity == "advanced":
            # Advanced: full pipeline including DevOps and QA
            return self.agent_pipeline
        else:
            return self.agent_pipeline  # Default to full
    
    def _build_agent_context(
        self,
        current_agent: str,
        previous_outputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build context dictionary with relevant previous outputs"""
        context = {}
        
        # Product Manager → all others need the spec
        if "product_manager" in previous_outputs and current_agent != "product_manager":
            context["product_spec"] = previous_outputs["product_manager"]
        
        # UI Designer needs product spec
        if "ui_designer" in previous_outputs and current_agent not in ["product_manager", "ui_designer"]:
            context["design_spec"] = previous_outputs["ui_designer"]
        
        # Frontend/Backend need product + design specs
        if current_agent in ["frontend_engineer", "backend_engineer"]:
            context["product_spec"] = previous_outputs.get("product_manager")
            context["design_spec"] = previous_outputs.get("ui_designer")
        
        # Database Architect needs data models
        if current_agent == "database_architect":
            context["data_models"] = previous_outputs.get("product_manager", {}).get("data_models", [])
        
        # DevOps needs frontend/backend paths
        if current_agent == "devops_engineer":
            context["frontend_code"] = "src/"
            context["backend_code"] = "backend/"
        
        # QA Validator needs all previous outputs
        if current_agent == "qa_validator":
            context["all_outputs"] = previous_outputs
        
        return context
    
    def _build_user_message(
        self,
        agent_name: str,
        user_prompt: str,
        context: Dict[str, Any]
    ) -> str:
        """Build the user message with context for the agent"""
        message = f"User request: {user_prompt}\n\n"
        
        if context:
            message += "Previous outputs for context:\n"
            for key, value in context.items():
                if value:
                    if isinstance(value, dict):
                        message += f"{key}: {json.dumps(value, indent=2)[:500]}...\n"
                    elif isinstance(value, list):
                        message += f"{key}: {json.dumps(value, indent=2)[:500]}...\n"
                    else:
                        message += f"{key}: {str(value)[:500]}...\n"
        
        return message
    
    async def _call_groq_api(
        self,
        system_prompt: str,
        user_message: str,
        agent_name: str
    ) -> str:
        """Call Groq API and return response"""
        try:
            # Using Groq's newest and most stable models
            # Check: https://console.groq.com/docs/models
            # Primary: llama-3.3-70b-specdec (newest 70B)
            # Fallback: llama-3.1-405b-reasoning (reasoning model)
            # Fast: llama-3.1-8b-instant
            
            # Using the latest stable model that's widely available
            model = "llama-3.1-8b-instant"  # Fast and reliable for most tasks
            
            response = self.groq.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                temperature=0.3,  # Lower temp for more consistent output
                max_tokens=2000,  # Adjust per agent needs
                top_p=0.9,
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            print(f"⚠️  API Error: {str(e)}")
            raise
    
    def _parse_agent_response(self, response: str, agent_name: str) -> Dict[str, Any]:
        """Parse agent response, extracting JSON if needed"""
        # Try to extract JSON from response
        try:
            # First try direct JSON parsing
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        
        # Try to find JSON block in response
        try:
            # Look for JSON between { and }
            start = response.find('{')
            end = response.rfind('}') + 1
            
            if start != -1 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
        except (json.JSONDecodeError, ValueError):
            pass
        
        # If it's code (FILE: markers), return as-is
        if "FILE:" in response:
            return {"code": response, "type": "code_output"}
        
        # If it's QA report (JSON with checks), return as-is
        if "overall_status" in response and "checks" in response:
            try:
                # Extract JSON
                start = response.find('{')
                end = response.rfind('}') + 1
                if start != -1:
                    return json.loads(response[start:end])
            except:
                pass
        
        # Fallback: return raw response
        return {
            "raw_output": response,
            "agent": agent_name,
            "parsing_status": "partial"
        }
    
    def get_pipeline_status(self, outputs: Dict[str, Any]) -> Dict[str, str]:
        """Get status of all agents in the pipeline"""
        status = {}
        
        for agent_name in self.agent_pipeline:
            if agent_name not in outputs:
                status[agent_name] = "pending"
            elif "error" in outputs[agent_name]:
                status[agent_name] = "failed"
            else:
                status[agent_name] = "completed"
        
        return status
    
    async def regenerate_agent(
        self,
        agent_name: str,
        user_prompt: str,
        previous_outputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Regenerate output from a specific agent"""
        if agent_name not in self.agent_prompts:
            raise ValueError(f"Unknown agent: {agent_name}")
        
        context = self._build_agent_context(agent_name, previous_outputs)
        return await self.execute_agent(agent_name, user_prompt, context)


async def run_orchestrator(
    user_prompt: str,
    groq_api_key: Optional[str] = None,
    complexity: str = "standard"
) -> Dict[str, Any]:
    """
    Convenience function to run the full orchestration pipeline
    
    Args:
        user_prompt: User's app description
        groq_api_key: Groq API key (uses env if not provided)
        complexity: "simple", "standard", or "advanced"
    
    Returns:
        Dictionary with outputs from all agents
    """
    orchestrator = AgentOrchestrator(groq_api_key)
    return await orchestrator.run_full_pipeline(user_prompt, complexity)


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = "Create a video sharing app like YouTube"
    
    # Run async
    asyncio.run(run_orchestrator(prompt, complexity="standard"))

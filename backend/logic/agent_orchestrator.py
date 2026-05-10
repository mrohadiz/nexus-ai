import asyncio
import json
from typing import List, Dict, Optional
from logic.ai_service import ai_service

class AgentOrchestrator:
    def __init__(self):
        self.max_iterations = 10
        self.tools = self._get_available_tools()
    
    def _get_available_tools(self) -> List[Dict]:
        """Define available tools for the agent"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": "Search the web for current information on a topic",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query"
                            },
                            "num_results": {
                                "type": "number",
                                "description": "Number of results to return (default: 5)"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "research_topic",
                    "description": "Perform in-depth research on a topic with multiple searches",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "description": "The topic to research"
                            },
                            "depth": {
                                "type": "string",
                                "enum": ["shallow", "deep"],
                                "description": "Research depth level"
                            }
                        },
                        "required": ["topic"]
                    }
                }
            }
        ]
    
    async def autonomous_research(self, query: str, session_id: str = "default") -> Dict:
        """
        Autonomous research workflow:
        1. Plan research approach
        2. Execute searches
        3. Synthesize findings
        4. Generate final report
        """
        
        print(f"🔍 Starting autonomous research on: {query}")
        
        # Step 1: Create research plan
        plan_prompt = f"""
You are a research planner. Create a step-by-step plan to research: "{query}"

Return a JSON object with:
- objectives: List of research objectives
- search_queries: List of specific search queries to execute
- expected_outcomes: What we hope to learn

Format: {{"objectives": [...], "search_queries": [...], "expected_outcomes": [...]}}
"""
        
        plan_response = await asyncio.to_thread(
            ai_service.call_ai,
            plan_prompt,
            system_prompt="You are an expert research planner.",
            model="google/gemini-2.0-flash-001"
        )
        
        try:
            plan = json.loads(plan_response) if plan_response else {}
        except:
            plan = {
                "objectives": [f"Research {query}"],
                "search_queries": [query],
                "expected_outcomes": ["Comprehensive understanding"]
            }
        
        print(f"📋 Research plan created: {len(plan.get('search_queries', []))} queries planned")
        
        # Step 2: Execute research iterations
        findings = []
        iteration = 0
        
        for iteration in range(self.max_iterations):
            print(f"🔄 Iteration {iteration + 1}/{self.max_iterations}")
            
            # Decide next action
            action_prompt = f"""
Based on the research plan and findings so far, what should we do next?

Plan: {json.dumps(plan)}
Findings so far: {json.dumps(findings[-3:]) if findings else "None yet"}

Choose one:
1. Call web_search with a specific query
2. Call research_topic for deep dive
3. Summarize findings and complete research

Return JSON: {{"action": "search|research|complete", "parameters": {{...}}, "reasoning": "..."}}
"""
            
            action_response = await asyncio.to_thread(
                ai_service.call_ai,
                action_prompt,
                system_prompt="You are a research executor. Decide the next best action.",
                model="google/gemini-2.0-flash-001"
            )
            
            try:
                action = json.loads(action_response) if action_response else {"action": "complete"}
            except:
                action = {"action": "complete", "parameters": {}, "reasoning": "Parsing error"}
            
            print(f"   Action: {action.get('action', 'unknown')}")
            
            if action["action"] == "complete" or iteration == self.max_iterations - 1:
                print("✅ Research complete")
                break
            
            # Execute the chosen action
            if action["action"] == "search":
                query_text = action['parameters'].get('query', query)
                print(f"   🔎 Searching: {query_text}")
                
                result = await asyncio.to_thread(
                    ai_service.call_ai,
                    f"Search for: {query_text}",
                    tools=self.tools,
                    tool_choice={"type": "function", "function": {"name": "web_search"}},
                    model="google/gemini-2.0-flash-001"
                )
                
                findings.append({
                    "iteration": iteration,
                    "action": "search",
                    "query": query_text,
                    "result": result
                })
            
            elif action["action"] == "research":
                topic = action['parameters'].get('topic', query)
                depth = action['parameters'].get('depth', 'shallow')
                print(f"   📚 Researching: {topic} ({depth})")
                
                result = await asyncio.to_thread(
                    ai_service.call_ai,
                    f"Research topic: {topic}",
                    tools=self.tools,
                    tool_choice={"type": "function", "function": {"name": "research_topic"}},
                    model="google/gemini-2.0-flash-001"
                )
                
                findings.append({
                    "iteration": iteration,
                    "action": "research",
                    "topic": topic,
                    "depth": depth,
                    "result": result
                })
        
        # Step 3: Synthesize final report
        print("📝 Synthesizing final report...")
        synthesis_prompt = f"""
Synthesize all research findings into a comprehensive report on: "{query}"

Research Plan: {json.dumps(plan)}
All Findings: {json.dumps(findings)}

Create a well-structured report with:
1. Executive Summary
2. Key Findings
3. Detailed Analysis
4. Sources Referenced
5. Recommendations (if applicable)
"""
        
        final_report = await asyncio.to_thread(
            ai_service.call_ai,
            synthesis_prompt,
            system_prompt="You are an expert researcher creating a comprehensive report.",
            model="google/gemini-2.0-flash-001"
        )
        
        print("✅ Research completed successfully!")
        
        return {
            "query": query,
            "plan": plan,
            "findings": findings,
            "final_report": final_report,
            "iterations_used": iteration + 1
        }
    
    async def task_planning(self, goal: str) -> Dict:
        """
        Autonomous task planning:
        Break down complex goals into executable steps
        """
        
        print(f"📋 Creating task plan for: {goal}")
        
        planning_prompt = f"""
Goal: {goal}

Create a detailed execution plan with:
1. Task breakdown into sequential steps
2. Required resources/tools for each step
3. Success criteria
4. Potential obstacles and mitigation

Return JSON format:
{{
    "steps": [
        {{"step_number": 1, "action": "...", "tool_needed": "...", "success_criteria": "..."}}
    ],
    "resources_needed": [...],
    "risks": [...]
}}
"""
        
        plan = await asyncio.to_thread(
            ai_service.call_ai,
            planning_prompt,
            system_prompt="You are an expert task planner. Create actionable, detailed plans.",
            model="google/gemini-2.0-flash-001"
        )
        
        try:
            parsed_plan = json.loads(plan) if plan else {}
            print(f"✅ Task plan created with {len(parsed_plan.get('steps', []))} steps")
            return parsed_plan
        except:
            print("⚠️ Failed to parse plan, returning raw response")
            return {"error": "Failed to parse plan", "raw_response": plan}

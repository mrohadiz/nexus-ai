from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

from config.database import init_db, get_db
from logic.memory_manager import memory_manager
from logic.agent_orchestrator import AgentOrchestrator

load_dotenv()

app = FastAPI(title="Nexus AI Backend")

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Message]] = []
    session_id: Optional[str] = "default"
    model: Optional[str] = "google/gemini-2.0-flash-001"
    images: Optional[List[str]] = []  # Base64 image data URIs

class ChatResponse(BaseModel):
    response: str
    context_used: List[str]

@app.on_event("startup")
def startup_event():
    init_db()
    print("🚀 Nexus AI Backend Started & DB Initialized")

# Initialize agent orchestrator
orchestrator = AgentOrchestrator()

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "0.1.0"}

from logic.ai_service import ai_service

from fastapi.responses import StreamingResponse
import json

@app.post("/chat/stream")
async def chat_stream_endpoint(req: ChatRequest):
    # 1. Recall from Mira (Episodic)
    mira_context = memory_manager.mira_recall(req.message)
    
    # 2. Build Enriched Prompt
    system_prompt = "You are Nexus AI. Be concise and professional. Use the following context if relevant."
    if mira_context:
        system_prompt += f"\n\n[CONTEXT FROM MEMORY]:\n{mira_context}"
    
    # 3. Define Generator for Streaming with auto-fallback
    async def event_generator():
        full_response = ""
        
        # Build fallback chain: primary model + all available free models from OpenRouter
        models_to_try = ai_service.get_fallback_chain(req.model)
        print(f"[AUTO-ROUTER] Fallback chain ({len(models_to_try)} models): {models_to_try[:3]}...")
        
        last_error = None
        for attempt_idx, model in enumerate(models_to_try):
            try:
                print(f"[AUTO-FALLBACK] Attempt {attempt_idx + 1}/{len(models_to_try)} with model: {model}")
                
                # Notify frontend if switching models (after first attempt)
                if attempt_idx > 0:
                    yield f"data: {json.dumps({'type': 'info', 'message': f'Switching to {model} due to previous model error...'})}\n\n"
                
                async for chunk in ai_service.call_ai_stream(
                    req.message, 
                    history=req.history, 
                    system_prompt=system_prompt, 
                    model=model,
                    images=req.images if req.images else None
                ):
                    if chunk:
                        # Check if it's an error message
                        if chunk.startswith("data: "):
                            try:
                                data = json.loads(chunk[6:])
                                
                                # If we got an error, save it and try next model
                                if data.get('type') == 'error':
                                    last_error = data.get('message', 'Unknown error')
                                    print(f"[AUTO-FALLBACK] Error from {model}: {last_error}")
                                    break  # Break inner loop, try next model
                            except:
                                pass
                        
                        # Successful chunk - stream it
                        full_response += chunk
                        yield chunk
                
                # If we got here and have content, success!
                if full_response.strip():
                    print(f"[AUTO-FALLBACK] Success with model: {model}")
                    break  # Exit the model retry loop
                    
            except Exception as e:
                print(f"[AUTO-FALLBACK] Exception with {model}: {str(e)}")
                last_error = str(e)
                continue
        
        # If all models failed
        if not full_response.strip():
            error_msg = f"All models failed. Last error: {last_error or 'Unknown error'}"
            print(f"[AUTO-FALLBACK] {error_msg}")
            yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"
        
        # 4. Store in Mira after stream completion
        if full_response:
            memory_manager.mira_store(f"User: {req.message}\nAI: {full_response}", room=req.session_id)
            
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    # 1. Recall from Mira (Episodic)
    mira_context = memory_manager.mira_recall(req.message)
    
    # 2. Build Enriched Prompt
    system_prompt = "You are Nexus AI. Be concise and professional. Use the following context if relevant."
    if mira_context:
        system_prompt += f"\n\n[CONTEXT FROM MEMORY]:\n{mira_context}"
    
    # 3. Call AI with specific model
    ai_response = ai_service.call_ai(req.message, history=req.history, system_prompt=system_prompt, model=req.model)
    
    if ai_response:
        # 4. Store in Mira
        memory_manager.mira_store(f"User: {req.message}\nAI: {ai_response}", room=req.session_id)
    else:
        ai_response = "I'm sorry, I'm having trouble connecting to my brain (AI Service). Please check the server."
    
    return {
        "response": ai_response,
        "context_used": ["mira"] if mira_context else []
    }

@app.post("/chat/tools")
async def chat_with_tools(req: ChatRequest):
    """Chat endpoint with tool calling support"""
    
    # Define available tools with REAL web search capabilities
    tools = [
        {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Search the web for CURRENT, REAL-TIME information using DuckDuckGo. Use this for keywords, trends, news, and live data.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query (use specific keywords)"},
                        "num_results": {"type": "number", "description": "Number of results (default 5)"}
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "research_topic",
                "description": "Perform IN-DEPTH research on a topic with REAL data from multiple sources. Gets search results, PAA questions, related searches, and fetches detailed content from top URLs.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string", "description": "Topic or keyword to research"},
                        "depth": {"type": "string", "enum": ["shallow", "deep"], "description": "Research depth (deep = more sources)"}
                    },
                    "required": ["topic"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "fetch_url",
                "description": "Fetch and extract REAL content from a specific URL. Use this to read first-page ranking articles for references.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "Full URL to fetch content from"}
                    },
                    "required": ["url"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_people_also_ask",
                "description": "Get REAL 'People Also Ask' questions for a keyword from search results.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Main keyword to get PAA questions for"}
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_related_searches",
                "description": "Get REAL related searches and 'People Also Search' for a keyword.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Main keyword to get related searches for"}
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_current_time",
                "description": "Get the current date and time",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        }
    ]
    
    # Stream with tools and auto-fallback
    async def event_generator():
        full_response = ""
        tool_calls_detected = []
        
        # Only use tools if user explicitly asks for web search/research
        # Check if prompt contains keywords that suggest need for real-time data
        needs_tools = any(keyword in req.message.lower() for keyword in [
            'research', 'search', 'current', 'latest', 'today', 'real-time', 
            'template', 'seo', 'keyword', 'trend', 'news', 'people also ask'
        ])
        
        # Build fallback chain: primary model + all available free models from OpenRouter
        models_to_try = ai_service.get_fallback_chain(req.model)
        print(f"[AUTO-ROUTER] Fallback chain ({len(models_to_try)} models): {models_to_try[:3]}...")
        
        last_error = None
        for attempt_idx, model in enumerate(models_to_try):
            try:
                print(f"[AUTO-FALLBACK] Attempt {attempt_idx + 1}/{len(models_to_try)} with model: {model}")
                
                # Notify frontend if switching models (after first attempt)
                if attempt_idx > 0:
                    yield f"data: {json.dumps({'type': 'info', 'message': f'Switching to {model} due to previous model error...'})}\n\n"
                
                async for chunk in ai_service.call_ai_stream(
                    req.message,
                    history=req.history,
                    system_prompt="""You are Nexus AI with access to REAL-TIME web search and research tools.

IMPORTANT: When users ask you to fill templates that require current data (keywords, SEO data, trends, references, etc.), you MUST:
1. Use web_search tool to get CURRENT keywords and search data
2. Use get_people_also_ask to get REAL "People Also Ask" questions
3. Use get_related_searches to get REAL related searches
4. Use research_topic for comprehensive data gathering
5. Use fetch_url to read first-page ranking articles for references
6. ALWAYS use real data from tools, NEVER make up or guess information

Available tools give you access to:
- Live search results from DuckDuckGo
- Current "People Also Ask" questions
- Related searches and trends
- Full article content from URLs
- Current date/time

Always cite your sources when using real-time data.""",
                    model=model,
                    tools=tools if needs_tools else None,
                    tool_choice="auto" if needs_tools else None
                ):
                    if chunk:
                        # Check if it's an error message
                        if chunk.startswith("data: "):
                            try:
                                data = json.loads(chunk[6:])
                                
                                # If we got an error, save it and try next model
                                if data.get('type') == 'error':
                                    last_error = data.get('message', 'Unknown error')
                                    print(f"[AUTO-FALLBACK] Error from {model}: {last_error}")
                                    break  # Break inner loop, try next model
                                
                                # If it's a tool call
                                if "tool_calls" in data:
                                    tool_calls_detected.extend(data["tool_calls"])
                                    yield f"data: {json.dumps({'type': 'tool_call', 'data': data['tool_calls']})}\n\n"
                                    continue
                            except:
                                pass
                        
                        # Successful chunk - stream it
                        full_response += chunk
                        yield chunk
                
                # If we got here and have content, success!
                if full_response.strip():
                    print(f"[AUTO-FALLBACK] Success with model: {model}")
                    break  # Exit the model retry loop
                    
            except Exception as e:
                print(f"[AUTO-FALLBACK] Exception with {model}: {str(e)}")
                last_error = str(e)
                continue
        
        # If all models failed
        if not full_response.strip():
            error_msg = f"All models failed. Last error: {last_error or 'Unknown error'}"
            print(f"[AUTO-FALLBACK] {error_msg}")
            yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"
        
        # If tool calls were made, process them
        if tool_calls_detected:
            for tool_call in tool_calls_detected:
                result = await ai_service.execute_tool_call(tool_call)
                yield f"data: {json.dumps({'type': 'tool_result', 'tool_call_id': tool_call.get('id'), 'result': result})}\n\n"
        
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/research/autonomous")
async def autonomous_research(req: ChatRequest):
    """Autonomous research endpoint"""
    
    result = await orchestrator.autonomous_research(
        query=req.message,
        session_id=req.session_id
    )
    
    return result


@app.post("/planning/task")
async def create_task_plan(req: ChatRequest):
    """Task planning endpoint"""
    
    plan = await orchestrator.task_planning(goal=req.message)
    
    return plan

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

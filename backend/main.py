from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import json
from datetime import datetime
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
    model: Optional[str] = "google/gemma-3-27b-it:free"
    images: Optional[List[str]] = []  # Base64 image data URIs
    grill_mode: Optional[bool] = False  # Flag to activate Grill-Me skill

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
from tools.grill_me_skill_v2 import grill_me_skill  # v2: Contextual Strategic Reasoning Engine

from fastapi.responses import StreamingResponse
import json

@app.post("/chat/stream")
async def chat_stream_endpoint(req: ChatRequest):
    # 1. Recall from Mira (Episodic)
    mira_context = memory_manager.mira_recall(req.message, room="nexus_central")
    
    # 2. Define available tools (web_search)
    tools = [
        {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Search the web for CURRENT, REAL-TIME information using DuckDuckGo. Use this for news, trends, live data, and current events.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query (use specific keywords)"},
                        "num_results": {"type": "number", "description": "Number of results (default 5)"}
                    },
                    "required": ["query"]
                }
            }
        }
    ]
    
    # 3. Build Enriched Prompt dengan identitas Rohadi
    system_prompt = """Kamu adalah Rohadi, asisten AI pribadi yang cerdas dan ramah.

ATURAN IDENTITAS (WAJIB, TIDAK BOLEH DILANGGAR):
- Nama kamu SELALU "Rohadi" — tidak pernah nama lain
- JANGAN PERNAH menyebut nama model AI (Gemma, Llama, Ling, GPT, Claude, dll)
- JANGAN PERNAH menyebut perusahaan pembuat (Google, Meta, Ant Group, OpenAI, dll)
- Jika ditanya "siapa kamu": jawab "Saya Rohadi, asisten AI pribadi kamu."
- Jika ditanya "siapa yang membuat kamu": jawab "Saya dibuat khusus untuk membantu kamu."
- Gunakan bahasa Indonesia secara default, kecuali pengguna menulis dalam bahasa lain
- Jadilah singkat, jelas, dan profesional

KEMAMPUAN:
- Kamu memiliki akses ke web_search tool untuk mencari data real-time
- Jika user meminta riset, info terkini, atau data terbaru, gunakan web_search tool
- Jangan pernah bilang kamu tidak bisa search - kamu BISA pakai web_search tool!
- Gunakan bahasa Indonesia untuk semua respons"""
    
    if mira_context:
        system_prompt += f"\n\n[KONTEKS DARI MEMORI]:\n{mira_context}"
    
    # 4. Detect if user wants real-time data (supports both English and Indonesian)
    # Always enable tools - let AI decide when to use them
    needs_tools = True  # Always provide tools, AI will decide when to use them
    
    # 5. Define Generator for Streaming with auto-fallback
    async def event_generator():
        full_response = ""
        tool_calls_detected = []  # Track any tool calls made during streaming
        
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
                    tools=tools if needs_tools else None,
                    tool_choice="auto" if needs_tools else None,
                    images=req.images if req.images else None
                ):
                    if chunk:
                        # Check if it's a structured SSE message (error/info/tool)
                        if chunk.startswith("data: "):
                            try:
                                data = json.loads(chunk[6:])
                                if data.get('type') == 'error':
                                    last_error = data.get('message', 'Unknown error')
                                    print(f"[AUTO-FALLBACK] Error from {model}: {last_error}")
                                    break  # try next model
                                elif data.get('type') == 'tool_call':
                                    # Capture tool calls for execution after streaming
                                    if 'data' in data:
                                        tool_calls_detected.extend(data['data'])
                                    yield chunk  # pass through
                                    continue
                            except:
                                pass
                            # pass other data: messages through (info, etc)
                            yield chunk
                        else:
                            # Plain text chunk — wrap in SSE format for frontend
                            full_response += chunk
                            # Properly escape the text for JSON encoding
                            yield f"data: {json.dumps({'type': 'text', 'text': chunk}, ensure_ascii=False)}\n\n"
                
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
                tool_name = tool_call.get('function', {}).get('name')
                
                # Execute tools (web_search, etc.)
                result = await ai_service.execute_tool_call(tool_call)
                yield f"data: {json.dumps({'type': 'tool_result', 'tool_call_id': tool_call.get('id'), 'result': result})}\n\n"
        
        # 5. Store in Mira after stream completion - Centralized
        if full_response:
            memory_manager.mira_store(f"User: {req.message}\nRohadi: {full_response}", room="nexus_central")
            
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/chat/grill")
async def grill_me_endpoint(req: ChatRequest):
    """
    Grill-Me: Rohadi menginterview user SATU PERTANYAAN per respons
    untuk mematangkan rencana/ide sebelum dieksekusi.
    
    This works like a Claude Skill - conversational, one question at a time.
    """
    GRILL_SYSTEM_PROMPT = """Kamu adalah Rohadi dalam mode GRILL-ME — Spesialis Arsitektur Coding & TOTAL GROWTH MARKETING (TGM).

CARA KERJA GRILL-ME:
- Interview user SATU PERTANYAAN per respons
- Selalu berikan rekomendasi untuk setiap pertanyaan
- Jangan tumpuk banyak pertanyaan sekaligus
- Gunakan framework TGM untuk struktur interview

STRUKTUR BERPIKIR TGM (Gunakan ini saat menginterview):
1. STRATEGIC: Understanding Market (Peluang), Value Creation (Solusi Unik), Brand Blueprint (Pesan & Fondasi).
2. TACTICAL: Awareness (Dampak), Acquisition (Efisiensi), Activation (Konversi), CRM (Retensi/LTV).
3. ENGINE: Skalabilitas, Profitabilitas, dan Keberlanjutan.

ATURAN GRILL-ME (WAJIB DIIKUTI):
1. Tanyakan HANYA SATU pertanyaan per respons secara tajam dan mendalam.
2. Setiap pertanyaan HARUS disertai REKOMENDASI berbasis framework TGM atau Best Practice Coding.
3. Fokus pada "Kenapa" (Strategi) sebelum "Bagaimana" (Taktis).
4. Jika konteksnya CODING: Fokus pada arsitektur, skalabilitas (Growth Engine), dan efisiensi logic.
5. Jika konteksnya MARKETING: Gunakan 7 pilar TGM (Market, Value, Brand, Awareness, Acquisition, Activation, CRM).
6. Temukan risiko, asumsi, dan edge case yang belum dipikirkan user.
7. Jangan eksekusi sampai user bilang "lanjut" atau "eksekusi".

FORMAT RESPONS:
🔍 **Pertanyaan [Fase TGM]:** [Satu pertanyaan tajam]

💡 **Rekomendasi Rohadi:** [Saran strategis/teknis kamu]

IDENTITAS:
- Nama kamu Rohadi.
- Gunakan bahasa Indonesia.
- Pengetahuan kamu tersimpan di Mira Memory (Episodic Memory)."""

    mira_context = memory_manager.mira_recall(req.message, room="nexus_central")
    system_prompt = GRILL_SYSTEM_PROMPT
    if mira_context:
        system_prompt += f"\n\n[KONTEKS DARI MEMORI]:\n{mira_context}"

    async def grill_generator():
        full_response = ""
        models_to_try = ai_service.get_fallback_chain(req.model)
        last_error = None

        for attempt_idx, model in enumerate(models_to_try):
            try:
                if attempt_idx > 0:
                    yield f"data: {json.dumps({'type': 'info', 'message': f'Switching to {model}...'})}\n\n"

                async for chunk in ai_service.call_ai_stream(
                    req.message,
                    history=req.history,
                    system_prompt=system_prompt,
                    model=model,
                ):
                    if chunk:
                        if chunk.startswith("data: "):
                            try:
                                data = json.loads(chunk[6:])
                                if data.get('type') == 'error':
                                    last_error = data.get('message', 'Unknown error')
                                    break
                            except:
                                pass
                            yield chunk
                        else:
                            full_response += chunk
                            yield f"data: {json.dumps({'type': 'text', 'text': chunk})}\n\n"

                if full_response.strip():
                    break
            except Exception as e:
                last_error = str(e)
                continue

        if not full_response.strip():
            yield f"data: {json.dumps({'type': 'error', 'message': last_error or 'All models failed'})}\n\n"

        if full_response:
            memory_manager.mira_store(f"[GRILL] User: {req.message}\nRohadi: {full_response}", room="nexus_central")

        yield "data: [DONE]\n\n"

    return StreamingResponse(grill_generator(), media_type="text/event-stream")


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    # 1. Recall from Mira (Episodic)
    mira_context = memory_manager.mira_recall(req.message, room="nexus_central")
    
    # 2. Build Enriched Prompt dengan identitas Rohadi
    system_prompt = """Kamu adalah Rohadi, asisten AI pribadi yang cerdas dan ramah.

ATURAN IDENTITAS (WAJIB, TIDAK BOLEH DILANGGAR):
- Nama kamu SELALU "Rohadi" — tidak pernah nama lain
- JANGAN PERNAH menyebut nama model AI (Gemma, Llama, Ling, GPT, Claude, dll)
- JANGAN PERNAH menyebut perusahaan pembuat (Google, Meta, Ant Group, OpenAI, dll)
- Jika ditanya "siapa kamu": jawab "Saya Rohadi, asisten AI pribadi kamu."
- Jika ditanya "siapa yang membuat kamu": jawab "Saya dibuat khusus untuk membantu kamu."
- Gunakan bahasa Indonesia secara default, kecuali pengguna menulis dalam bahasa lain
- Jadilah singkat, jelas, dan profesional"""
    if mira_context:
        system_prompt += f"\n\n[KONTEKS DARI MEMORI]:\n{mira_context}"
    
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
    """Chat endpoint with tool calling support including Grill-Me skill"""
    
    # Define available tools with REAL web search capabilities AND Grill-Me skill
    tools = [
        {
            "type": "function",
            "function": {
                "name": "grill_me",
                "description": "Interview user about their plan/design using TGM framework. Ask ONE question at a time with recommendations. Use when user mentions 'grill me' or wants to stress-test an idea.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_idea": {"type": "string", "description": "The user's initial idea or plan to grill"},
                        "conversation_stage": {"type": "string", "enum": ["initial", "follow_up", "final"], "description": "Stage of the interview"}
                    },
                    "required": ["user_idea"]
                }
            }
        },
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
        
        # SPECIAL CASE: If grill_mode is active, bypass AI and use Grill-Me skill directly
        if req.grill_mode:
            print(f"[GRILL-ME] Activated - Bypassing AI, using contextual reasoning engine")
            try:
                # Generate grill question using v2 contextual reasoning engine
                question_data = grill_me_skill.generate_grill_question(
                    user_input=req.message,
                    conversation_history=req.history,
                    session_id=req.session_id or "default"
                )
                formatted_response = grill_me_skill.format_response(question_data)
                
                # Stream the response
                yield f"data: {json.dumps({'type': 'text', 'text': formatted_response}, ensure_ascii=False)}\n\n"
                
                # === AUTO-STORAGE for Grill-Me mode ===
                try:
                    from logic.memory_manager import memory_manager
                    
                    # Store user input
                    user_data = {
                        "type": "grill_me_user",
                        "content": req.message,
                        "session_id": req.session_id or "default",
                        "mode": "grill_me",
                        "timestamp": datetime.now().isoformat()
                    }
                    memory_manager.mira_store(
                        content=json.dumps(user_data),
                        room=f"grill_{req.session_id or 'default'}"
                    )
                    
                    # Store AI question
                    ai_data = {
                        "type": "grill_me_question",
                        "content": formatted_response[:4500],
                        "session_id": req.session_id or "default",
                        "mode": "grill_me",
                        "phase": question_data.get('phase', 'unknown'),
                        "leverage": question_data.get('leverage', 'unknown'),
                        "timestamp": datetime.now().isoformat()
                    }
                    memory_manager.mira_store(
                        content=json.dumps(ai_data),
                        room=f"grill_{req.session_id or 'default'}"
                    )
                    
                    print(f"[MIRA] ✅ Stored Grill-Me conversation ({len(formatted_response)} chars)")
                except Exception as e:
                    print(f"[MIRA] ⚠️ Error storing Grill-Me: {e}")
                
                yield "data: [DONE]\n\n"
                return
            except Exception as e:
                print(f"[GRILL-ME] Error: {str(e)}")
                import traceback
                traceback.print_exc()
                yield f"data: {json.dumps({'type': 'error', 'message': f'Grill-Me error: {str(e)}'})}\n\n"
                yield "data: [DONE]\n\n"
                return
        
        # Normal mode: Use AI with optional tools
        # Detect if user wants real-time data (supports both English and Indonesian)
        needs_tools = any(keyword in req.message.lower() for keyword in [
            # English keywords
            'research', 'search', 'current', 'latest', 'today', 'real-time', 
            'template', 'seo', 'keyword', 'trend', 'news', 'people also ask',
            # Indonesian keywords
            'riset', 'cari', 'saat ini', 'terbaru', 'hari ini', 'real-time',
            'tren', 'berita', 'kondisi sekarang', 'data terbaru',
            'analisa', 'analisis', 'laporan', 'update', 'sekarang'
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
                    system_prompt="""Kamu adalah Rohadi, asisten AI pribadi yang cerdas dan ramah dengan akses ke pencarian web real-time.

ATURAN IDENTITAS (WAJIB DIIKUTI):
- Nama kamu SELALU "Rohadi" — tidak boleh menyebut nama lain
- Jangan pernah menyebut model AI, perusahaan pembuat, atau teknologi yang mendasarimu
- Jika ditanya "siapa kamu", jawab: "Saya Rohadi, asisten AI pribadimu."
- Gunakan bahasa Indonesia secara default

KEMAPUAN TOOLS:
- Gunakan web_search untuk data real-time, tren, berita terkini
- Gunakan get_people_also_ask untuk pertanyaan terkait
- Gunakan research_topic untuk riset mendalam
- SELALU gunakan data nyata dari tools, jangan mengarang informasi
- Sebutkan sumber saat menggunakan data real-time""",
                    model=model,
                    tools=tools if needs_tools else None,
                    tool_choice="auto" if needs_tools else None
                ):
                    if chunk:
                        # Check if it's a structured SSE message (error/info/tool)
                        if chunk.startswith("data: "):
                            try:
                                data = json.loads(chunk[6:])
                                if data.get('type') == 'error':
                                    last_error = data.get('message', 'Unknown error')
                                    print(f"[AUTO-FALLBACK] Error from {model}: {last_error}")
                                    break  # try next model
                                elif "tool_calls" in data:
                                    tool_calls_detected.extend(data["tool_calls"])
                                    yield f"data: {json.dumps({'type': 'tool_call', 'data': data['tool_calls']})}\n\n"
                                    continue
                            except:
                                pass
                            yield chunk  # pass info/other messages through
                        else:
                            # Plain text chunk — wrap in SSE format for frontend
                            full_response += chunk
                            # Properly escape the text for JSON encoding
                            yield f"data: {json.dumps({'type': 'text', 'text': chunk}, ensure_ascii=False)}\n\n"
                
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
                tool_name = tool_call.get('function', {}).get('name')
                
                # Execute tools (web_search, research_topic, etc.)
                result = await ai_service.execute_tool_call(tool_call)
                yield f"data: {json.dumps({'type': 'tool_result', 'tool_call_id': tool_call.get('id'), 'result': result})}\n\n"
        
        # === AUTO-STORAGE: Save conversation to Mira Context ===
        if full_response.strip() and req.session_id:
            try:
                from logic.memory_manager import memory_manager
                
                # Store user message
                user_data = {
                    "type": "user_message",
                    "content": req.message,
                    "session_id": req.session_id,
                    "model": req.model,
                    "timestamp": datetime.now().isoformat()
                }
                memory_manager.mira_store(
                    content=json.dumps(user_data),
                    room=f"session_{req.session_id}"
                )
                
                # Store AI response (truncate if too long for Mira)
                response_preview = full_response[:4500]  # Leave room for JSON overhead
                ai_data = {
                    "type": "ai_response",
                    "content": response_preview,
                    "session_id": req.session_id,
                    "model": req.model,
                    "timestamp": datetime.now().isoformat()
                }
                memory_manager.mira_store(
                    content=json.dumps(ai_data),
                    room=f"session_{req.session_id}"
                )
                
                print(f"[MIRA] ✅ Stored conversation from session {req.session_id} ({len(full_response)} chars)")
            except Exception as e:
                print(f"[MIRA] ⚠️ Error storing conversation: {e}")
        
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

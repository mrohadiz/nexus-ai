import os
import asyncio
import requests
import json
import time
from typing import Optional, List, Dict, Tuple

# ----- Free model cache (module-level, shared across requests) -----
_free_models_cache: List[str] = []
_free_models_fetched_at: float = 0.0
_FREE_MODELS_TTL = 600  # refresh every 10 minutes

class AIService:
    def __init__(self):
        self.provider = os.getenv("DEFAULT_AI_PROVIDER", "openrouter")
        
        # DuckAI Config
        self.duckai_url = os.getenv("DUCKAI_URL", "http://localhost:3000/v1/chat/completions")
        self.duckai_api_key = os.getenv("DUCKAI_API_KEY", "dummy-key")
        
        # OpenRouter Config
        self.openrouter_url = os.getenv("OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions")
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "")

        # Hardcoded reliable free fallbacks (used if API fetch fails)
        self._default_free_models = [
            "google/gemini-2.0-flash-001",
            "google/gemma-3-27b-it:free",
            "meta-llama/llama-3.1-8b-instruct:free",
            "mistralai/mistral-7b-instruct:free",
            "qwen/qwen-2.5-7b-instruct:free",
        ]

    def _get_config(self):
        if self.provider == "openrouter":
            return self.openrouter_url, self.openrouter_api_key
        else:
            return self.duckai_url, self.duckai_api_key

    def fetch_free_models(self) -> List[str]:
        """Fetch & cache the list of free models from OpenRouter API.
        Models are considered free if prompt pricing == '0' OR id ends with ':free'.
        Cache is refreshed every FREE_MODELS_TTL seconds.
        """
        global _free_models_cache, _free_models_fetched_at

        now = time.time()
        if _free_models_cache and (now - _free_models_fetched_at) < _FREE_MODELS_TTL:
            return _free_models_cache

        try:
            print("[FREE-ROUTER] Fetching free models from OpenRouter API...")
            resp = requests.get(
                "https://openrouter.ai/api/v1/models",
                headers={"Authorization": f"Bearer {self.openrouter_api_key}"},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json().get("data", [])
                free = []
                for m in data:
                    model_id = m.get("id", "")
                    prompt_price = str(m.get("pricing", {}).get("prompt", "1"))
                    completion_price = str(m.get("pricing", {}).get("completion", "1"))
                    ctx = m.get("context_length", 0)

                    is_free = (
                        model_id.endswith(":free") or
                        (prompt_price == "0" and completion_price == "0")
                    )
                    # Filter out experimental/low-quality models
                    is_usable = ctx >= 8192 and "ocr" not in model_id and "vision-ocr" not in model_id

                    if is_free and is_usable:
                        free.append(model_id)

                if free:
                    _free_models_cache = free
                    _free_models_fetched_at = now
                    print(f"[FREE-ROUTER] Found {len(free)} free models: {free[:5]}...")
                    return free
        except Exception as e:
            print(f"[FREE-ROUTER] Failed to fetch free models: {e}")

        # Fallback to defaults
        return self._default_free_models

    async def fetch_free_models_async(self) -> List[str]:
        """Async wrapper to fetch free models without blocking the event loop."""
        return await asyncio.to_thread(self.fetch_free_models)

    def get_fallback_chain(self, primary_model: str) -> List[str]:
        """Build fallback chain: [primary] + free_models (excluding primary)."""
        free = self.fetch_free_models()
        chain = [primary_model] + [m for m in free if m != primary_model]
        return chain


    async def call_ai_stream(self, prompt: str, history: List = [], system_prompt: str = "You are Nexus AI, a helpful personal assistant.", model: str = "openrouter/free", tools: Optional[List[Dict]] = None, tool_choice: Optional[str] = "auto", images: Optional[List[str]] = None):
        import httpx
        
        url, api_key = self._get_config()
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # If OpenRouter, add required headers
        if self.provider == "openrouter":
            headers["HTTP-Referer"] = "https://nexus-ai.local" # Required by OpenRouter
            headers["X-Title"] = "Nexus AI"
        
        # Build messages
        messages = []
        
        # System prompt handling
        if self.provider == "duckai":
            # DuckAI often dislikes 'system' role, so we merge it
            if history:
                for i, msg in enumerate(history):
                    role = msg.role if hasattr(msg, 'role') else msg.get('role')
                    content = msg.content if hasattr(msg, 'content') else msg.get('content')
                    
                    if i == 0 and role == "user":
                        messages.append({"role": "user", "content": f"{system_prompt}\n\n{content}"})
                    else:
                        messages.append({"role": role, "content": content})
                messages.append({"role": "user", "content": prompt})
            else:
                messages.append({"role": "user", "content": f"{system_prompt}\n\nUSER MESSAGE: {prompt}"})
        else:
            # OpenRouter / Standard OpenAI-like
            messages.append({"role": "system", "content": system_prompt})
            for msg in history:
                role = msg.role if hasattr(msg, 'role') else msg.get('role')
                content = msg.content if hasattr(msg, 'content') else msg.get('content')
                item = {"role": role, "content": content}
                
                # Support reasoning_details if present
                if hasattr(msg, 'reasoning_details'):
                    item["reasoning_details"] = getattr(msg, 'reasoning_details')
                elif isinstance(msg, dict) and "reasoning_details" in msg:
                    item["reasoning_details"] = msg["reasoning_details"]
                    
                messages.append(item)
            
            if images and len(images) > 0:
                content_parts = [{"type": "text", "text": prompt}]
                for img_url in images:
                    content_parts.append({
                        "type": "image_url",
                        "image_url": {"url": img_url}
                    })
                messages.append({"role": "user", "content": content_parts})
            else:
                messages.append({"role": "user", "content": prompt})
        
        # For OpenRouter, if model is simple like 'gpt-4o-mini', we might want to map it to full OpenRouter slug
        # but the user might be passing the full slug already.
        
        payload = {
            "model": model, 
            "messages": messages,
            "temperature": 0.7,
            "stream": True
        }
        
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = tool_choice
            
        # Enable reasoning for OpenRouter free models if requested or by default
        if self.provider == "openrouter":
            payload["reasoning"] = {"enabled": True}
        
        max_retries = 2
        for attempt in range(max_retries):
            try:
                print(f"[STREAM] {self.provider.upper()} Attempt {attempt + 1}/{max_retries} for model: {model}")
                async with httpx.AsyncClient(timeout=180.0) as client:
                    async with client.stream("POST", url, json=payload, headers=headers) as response:
                        if response.status_code != 200:
                            resp_text = await response.aread()
                            error_msg = f"Error: {response.status_code} - {resp_text.decode()}"
                            print(f"[STREAM ERROR] {error_msg}")
                            
                            detailed_error = f"AI Provider ({self.provider}) returned {response.status_code}. Try again or switch model."
                            yield f"data: {json.dumps({'type': 'error', 'message': detailed_error})}\n\n"
                            return
                        
                        async for line in response.aiter_lines():
                            if line.startswith("data: "):
                                data_str = line[6:].strip()
                                if data_str == "[DONE]":
                                    return
                                try:
                                    data = json.loads(data_str)
                                    if not data.get("choices"):
                                        continue
                                        
                                    choice = data["choices"][0]
                                    delta = choice.get("delta", {})
                                    
                                    if "tool_calls" in delta:
                                        yield f"data: {json.dumps({'type': 'tool_call', 'tool_calls': delta['tool_calls']})}\n\n"
                                        continue
                                    
                                    chunk = delta.get("content", "")
                                    if chunk:
                                        yield chunk
                                except Exception as e:
                                    continue
                return
                    
            except Exception as e:
                print(f"[STREAM ERROR] {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)
                    continue
                else:
                    yield f"data: {json.dumps({'type': 'error', 'message': f'Connection error: {str(e)}'})}\n\n"
                    return

    def call_ai(self, prompt: str, history: List = [], system_prompt: str = "You are Nexus AI, a helpful personal assistant.", model: str = "google/gemma-3-27b-it:free", tools: Optional[List[Dict]] = None, tool_choice: Optional[str] = "auto", images: Optional[List[str]] = None) -> Optional[str]:
        url, api_key = self._get_config()
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        if self.provider == "openrouter":
            headers["HTTP-Referer"] = "https://nexus-ai.local"
            headers["X-Title"] = "Nexus AI"
            
        messages = []
        if self.provider == "duckai":
            if history:
                for i, msg in enumerate(history):
                    role = msg.role if hasattr(msg, 'role') else msg.get('role')
                    content = msg.content if hasattr(msg, 'content') else msg.get('content')
                    if i == 0 and role == "user":
                        messages.append({"role": "user", "content": f"{system_prompt}\n\n{content}"})
                    else:
                        messages.append({"role": role, "content": content})
                messages.append({"role": "user", "content": prompt})
            else:
                messages.append({"role": "user", "content": f"{system_prompt}\n\nUSER MESSAGE: {prompt}"})
        else:
            messages.append({"role": "system", "content": system_prompt})
            for msg in history:
                role = msg.role if hasattr(msg, 'role') else msg.get('role')
                content = msg.content if hasattr(msg, 'content') else msg.get('content')
                item = {"role": role, "content": content}
                
                # Support reasoning_details if present
                if hasattr(msg, 'reasoning_details'):
                    item["reasoning_details"] = getattr(msg, 'reasoning_details')
                elif isinstance(msg, dict) and "reasoning_details" in msg:
                    item["reasoning_details"] = msg["reasoning_details"]
                    
                messages.append(item)
            
            if images and len(images) > 0:
                content_parts = [{"type": "text", "text": prompt}]
                for img_url in images:
                    content_parts.append({
                        "type": "image_url",
                        "image_url": {"url": img_url}
                    })
                messages.append({"role": "user", "content": content_parts})
            else:
                messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": model, 
            "messages": messages,
            "temperature": 0.7
        }
        
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = tool_choice
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=120)
            if response.status_code == 200:
                data = response.json()
                message = data['choices'][0]['message']
                if 'tool_calls' in message and message['tool_calls']:
                    return json.dumps({'tool_calls': message['tool_calls']})
                return message['content'].strip()
            else:
                print(f"{self.provider} Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"{self.provider} Call Failed: {e}")
        
        return None

    # Backward compatibility aliases
    def call_duckai(self, *args, **kwargs):
        return self.call_ai(*args, **kwargs)
        
    def call_duckai_stream(self, *args, **kwargs):
        return self.call_ai_stream(*args, **kwargs)

    async def execute_tool_call(self, tool_call: Dict) -> str:
        """Execute a tool call with REAL web search"""
        from tools.web_search_tool import web_search_tool
        
        tool_name = tool_call.get('function', {}).get('name', '')
        arguments = tool_call.get('function', {}).get('arguments', '{}')
        
        try:
            args = json.loads(arguments)
            if tool_name == 'web_search':
                query = args.get('query', '')
                num_results = args.get('num_results', 5)
                print(f"[TOOL] Executing real web search: {query}")
                result = await web_search_tool.search(query, num_results)
                if 'error' in result:
                    return json.dumps({"error": result['error']})
                formatted_results = []
                for i, res in enumerate(result.get('results', []), 1):
                    formatted_results.append(
                        f"{i}. {res.get('title', 'No title')}\n"
                        f"   URL: {res.get('url', 'N/A')}\n"
                        f"   Snippet: {res.get('snippet', 'N/A')}"
                    )
                return json.dumps({
                    "query": query,
                    "results": '\n\n'.join(formatted_results),
                    "total_results": result.get('results_count', 0),
                    "source": "DuckDuckGo (real-time)",
                    "timestamp": "live"
                })
            elif tool_name == 'research_topic':
                topic = args.get('topic', '')
                depth = args.get('depth', 'shallow')
                print(f"[TOOL] Conducting deep research: {topic}")
                search_result = await web_search_tool.search(topic, num_results=10 if depth == 'deep' else 5)
                if 'error' in search_result:
                    return json.dumps({"error": search_result['error']})
                detailed_content = []
                urls_to_fetch = search_result.get('results', [])[:3]
                for url_data in urls_to_fetch:
                    url = url_data.get('url', '')
                    if url:
                        content = await web_search_tool.fetch_url_content(url)
                        if 'error' not in content:
                            detailed_content.append({
                                "url": url,
                                "title": content.get('title', ''),
                                "content": content.get('content', '')[:500]
                            })
                paa = await web_search_tool.get_people_also_ask(topic)
                related = await web_search_tool.get_related_searches(topic)
                return json.dumps({
                    "topic": topic,
                    "search_results": search_result.get('results', [])[:5],
                    "detailed_content": detailed_content,
                    "people_also_ask": paa.get('questions', []),
                    "related_searches": related.get('related_searches', []),
                    "depth": depth,
                    "source": "Multiple real-time sources"
                })
            elif tool_name == 'fetch_url':
                url = args.get('url', '')
                print(f"[TOOL] Fetching URL content: {url}")
                result = await web_search_tool.fetch_url_content(url)
                return json.dumps(result)
            elif tool_name == 'get_people_also_ask':
                query = args.get('query', '')
                print(f"[TOOL] Getting PAA for: {query}")
                result = await web_search_tool.get_people_also_ask(query)
                return json.dumps(result)
            elif tool_name == 'get_related_searches':
                query = args.get('query', '')
                print(f"[TOOL] Getting related searches for: {query}")
                result = await web_search_tool.get_related_searches(query)
                return json.dumps(result)
            elif tool_name == 'calculate':
                expression = args.get('expression', '')
                try:
                    result = eval(expression, {"__builtins__": {}}, {})
                    return json.dumps({"result": result})
                except:
                    return json.dumps({"error": "Invalid expression"})
            elif tool_name == 'get_current_time':
                from datetime import datetime
                return json.dumps({"current_time": datetime.now().isoformat()})
            else:
                return json.dumps({"error": f"Unknown tool: {tool_name}"})
        except Exception as e:
            return json.dumps({"error": str(e)})

ai_service = AIService()

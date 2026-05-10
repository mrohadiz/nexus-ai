"""Real-time web search tool using DuckDuckGo and web scraping"""
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import json
import re


class WebSearchTool:
    """Fetch real-time data from the web"""
    
    def __init__(self):
        self.duckduckgo_url = "https://html.duckduckgo.com/html/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
    
    async def search(self, query: str, num_results: int = 5) -> Dict:
        """Search DuckDuckGo and return real results"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # DuckDuckGo HTML search
                response = await client.post(
                    self.duckduckgo_url,
                    data={"q": query},
                    headers=self.headers
                )
                
                if response.status_code != 200:
                    return {"error": f"Search failed with status {response.status_code}"}
                
                # Parse results
                soup = BeautifulSoup(response.text, 'html.parser')
                results = []
                
                for result in soup.find_all('a', class_='result__snippet', limit=num_results):
                    title_elem = result.find_parent('div', class_='result__body')
                    title = title_elem.find('a', class_='result__snippet').text if title_elem else ""
                    url = result.get('href', '')
                    snippet = result.text.strip()
                    
                    results.append({
                        "title": title,
                        "url": url,
                        "snippet": snippet
                    })
                
                return {
                    "query": query,
                    "results_count": len(results),
                    "results": results,
                    "timestamp": "real-time"
                }
        
        except Exception as e:
            return {"error": f"Search error: {str(e)}"}
    
    async def fetch_url_content(self, url: str) -> Dict:
        """Fetch and extract content from a URL"""
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                response = await client.get(url, headers=self.headers)
                
                if response.status_code != 200:
                    return {"error": f"Failed to fetch URL: {response.status_code}"}
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove unwanted elements
                for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                    element.decompose()
                
                # Extract main content
                title = soup.find('title')
                title_text = title.get_text() if title else ""
                
                # Try to find main article content
                main_content = soup.find('article') or soup.find('main') or soup.find('body')
                text_content = main_content.get_text(separator='\n', strip=True) if main_content else ""
                
                # Limit text length
                if len(text_content) > 3000:
                    text_content = text_content[:3000] + "..."
                
                # Extract meta description
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                description = meta_desc.get('content', '') if meta_desc else ""
                
                return {
                    "url": url,
                    "title": title_text,
                    "description": description,
                    "content": text_content[:2000],
                    "word_count": len(text_content.split())
                }
        
        except Exception as e:
            return {"error": f"Fetch error: {str(e)}"}
    
    async def get_people_also_ask(self, query: str) -> Dict:
        """Get 'People Also Ask' questions from Google (simulated via search)"""
        try:
            # Search for PAA questions
            paa_query = f"{query} questions"
            search_result = await self.search(paa_query, num_results=5)
            
            # Extract questions from snippets
            questions = []
            for result in search_result.get("results", []):
                snippet = result.get("snippet", "")
                # Look for question patterns
                question_matches = re.findall(r'[^.!?]*\?', snippet)
                questions.extend(question_matches[:2])
            
            return {
                "query": query,
                "questions": list(set(questions))[:5],  # Remove duplicates
                "source": "extracted from search results"
            }
        
        except Exception as e:
            return {"error": f"PAA extraction failed: {str(e)}"}
    
    async def get_related_searches(self, query: str) -> Dict:
        """Get related searches"""
        try:
            related_query = f"related: {query}"
            search_result = await self.search(related_query, num_results=5)
            
            # Extract related terms from titles and snippets
            related_terms = []
            for result in search_result.get("results", []):
                title = result.get("title", "")
                # Remove the original query to get related terms
                clean_title = title.replace(query, "").strip()
                if clean_title and len(clean_title) > 5:
                    related_terms.append(clean_title)
            
            return {
                "query": query,
                "related_searches": list(set(related_terms))[:8]
            }
        
        except Exception as e:
            return {"error": f"Related searches failed: {str(e)}"}


# Singleton instance
web_search_tool = WebSearchTool()

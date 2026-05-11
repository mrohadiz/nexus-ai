import os
import threading
import json
from typing import List, Optional
from logic import simple_memory

class MemoryManager:
    def __init__(self, data_path="./data/nexus_memory.db"):
        self.data_path = data_path
        simple_memory.init_db()

    def mira_recall(self, query: str, room: str = "general") -> str:
        """
        Recall episodic memory using Simple Memory (SQLite).
        Extremely fast, no heavy models.
        """
        try:
            return simple_memory.recall_memory(query, room=room)
        except Exception as e:
            print(f"[MEMORY] Recall error: {e}")
            return ""

    def _store_worker(self, content: str, room: str):
        """Worker thread to handle storage in background"""
        try:
            simple_memory.store_memory(content, room=room)
            print(f"[MEMORY] Successfully stored in room: {room}")
        except Exception as e:
            print(f"[MEMORY] Background store error: {e}")

    def mira_store(self, content: str, room: str = "general") -> bool:
        """
        Store episodic memory.
        Executed in a separate thread for maximum responsiveness.
        """
        if not content:
            return False
            
        # Clean content if it's a complex JSON string
        try:
            data = json.loads(content)
            if isinstance(data, dict) and 'content' in data:
                content = data['content']
        except:
            pass

        # Run storage in background thread
        thread = threading.Thread(target=self._store_worker, args=(content, room))
        thread.daemon = True
        thread.start()
        
        return True

memory_manager = MemoryManager()

import os
# import zvec  # Commented out due to Illegal Instruction on this CPU
import numpy as np
import subprocess
import json
from typing import List, Optional

class MemoryManager:
    def __init__(self, data_path="./data/memory_cache"):
        self.data_path = data_path
        os.makedirs(os.path.dirname(data_path), exist_ok=True)
        
        # Zvec is disabled due to instruction set incompatibility
        # We will use Postgres + Mira for now.

    def mira_recall(self, query: str, room: str = "general") -> str:
        """Recall episodic memory using Mira binary"""
        try:
            # We assume mira binary is in the same directory for now
            mira_path = "./mira"
            if not os.path.exists(mira_path):
                return ""
                
            cmd = [mira_path, "recall", query, "--room", room]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            print(f"Mira recall error: {e}")
        return ""

    def mira_store(self, content: str, room: str = "general") -> bool:
        """Store episodic memory using Mira binary"""
        try:
            # Skip storing if content is too long (prevents timeout)
            if len(content) > 5000:
                print(f"[MIRA] Skipping store - content too long ({len(content)} chars)")
                return False
                
            mira_path = "./mira"
            if not os.path.exists(mira_path):
                return False
                
            cmd = [mira_path, "verbatim", content, "--room", room]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            return result.returncode == 0
        except Exception as e:
            print(f"Mira store error: {e}")
        return False

    def store_local(self, content: str, vector: List[float]):
        """Store transient memory in Zvec"""
        # Logic to insert into zvec collection
        pass

memory_manager = MemoryManager()

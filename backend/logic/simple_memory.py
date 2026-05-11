"""
Simple Memory System for Nexus AI - Lightweight Alternative to MIRA
Uses SQLite for storage and keyword-based search (no heavy embeddings)
"""
import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

DB_PATH = "data/nexus_memory.db"

def init_db():
    """Initialize SQLite database for memory storage"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create tables
    c.execute('''
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room TEXT NOT NULL,
            content TEXT NOT NULL,
            memory_type TEXT DEFAULT 'fact',
            tags TEXT,  -- JSON array
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            accessed_count INTEGER DEFAULT 0
        )
    ''')
    
    # Create index for faster searches
    c.execute('CREATE INDEX IF NOT EXISTS idx_room ON memories(room)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_created ON memories(created_at)')
    
    conn.commit()
    conn.close()

def store_memory(content: str, room: str = "general", memory_type: str = "fact",
                 tags: List[str] = None):
    """Store a memory entry"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    tags_json = json.dumps(tags) if tags else json.dumps([])
    
    c.execute('''
        INSERT INTO memories (room, content, memory_type, tags)
        VALUES (?, ?, ?, ?)
    ''', (room, content, memory_type, tags_json))
    
    conn.commit()
    conn.close()
    print(f"💾 Memory stored in room: {room}")

def recall_memory(query: str, room: str = "general", budget: int = 3000,
                  limit: int = 5) -> str:
    """
    Recall memories using keyword-based search
    Returns formatted context string
    """
    if not query:
        return ""
        
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Build search terms from query (longer words only)
    search_terms = [t.lower() for t in query.split() if len(t) > 2]
    
    # Search with LIKE for each term
    conditions = []
    params = [room]
    
    for term in search_terms:
        conditions.append("content LIKE ?")
        params.append(f'%{term}%')
    
    where_clause = " OR ".join(conditions) if conditions else "1=1"
    
    query_sql = f'''
        SELECT * FROM memories
        WHERE room = ?
        AND ({where_clause})
        ORDER BY accessed_count DESC, created_at DESC
        LIMIT ?
    '''
    
    params.append(limit)
    c.execute(query_sql, params)
    rows = c.fetchall()
    
    # Format results
    if not rows:
        # Fallback: get last 2 messages from this room if no keyword match
        c.execute('SELECT * FROM memories WHERE room = ? ORDER BY created_at DESC LIMIT 2', (room,))
        rows = c.fetchall()
        if not rows:
            conn.close()
            return ""
    
    result_parts = []
    total_tokens = 0
    
    for row in rows:
        # Update access count
        c.execute('UPDATE memories SET accessed_count = accessed_count + 1 WHERE id = ?', 
                 (row['id'],))
        
        content = row['content']
        token_estimate = len(content) // 4  # Rough estimate
        
        if total_tokens + token_estimate > budget:
            break
            
        result_parts.append(f"[Memori {row['created_at']}]: {content}")
        total_tokens += token_estimate
    
    conn.commit()
    conn.close()
    
    return "\n\n".join(result_parts)

def list_memories(room: str = "general") -> List[Dict]:
    """List all memories in a room"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('''
        SELECT id, room, memory_type, tags, created_at, accessed_count
        FROM memories
        WHERE room = ?
        ORDER BY created_at DESC
    ''', (room,))
    
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows

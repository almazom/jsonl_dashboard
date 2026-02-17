# Card 22: Audit Logging

| Field | Value |
|-------|-------|
| **ID** | AN-22 |
| **Story Points** | 1 |
| **Depends On** | AN-20 |
| **Sprint** | Phase 3 |

## User Story

> As a system, I want to log all Cognitive Router interactions so that users can review chat history and model fallback chains.

## Context

- [requirements.md](../requirements.md) - Section 2.1 (cognitive_audit table)
- [Card 17](./17-cognitive-router.md) - CognitiveRouter Class

## Instructions

### Step 1: Create Audit Logger

```python
# src/nexus/router/audit_logger.py
import sqlite3
from datetime import datetime
from typing import Optional, List

class AuditLogger:
    """Logs Cognitive Router interactions to cognitive_audit table."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def log_query(
        self,
        session_ids: List[int],
        user_query: str,
        final_model: Optional[str] = None,
        chain_log: Optional[str] = None
    ) -> int:
        """
        Log a chat query to the database.
        
        Returns the ID of the inserted record.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO cognitive_audit 
            (session_ids, user_query, final_model, chain_log, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                ",".join(map(str, session_ids)),
                user_query,
                final_model,
                chain_log,
                datetime.now().isoformat()
            )
        )
        
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return record_id
    
    def get_history(
        self,
        session_id: Optional[int] = None,
        limit: int = 50
    ) -> List[dict]:
        """Get chat history, optionally filtered by session."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if session_id:
            cursor.execute(
                """
                SELECT * FROM cognitive_audit
                WHERE session_ids LIKE ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (f"%{session_id}%", limit)
            )
        else:
            cursor.execute(
                """
                SELECT * FROM cognitive_audit
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,)
            )
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
```

### Step 2: Integrate with Cognitive Router

```python
# src/nexus/router/cognitive_router.py
from .audit_logger import AuditLogger

class CognitiveRouter:
    """AI chat engine with fallback chain."""
    
    def __init__(self, db_path: str, chains_config: dict):
        self.db_path = db_path
        self.audit = AuditLogger(db_path)
        self.chains = chains_config
    
    async def query(
        self,
        sessions: list,
        user_query: str
    ) -> dict:
        """
        Query sessions with fallback chain.
        
        Returns answer and metadata.
        """
        session_ids = [s["id"] for s in sessions]
        chain_log = []
        final_model = None
        answer = None
        
        for model_config in self.chains["default"]:
            try:
                answer = await self._query_model(
                    model_config, sessions, user_query
                )
                final_model = model_config["name"]
                chain_log.append(f"{model_config['name']}: success")
                break
            except Exception as e:
                chain_log.append(f"{model_config['name']}: failed ({str(e)})")
        
        # Log to audit
        self.audit.log_query(
            session_ids=session_ids,
            user_query=user_query,
            final_model=final_model,
            chain_log=" → ".join(chain_log) if chain_log else None
        )
        
        return {
            "answer": answer,
            "final_model": final_model,
            "chain_log": chain_log
        }
```

### Step 3: Add Chat History Tab to Inspector

```python
# src/nexus/tui/inspector.py
class HistoryTab(Widget):
    """Shows chat history for selected session(s)."""
    
    def __init__(self, session_ids: list, db_path: str):
        super().__init__()
        self.session_ids = session_ids
        self.db_path = db_path
    
    def compose(self) -> ComposeResult:
        yield Static("Chat History", classes="tab-title")
        
        # Load history from audit
        audit = AuditLogger(self.db_path)
        history = audit.get_history(
            session_id=self.session_ids[0] if len(self.session_ids) == 1 else None
        )
        
        for entry in history:
            yield Static(
                f"Q: {entry['user_query']}\nA: via {entry['final_model']}",
                classes="history-entry"
            )
```

### Step 4: Write Unit Tests

```python
# tests/test_audit_logger.py
import pytest
from src.nexus.router.audit_logger import AuditLogger

def test_audit_log_query(tmp_path):
    db_path = str(tmp_path / "test.db")
    logger = AuditLogger(db_path)
    
    # Create table
    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE cognitive_audit (
            id INTEGER PRIMARY KEY,
            session_ids TEXT,
            user_query TEXT,
            final_model TEXT,
            chain_log TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()
    
    # Log query
    record_id = logger.log_query(
        session_ids=[1, 2, 3],
        user_query="What files were modified?",
        final_model="gemini-1.5-pro",
        chain_log="qwen: failed → gemini: success"
    )
    
    assert record_id > 0
    
    # Retrieve history
    history = logger.get_history(limit=10)
    assert len(history) == 1
    assert history[0]["user_query"] == "What files were modified?"
```

## Acceptance Criteria

- [ ] AuditLogger class implemented
- [ ] log_query() inserts records correctly
- [ ] get_history() retrieves records with optional session filter
- [ ] CognitiveRouter integrates audit logging
- [ ] chain_log format: "model1: failed → model2: success"
- [ ] Unit tests pass
- [ ] No SQL injection vulnerabilities (parameterized queries)

## Next Steps

After completing this card:
1. Update state.json: set card 22 to "completed"
2. All 22 cards complete!
3. Run full E2E test suite (manual-e2e-test.md)
4. Mark SDD as IMPLEMENTATION READY

# Card 03: DatabaseManager Class

| Field | Value |
|-------|-------|
| **ID** | AN-03 |
| **Story Points** | 3 |
| **Depends On** | AN-02 (Database Schema) |
| **Sprint** | Phase 1 |

## User Story

> As a developer, I want a DatabaseManager class that handles all SQLite operations so that other components can interact with the registry without writing SQL directly.

## Context

- [requirements.md](../requirements.md) - Section 2.1 (Database Schema)
- [02-database-schema.md](./02-database-schema.md) - Schema definition
- Referenced by: Cards 12, 13, 14, 21, 22

## Instructions

### Step 1: Create DatabaseManager Class

```python
# src/nexus/db/database_manager.py
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

class DatabaseManager:
    """SQLite database manager for Artifact Nexus registry."""
    
    def __init__(self, db_path: str):
        """Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None
        self._ensure_directory()
    
    def _ensure_directory(self) -> None:
        """Ensure database directory exists."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get or create database connection."""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
            # Enable foreign keys
            self._conn.execute("PRAGMA foreign_keys = ON")
        return self._conn
    
    def close(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
```

### Step 2: Implement Session CRUD Operations

```python
# src/nexus/db/database_manager.py (continued)

    def insert_session(self, session_data: Dict[str, Any]) -> int:
        """Insert a new session into the database.
        
        Args:
            session_data: Dict with keys: filepath, project_name, project_root,
                         agent_type, start_time, end_time, status, summary, title
        
        Returns:
            Inserted session ID
            
        Raises:
            sqlite3.IntegrityError: If filepath already exists
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                INSERT INTO sessions 
                (filepath, project_name, project_root, agent_type, 
                 start_time, end_time, status, summary, title, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_data["filepath"],
                    session_data["project_name"],
                    session_data["project_root"],
                    session_data["agent_type"],
                    session_data["start_time"],
                    session_data["end_time"],
                    session_data["status"],
                    session_data.get("summary", ""),
                    session_data["title"],
                    datetime.now().isoformat()
                )
            )
            conn.commit()
            return cursor.lastrowid
        
        except sqlite3.IntegrityError as e:
            # Session with this filepath already exists
            raise e
    
    def get_session(self, session_id: int) -> Optional[Dict[str, Any]]:
        """Get a single session by ID.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session dict or None if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM sessions WHERE id = ?",
            (session_id,)
        )
        row = cursor.fetchone()
        
        return dict(row) if row else None
    
    def get_sessions_by_ids(self, session_ids: List[int]) -> List[Dict[str, Any]]:
        """Get multiple sessions by their IDs.
        
        Args:
            session_ids: List of session IDs
            
        Returns:
            List of session dicts
        """
        if not session_ids:
            return []
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        placeholders = ",".join("?" * len(session_ids))
        cursor.execute(
            f"SELECT * FROM sessions WHERE id IN ({placeholders})",
            session_ids
        )
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_all_sessions(
        self,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Get all sessions with optional filters.
        
        Args:
            filters: Optional dict with keys:
                - time_range: "24h" | "3d" | "7d" | "custom"
                - start_date: datetime (for custom range)
                - end_date: datetime (for custom range)
                - agent_types: List[str] (e.g., ["codex", "qwen"])
                - statuses: List[str] (e.g., ["success", "failure"])
                - search_query: str (for fuzzy search)
        
        Returns:
            List of session dicts matching filters
        """
        from .filter_builder import FilterBuilder
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Build filter query
        builder = FilterBuilder(filters or {})
        query, params = builder.build_query()
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def update_session(
        self,
        session_id: int,
        data: Dict[str, Any]
    ) -> bool:
        """Update an existing session.
        
        Args:
            session_id: Session ID to update
            data: Dict of fields to update
            
        Returns:
            True if updated, False if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Build dynamic update query
        fields = []
        values = []
        for key, value in data.items():
            if key in ["filepath", "project_name", "project_root", "agent_type",
                       "start_time", "end_time", "status", "summary", "title"]:
                fields.append(f"{key} = ?")
                values.append(value)
        
        if not fields:
            return False
        
        values.append(session_id)
        query = f"UPDATE sessions SET {', '.join(fields)} WHERE id = ?"
        
        cursor.execute(query, values)
        conn.commit()
        
        return cursor.rowcount > 0
    
    def delete_session(self, session_id: int) -> bool:
        """Delete a session by ID.
        
        Args:
            session_id: Session ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "DELETE FROM sessions WHERE id = ?",
            (session_id,)
        )
        conn.commit()
        
        return cursor.rowcount > 0
    
    def session_exists(self, filepath: str) -> bool:
        """Check if a session with given filepath exists.
        
        Args:
            filepath: Absolute file path to check
            
        Returns:
            True if exists, False otherwise
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT 1 FROM sessions WHERE filepath = ? LIMIT 1",
            (filepath,)
        )
        return cursor.fetchone() is not None
```

### Step 3: Implement Audit Log Operations

```python
# src/nexus/db/database_manager.py (continued)

    def log_audit_query(
        self,
        session_ids: List[int],
        user_query: str,
        final_model: Optional[str] = None,
        chain_log: Optional[str] = None
    ) -> int:
        """Log a Cognitive Router query to audit table.
        
        Args:
            session_ids: List of session IDs that were queried
            user_query: The user's question
            final_model: Model that provided the answer
            chain_log: Fallback chain log (e.g., "qwen: failed → gemini: success")
            
        Returns:
            Inserted audit record ID
        """
        conn = self._get_connection()
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
        conn.commit()
        return cursor.lastrowid
    
    def get_audit_history(
        self,
        session_id: Optional[int] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get audit log history.
        
        Args:
            session_id: Optional session ID to filter by
            limit: Maximum number of records to return
            
        Returns:
            List of audit records
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if session_id:
            # Search for session_id in comma-separated list
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
        
        return [dict(row) for row in cursor.fetchall()]
```

### Step 4: Write Unit Tests

```python
# tests/test_database_manager.py
import pytest
import sqlite3
from pathlib import Path
from src.nexus.db.database_manager import DatabaseManager

@pytest.fixture
def db_manager(tmp_path):
    """Create test database manager."""
    db_path = str(tmp_path / "test.db")
    manager = DatabaseManager(db_path)
    
    # Create tables
    conn = manager._get_connection()
    conn.executescript("""
        CREATE TABLE sessions (
            id INTEGER PRIMARY KEY,
            filepath TEXT UNIQUE,
            project_name TEXT,
            project_root TEXT,
            agent_type TEXT,
            start_time TEXT,
            end_time TEXT,
            status TEXT,
            summary TEXT,
            title TEXT,
            created_at TEXT
        );
        CREATE TABLE cognitive_audit (
            id INTEGER PRIMARY KEY,
            session_ids TEXT,
            user_query TEXT,
            final_model TEXT,
            chain_log TEXT,
            created_at TEXT
        );
    """)
    conn.commit()
    
    yield manager
    manager.close()

def test_insert_and_get_session(db_manager):
    session_data = {
        "filepath": "/test/session.jsonl",
        "project_name": "test-project",
        "project_root": "/test",
        "agent_type": "codex",
        "start_time": "2026-02-17T10:00:00Z",
        "end_time": "2026-02-17T10:05:00Z",
        "status": "success",
        "title": "Test session",
        "summary": "[FIX] Test"
    }
    
    session_id = db_manager.insert_session(session_data)
    assert session_id > 0
    
    session = db_manager.get_session(session_id)
    assert session is not None
    assert session["filepath"] == "/test/session.jsonl"

def test_session_exists(db_manager):
    assert not db_manager.session_exists("/test/session.jsonl")
    
    session_data = {
        "filepath": "/test/session.jsonl",
        "project_name": "test",
        "project_root": "/test",
        "agent_type": "codex",
        "start_time": "2026-02-17T10:00:00Z",
        "end_time": "2026-02-17T10:05:00Z",
        "status": "success",
        "title": "Test"
    }
    db_manager.insert_session(session_data)
    
    assert db_manager.session_exists("/test/session.jsonl")

def test_get_sessions_by_ids(db_manager):
    # Insert test data
    for i in range(3):
        db_manager.insert_session({
            "filepath": f"/test/session{i}.jsonl",
            "project_name": "test",
            "project_root": "/test",
            "agent_type": "codex",
            "start_time": "2026-02-17T10:00:00Z",
            "end_time": "2026-02-17T10:05:00Z",
            "status": "success",
            "title": f"Test {i}"
        })
    
    sessions = db_manager.get_sessions_by_ids([1, 3])
    assert len(sessions) == 2

def test_log_audit(db_manager):
    audit_id = db_manager.log_audit_query(
        session_ids=[1, 2],
        user_query="What files were modified?",
        final_model="gemini-1.5-pro",
        chain_log="qwen: failed → gemini: success"
    )
    assert audit_id > 0
    
    history = db_manager.get_audit_history(limit=10)
    assert len(history) == 1
    assert history[0]["user_query"] == "What files were modified?"
```

## Acceptance Criteria

- [ ] DatabaseManager class with __init__(db_path)
- [ ] insert_session(session_data) -> int
- [ ] get_session(session_id) -> dict | None
- [ ] get_all_sessions(filters) -> list
- [ ] get_sessions_by_ids(ids) -> list
- [ ] update_session(session_id, data) -> bool
- [ ] delete_session(session_id) -> bool
- [ ] session_exists(filepath) -> bool
- [ ] log_audit_query(session_ids, query, model, chain_log) -> int
- [ ] get_audit_history(session_id, limit) -> list
- [ ] Connection management (context manager support)
- [ ] Error handling for SQLite operations
- [ ] Unit tests pass

## Next Steps

After completing this card:
1. Update state.json: set card 03 to "completed"
2. Update ssot_kanban.yaml: mark SDD-001 as done
3. Read next card: [04-static-layout.md](./04-static-layout.md)
4. Continue execution

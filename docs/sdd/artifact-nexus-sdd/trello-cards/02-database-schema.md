# Card 02: Database Schema Design

| Field | Value |
|-------|-------|
| **ID** | AN-02 |
| **Story Points** | 3 |
| **Depends On** | AN-01 |
| **Sprint** | Phase 1 |

## User Story

> As a developer, I want to design the SQLite schema so that session metadata can be efficiently stored and queried.

## Context

- [requirements.md](../requirements.md) - Section 2 (Data Model)
- [Card 01](./01-project-bootstrap.md) - Project Bootstrap

## Instructions

### Step 1: Create Schema SQL

```sql
-- src/nexus/db/schema.sql

-- Sessions table: stores metadata about agent sessions
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filepath TEXT NOT NULL UNIQUE,
    project_name TEXT NOT NULL,
    project_root TEXT NOT NULL,
    agent_type TEXT NOT NULL CHECK(agent_type IN ('codex', 'qwen', 'kimi', 'gemini', 'unknown')),
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('success', 'failure', 'interrupted')),
    summary TEXT,
    title TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast filtering
CREATE INDEX IF NOT EXISTS idx_sessions_project ON sessions(project_name);
CREATE INDEX IF NOT EXISTS idx_sessions_agent ON sessions(agent_type);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);
CREATE INDEX IF NOT EXISTS idx_sessions_start_time ON sessions(start_time);

-- Cognitive audit table: stores AI chat history
CREATE TABLE IF NOT EXISTS cognitive_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_ids TEXT NOT NULL,
    user_query TEXT NOT NULL,
    final_model TEXT,
    chain_log TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Index for audit lookups
CREATE INDEX IF NOT EXISTS idx_audit_created ON cognitive_audit(created_at);
```

### Step 2: Create Database Path Utility

```python
# src/nexus/db/config.py
import os
from pathlib import Path

def get_db_path() -> str:
    """Get path to SQLite database file."""
    nexus_dir = Path.home() / ".nexus"
    nexus_dir.mkdir(parents=True, exist_ok=True)
    return str(nexus_dir / "nexus.db")

def get_config_path() -> str:
    """Get path to config file."""
    return str(Path.home() / ".nexus" / "config.yaml")

def get_chains_path() -> str:
    """Get path to chains config."""
    return str(Path.home() / ".nexus" / "chains.yaml")
```

### Step 3: Create Schema Migration Script

```python
# src/nexus/db/migrate.py
import sqlite3
from pathlib import Path

def run_migrations(db_path: str) -> None:
    """Run database migrations."""
    conn = sqlite3.connect(db_path)
    
    # Read schema
    schema_path = Path(__file__).parent / "schema.sql"
    with open(schema_path) as f:
        schema = f.read()
    
    # Execute schema
    conn.executescript(schema)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    from .config import get_db_path
    run_migrations(get_db_path())
```

### Step 4: Verify Schema

```bash
cd /home/pets/temp/jsonl_dashboard

# Run migration
poetry run python -m nexus.db.migrate

# Verify tables created
sqlite3 ~/.nexus/nexus.db ".tables"

# Verify schema
sqlite3 ~/.nexus/nexus.db ".schema sessions"
sqlite3 ~/.nexus/nexus.db ".schema cognitive_audit"
```

## Acceptance Criteria

- [ ] schema.sql created with sessions and cognitive_audit tables
- [ ] All indexes created (project, agent, status, start_time)
- [ ] CHECK constraints on agent_type and status
- [ ] migrate.py script works
- [ ] Database file created at ~/.nexus/nexus.db
- [ ] Tables visible via `sqlite3 .tables`
- [ ] No SQL syntax errors

## Next Steps

After completing this card:
1. Update state.json: set card 02 to "completed"
2. Read next card: [03-database-manager.md](./03-database-manager.md)
3. Continue execution

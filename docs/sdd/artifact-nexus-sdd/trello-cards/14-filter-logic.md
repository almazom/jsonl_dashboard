# Card 14: Filter Logic (SQL)

| Field | Value |
|-------|-------|
| **ID** | AN-14 |
| **Story Points** | 2 |
| **Depends On** | AN-03 (DatabaseManager) |
| **Sprint** | Phase 2 |

## User Story

> As a system, I want to build SQL queries from filter parameters so that sessions can be efficiently filtered.

## Context

- [requirements.md](../requirements.md) - Section 4.1 (Filter Types)

## Instructions

### Step 1: Create FilterBuilder Class

```python
# src/nexus/db/filter_builder.py
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple

class FilterBuilder:
    """Builds SQL queries from filter parameters."""
    
    def __init__(self, filters: Dict[str, Any]):
        """Initialize filter builder.
        
        Args:
            filters: Dict with keys:
                - time_range: "24h" | "3d" | "7d" | "custom"
                - start_date: datetime (for custom)
                - end_date: datetime (for custom)
                - agent_types: List[str]
                - statuses: List[str]
                - search_query: str
        """
        self.filters = filters
    
    def build_query(self) -> Tuple[str, List[Any]]:
        """Build SQL query with filters.
        
        Returns:
            Tuple of (query_string, parameters)
        """
        base_query = "SELECT * FROM sessions WHERE 1=1"
        params = []
        
        # Time range filter
        time_clause, time_params = self._build_time_filter()
        if time_clause:
            base_query += f" AND {time_clause}"
            params.extend(time_params)
        
        # Agent type filter
        agent_clause, agent_params = self._build_agent_filter()
        if agent_clause:
            base_query += f" AND {agent_clause}"
            params.extend(agent_params)
        
        # Status filter
        status_clause, status_params = self._build_status_filter()
        if status_clause:
            base_query += f" AND {status_clause}"
            params.extend(status_params)
        
        # Add ordering
        base_query += " ORDER BY start_time DESC"
        
        return base_query, params
    
    def _build_time_filter(self) -> Tuple[str, List[Any]]:
        """Build time range filter clause."""
        time_range = self.filters.get("time_range")
        
        if not time_range or time_range == "all":
            return "", []
        
        if time_range == "24h":
            cutoff = datetime.now() - timedelta(hours=24)
            return "start_time >= ?", [cutoff.isoformat()]
        
        elif time_range == "3d":
            cutoff = datetime.now() - timedelta(days=3)
            return "start_time >= ?", [cutoff.isoformat()]
        
        elif time_range == "7d":
            cutoff = datetime.now() - timedelta(days=7)
            return "start_time >= ?", [cutoff.isoformat()]
        
        elif time_range == "custom":
            start = self.filters.get("start_date")
            end = self.filters.get("end_date")
            
            clause = ""
            params = []
            
            if start:
                clause += "start_time >= ?"
                params.append(start.isoformat())
            
            if end:
                if clause:
                    clause += " AND "
                clause += "start_time <= ?"
                params.append(end.isoformat())
            
            return clause, params
        
        return "", []
    
    def _build_agent_filter(self) -> Tuple[str, List[Any]]:
        """Build agent type filter clause."""
        agent_types = self.filters.get("agent_types")
        
        if not agent_types:
            return "", []
        
        # Filter out None values (unchecked agents)
        active_agents = [a for a in agent_types if a]
        
        if not active_agents:
            return "1=0", []  # No agents selected
        
        placeholders = ",".join("?" * len(active_agents))
        return f"agent_type IN ({placeholders})", active_agents
    
    def _build_status_filter(self) -> Tuple[str, List[Any]]:
        """Build status filter clause."""
        statuses = self.filters.get("statuses")
        
        if not statuses:
            return "", []
        
        # Filter out None values
        active_statuses = [s for s in statuses if s]
        
        if not active_statuses:
            return "1=0", []
        
        placeholders = ",".join("?" * len(active_statuses))
        return f"status IN ({placeholders})", active_statuses
```

### Step 2: Integrate with DatabaseManager

```python
# src/nexus/db/database_manager.py (update)
from .filter_builder import FilterBuilder

class DatabaseManager:
    """SQLite database manager."""
    
    def get_all_sessions(
        self,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Get all sessions with optional filters."""
        from .filter_builder import FilterBuilder
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Build filter query
        builder = FilterBuilder(filters or {})
        query, params = builder.build_query()
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
```

## Acceptance Criteria

- [ ] FilterBuilder class
- [ ] Time range filter (24h, 3d, 7d, custom)
- [ ] Agent type filter (IN clause)
- [ ] Status filter (IN clause)
- [ ] Filter combination (AND logic)
- [ ] Parameterized queries (no SQL injection)
- [ ] Performance index usage

## Next Steps

1. Update state.json: set card 14 to "completed"
2. Continue with Card 15 (Fuzzy Search)

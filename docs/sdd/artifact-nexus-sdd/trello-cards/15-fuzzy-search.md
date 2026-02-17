# Card 15: Fuzzy Search (rapidfuzz)

| Field | Value |
|-------|-------|
| **ID** | AN-15 |
| **Story Points** | 2 |
| **Depends On** | AN-14 (Filter Logic) |
| **Sprint** | Phase 2 |

## User Story

> As a user, I want fuzzy search across project names and session titles so that I can find sessions even with partial or misspelled queries.

## Context

- [requirements.md](../requirements.md) - Section 4.2 (Fuzzy Search)
- Library: rapidfuzz

## Instructions

### Step 1: Create FuzzySearch Class

```python
# src/nexus/search/fuzzy_search.py
from typing import List, Dict, Any, Tuple
from rapidfuzz import process, fuzz

class FuzzySearch:
    """Fuzzy search for sessions."""
    
    def __init__(self, threshold: int = 60):
        """Initialize fuzzy search.
        
        Args:
            threshold: Minimum match score (0-100, default 60)
        """
        self.threshold = threshold
    
    def search(
        self,
        query: str,
        sessions: List[Dict[str, Any]]
    ) -> List[Tuple[Dict[str, Any], int]]:
        """Search sessions with fuzzy matching.
        
        Args:
            query: Search query string
            sessions: List of session dicts to search
            
        Returns:
            List of (session, score) tuples sorted by score
        """
        if not query or not sessions:
            return []
        
        # Create searchable strings
        searchable = []
        for session in sessions:
            # Combine project_name and title for search
            project = session.get("project_name", "")
            title = session.get("title", "")
            summary = session.get("summary", "")
            
            search_text = f"{project} {title} {summary}".lower()
            searchable.append((session, search_text))
        
        # Perform fuzzy matching
        results = []
        for session, text in searchable:
            # Use partial ratio for substring matching
            score = fuzz.partial_ratio(query.lower(), text)
            
            if score >= self.threshold:
                results.append((session, score))
        
        # Sort by score descending
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results
    
    def search_with_highlights(
        self,
        query: str,
        sessions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Search and add highlight information.
        
        Args:
            query: Search query string
            sessions: List of session dicts
            
        Returns:
            List of session dicts with _score and _match fields
        """
        results = self.search(query, sessions)
        
        enhanced = []
        for session, score in results:
            # Create copy with metadata
            enhanced_session = session.copy()
            enhanced_session["_score"] = score
            enhanced_session["_match"] = self._find_match_location(query, session)
            enhanced.append(enhanced_session)
        
        return enhanced
    
    def _find_match_location(
        self,
        query: str,
        session: Dict[str, Any]
    ) -> str:
        """Find where the match occurred.
        
        Returns:
            Field name where match was found
        """
        query_lower = query.lower()
        
        if query_lower in session.get("project_name", "").lower():
            return "project_name"
        elif query_lower in session.get("title", "").lower():
            return "title"
        elif query_lower in session.get("summary", "").lower():
            return "summary"
        else:
            return "combined"
```

### Step 2: Integrate with FilterPane

```python
# src/nexus/tui/filter_pane.py (update)
from ..search.fuzzy_search import FuzzySearch

class FilterPane(Widget):
    """Left pane filter controls."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fuzzy_search = FuzzySearch(threshold=60)
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        self.search_query = event.value
        
        if self.search_query:
            # Apply fuzzy search
            self._apply_fuzzy_search()
        else:
            # Clear search
            self._emit_filter_changed()
    
    def _apply_fuzzy_search(self) -> None:
        """Apply fuzzy search to current sessions."""
        # Get current sessions from screen
        screen = self.screen
        if hasattr(screen, "apply_fuzzy_search"):
            screen.apply_fuzzy_search(self.search_query)
```

### Step 3: Add Configuration

```yaml
# ~/.nexus/config.yaml
search:
  fuzzy_threshold: 60  # 0-100, higher = stricter matching
  search_fields:
    - project_name
    - title
    - summary
```

## Acceptance Criteria

- [ ] FuzzySearch class
- [ ] rapidfuzz.process.extract() usage
- [ ] Configurable threshold (default 60%)
- [ ] Search scope: project_name + title + summary
- [ ] Result ranking by score
- [ ] Performance optimization for large datasets

## Next Steps

1. Update state.json: set card 15 to "completed"
2. Update ssot_kanban.yaml: mark SDD-009 through SDD-015 as done
3. Continue with Card 16 (chains.yaml Parser)

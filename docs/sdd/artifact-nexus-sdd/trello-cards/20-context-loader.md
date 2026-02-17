# Card 20: Context Loader

| Field | Value |
|-------|-------|
| **ID** | AN-20 |
| **Story Points** | 2 |
| **Depends On** | AN-17 (CognitiveRouter) |
| **Sprint** | Phase 3 |

## User Story

> As a system, I want to load session content with smart token management so that context fits within model limits.

## Context

- [requirements.md](../requirements.md) - Section 5.3 (Context Strategy)

## Instructions

### Step 1: Create ContextLoader Class

```python
# src/nexus/router/context_loader.py
from typing import List, Dict, Any, Tuple
from pathlib import Path

class ContextLoader:
    """Loads and manages session context for AI queries."""
    
    def __init__(self, default_limit: int = 100000):
        """Initialize context loader.
        
        Args:
            default_limit: Default token limit
        """
        self.default_limit = default_limit
    
    def load_context(
        self,
        sessions: List[Dict[str, Any]],
        model_limit: int = None
    ) -> Tuple[str, bool]:
        """Load context from sessions.
        
        Args:
            sessions: List of session dicts
            model_limit: Model's context window limit
            
        Returns:
            Tuple of (context_string, was_truncated)
        """
        limit = model_limit or self.default_limit
        
        # Load full content from all sessions
        full_content = self._load_full_content(sessions)
        
        # Count tokens (estimate)
        token_count = self._count_tokens(full_content)
        
        if token_count <= limit:
            # Full content fits
            return full_content, False
        
        # Truncate using Heads & Tails strategy
        truncated = self._heads_and_tails(sessions, limit)
        return truncated, True
    
    def _load_full_content(self, sessions: List[Dict[str, Any]]) -> str:
        """Load full content from all sessions.
        
        Args:
            sessions: List of session dicts
            
        Returns:
            Combined content string
        """
        parts = []
        
        for session in sessions:
            filepath = session.get("filepath")
            if not filepath:
                continue
            
            content = self._load_session_file(filepath)
            if content:
                header = f"=== Session: {session.get('title', 'Untitled')} ==="
                parts.append(f"{header}\n{content}")
        
        return "\n\n".join(parts)
    
    def _load_session_file(self, filepath: str) -> str:
        """Load session content from file.
        
        Args:
            filepath: Path to session file
            
        Returns:
            Session content or empty string
        """
        try:
            path = Path(filepath)
            
            if path.suffix == ".jsonl":
                return self._load_jsonl(path)
            elif path.suffix == ".json":
                return self._load_json(path)
            else:
                return ""
        
        except Exception:
            return ""
    
    def _load_jsonl(self, path: Path) -> str:
        """Load JSONL session file.
        
        Args:
            path: Path to JSONL file
            
        Returns:
            Extracted conversations
        """
        import json
        
        conversations = []
        
        with open(path) as f:
            for line in f:
                try:
                    event = json.loads(line)
                    
                    # Extract based on event type
                    if event.get("type") == "response_item":
                        role = event.get("payload", {}).get("role")
                        content = event.get("payload", {}).get("content", [])
                        
                        if content and isinstance(content, list):
                            text = content[0].get("text", "")
                            if text:
                                conversations.append(f"{role}: {text}")
                    
                    elif event.get("role") in ["user", "assistant"]:
                        content = event.get("content", "")
                        if content:
                            conversations.append(f"{event['role']}: {content}")
                
                except:
                    continue
        
        return "\n".join(conversations)
    
    def _load_json(self, path: Path) -> str:
        """Load JSON session file (Gemini).
        
        Args:
            path: Path to JSON file
            
        Returns:
            Extracted conversations
        """
        import json
        
        try:
            with open(path) as f:
                data = json.load(f)
            
            conversations = []
            messages = data.get("messages", [])
            
            for msg in messages:
                msg_type = msg.get("type", "")
                content = msg.get("content", "")
                
                if msg_type in ["user", "gemini"] and content:
                    conversations.append(f"{msg_type}: {content}")
            
            return "\n".join(conversations)
        
        except:
            return ""
    
    def _heads_and_tails(
        self,
        sessions: List[Dict[str, Any]],
        limit: int
    ) -> str:
        """Load Heads & Tails (first 2 + last 2 interactions).
        
        Args:
            sessions: List of session dicts
            limit: Token limit
            
        Returns:
            Truncated context string
        """
        parts = []
        
        for session in sessions:
            filepath = session.get("filepath")
            if not filepath:
                continue
            
            content = self._extract_heads_tails(filepath, limit // len(sessions))
            if content:
                header = f"=== Session: {session.get('title', 'Untitled')} (truncated) ==="
                parts.append(f"{header}\n{content}")
        
        return "\n\n".join(parts)
    
    def _extract_heads_tails(self, filepath: str, per_session_limit: int) -> str:
        """Extract first 2 and last 2 interactions.
        
        Args:
            filepath: Path to session file
            per_session_limit: Token limit per session
            
        Returns:
            Heads & Tails content
        """
        path = Path(filepath)
        
        if path.suffix == ".jsonl":
            return self._extract_heads_tails_jsonl(path, per_session_limit)
        elif path.suffix == ".json":
            return self._extract_heads_tails_json(path, per_session_limit)
        
        return ""
    
    def _extract_heads_tails_jsonl(self, path: Path, limit: int) -> str:
        """Extract heads & tails from JSONL.
        
        Args:
            path: Path to JSONL file
            limit: Token limit
            
        Returns:
            First 2 + last 2 interactions
        """
        import json
        
        interactions = []
        
        with open(path) as f:
            for line in f:
                try:
                    event = json.loads(line)
                    if event.get("type") == "response_item":
                        role = event.get("payload", {}).get("role")
                        content = event.get("payload", {}).get("content", [])
                        
                        if content and isinstance(content, list):
                            text = content[0].get("text", "")
                            if text:
                                interactions.append(f"{role}: {text}")
                
                except:
                    continue
        
        # Take first 2 and last 2
        heads = interactions[:2]
        tails = interactions[-2:] if len(interactions) > 4 else []
        
        result = heads + ["... (truncated) ..."] + tails
        return "\n".join(result)
    
    def _extract_heads_tails_json(self, path: Path, limit: int) -> str:
        """Extract heads & tails from JSON.
        
        Args:
            path: Path to JSON file
            limit: Token limit
            
        Returns:
            First 2 + last 2 interactions
        """
        import json
        
        try:
            with open(path) as f:
                data = json.load(f)
            
            messages = data.get("messages", [])
            interactions = []
            
            for msg in messages:
                msg_type = msg.get("type", "")
                content = msg.get("content", "")
                
                if msg_type in ["user", "gemini"] and content:
                    interactions.append(f"{msg_type}: {content}")
            
            # Take first 2 and last 2
            heads = interactions[:2]
            tails = interactions[-2:] if len(interactions) > 4 else []
            
            result = heads + ["... (truncated) ..."] + tails
            return "\n".join(result)
        
        except:
            return ""
    
    def _count_tokens(self, text: str) -> int:
        """Estimate token count.
        
        Args:
            text: Text to count
            
        Returns:
            Estimated token count
        """
        # Rough estimate: 4 characters ≈ 1 token
        return len(text) // 4
```

## Acceptance Criteria

- [ ] ContextLoader class
- [ ] Token counting algorithm
- [ ] Full load if tokens < limit
- [ ] Heads&Tails (first 2 + last 2) if tokens > limit
- [ ] Per-model context window limits
- [ ] Multi-session token distribution
- [ ] JSONL and JSON format support

## Next Steps

1. Update state.json: set card 20 to "completed"
2. Update ssot_kanban.yaml: mark all Phase 3 cards done
3. SDD package now 100% complete!
